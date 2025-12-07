from google.genai import types, Client
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_BASE_URL = "http://localhost:5000"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_API_KEY missing.", file=sys.stderr)
    sys.exit(1)

# --- Tool Definitions (Connecting Agent to Mock API) ---


def open_account_tool(name: str, phone: str) -> dict:
    """Opens a new credit card account for a user."""
    try:
        resp = requests.post(f"{API_BASE_URL}/account/open",
                             json={"name": name, "phone": phone})
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def get_account_details_tool(customer_id: str) -> dict:
    """Gets balance, credit limit, and reward points."""
    try:
        return requests.get(f"{API_BASE_URL}/account/details/{customer_id}").json()
    except Exception as e:
        return {"error": str(e)}


def track_card_tool(customer_id: str) -> dict:
    """Checks physical card delivery status and ETA."""
    try:
        return requests.get(f"{API_BASE_URL}/card/track/{customer_id}").json()
    except Exception as e:
        return {"error": str(e)}


def block_freeze_card_tool(customer_id: str, action: str) -> dict:
    """
    Blocks or Freezes a card. 
    Action must be 'block' (permanent) or 'freeze' (temporary).
    """
    try:
        return requests.post(f"{API_BASE_URL}/card/control/{customer_id}", json={"action": action}).json()
    except Exception as e:
        return {"error": str(e)}


def get_bill_tool(customer_id: str) -> dict:
    """Gets total outstanding, minimum due, and due date."""
    try:
        return requests.get(f"{API_BASE_URL}/bill/summary/{customer_id}").json()
    except Exception as e:
        return {"error": str(e)}


def make_payment_tool(customer_id: str, amount: float) -> dict:
    """Pays the credit card bill. Method defaults to 'UPI' internally."""
    try:
        return requests.post(f"{API_BASE_URL}/payment/pay/{customer_id}", json={"amount": amount, "method": "UPI"}).json()
    except Exception as e:
        return {"error": str(e)}


def get_transactions_tool(customer_id: str) -> dict:
    """Fetches recent 5 transactions."""
    try:
        return requests.get(f"{API_BASE_URL}/transactions/list/{customer_id}").json()
    except Exception as e:
        return {"error": str(e)}


def convert_emi_tool(txn_id: str, months: int) -> dict:
    """Converts a high-value transaction into EMI."""
    try:
        return requests.post(f"{API_BASE_URL}/transactions/convert_emi", json={"txn_id": txn_id, "tenure_months": months}).json()
    except Exception as e:
        return {"error": str(e)}


def report_dispute_tool(txn_id: str, reason: str) -> dict:
    """Flags a transaction as fraudulent or incorrect."""
    try:
        return requests.post(f"{API_BASE_URL}/transactions/dispute", json={"txn_id": txn_id, "reason": reason}).json()
    except Exception as e:
        return {"error": str(e)}


def check_risk_status_tool(customer_id: str) -> dict:
    """Checks if the user is in the collections/high-risk bucket."""
    try:
        return requests.get(f"{API_BASE_URL}/collections/check/{customer_id}").json()
    except Exception as e:
        return {"error": str(e)}

# --- System Instruction  ---


system_prompt = """
You are the **OneCard AI Assistant**. You help users manage their credit cards.

### OPERATIONAL GUIDELINES:
1.  **Mandatory ID Check:** For ANY account-specific query (Balance, Bill, Block Card), you MUST ask for the `customer_id` first.
2.  **Safety & Confirmations:**
    * **Money Movement:** Before calling `make_payment_tool` or `convert_emi_tool`, explicitly confirm the amount and details with the user.
    * **Blocking:** If a user says "Block card", ask if they want to 'Freeze' (temporary) or 'Block' (Permanent/Lost) before calling `block_freeze_card_tool`.
3.  **Collections Empathy:** If `check_risk_status_tool` returns "CRITICAL" or mentions agents, adopt a supportive, calm tone. Do not threaten the user. Offer to take a payment.
4.  **Formatting:** Use bullet points for lists (like transactions). Keep answers concise.

### TOOL USAGE:
* Use `open_account_tool` only for new users.
* Use `report_dispute_tool` if a user claims a charge is wrong.
"""

# --- Agent & Runner Setup ---

agent = Agent(
    name="OneCardGenAI",
    model="gemini-2.5-flash-lite",  # Or 'gemini-1.5-pro' based on availability
    instruction=system_prompt,
    tools=[
        open_account_tool, get_account_details_tool, track_card_tool,
        block_freeze_card_tool, get_bill_tool, make_payment_tool,
        get_transactions_tool, convert_emi_tool, report_dispute_tool,
        check_risk_status_tool
    ]
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
session_service = InMemorySessionService()


class ChatRequest(BaseModel):
    user_id: str
    query: str


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id

    # Session Management
    sessions = await session_service.list_sessions(app_name="OneCardApp", user_id=user_id)
    if sessions.sessions:
        session_id = sessions.sessions[0].id
    else:
        sess = await session_service.create_session(app_name="OneCardApp", user_id=user_id)
        session_id = sess.id

    runner = Runner(agent=agent, app_name="OneCardApp",
                    session_service=session_service)

    user_msg = types.Content(
        role="user", parts=[types.Part(text=request.query)])

    final_text = ""
    async for event in runner.run_async(session_id=session_id, user_id=user_id, new_message=user_msg):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_text += part.text

    return {"response": final_text, "session_id": session_id}

if __name__ == "__main__":
    import uvicorn
    # backend runs on port 8000, mock_api runs on 5000
    uvicorn.run(app, host="0.0.0.0", port=8000)
