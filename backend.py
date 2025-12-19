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
import sqlite3
import numpy as np
import json
from typing import List
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_BASE_URL = "http://localhost:5000"
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    print("❌ ERROR: GOOGLE_API_KEY missing.", file=sys.stderr)
    sys.exit(1)

# Initialize GenAI Client for Embeddings
client = Client(api_key=GOOGLE_API_KEY)

# --- 1. RAG / Knowledge Base Implementation (SQLite + Vector Search) ---


class KnowledgeBaseService:
    def __init__(self, db_path="rag_knowledge.db"):
        self.db_path = db_path
        self.init_db()
        # Only populate if empty to avoid duplicates on restart
        if self.is_db_empty():
            print("Populating Knowledge Base with Mock Data...")
            self.populate_mock_data()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Table to store text chunks and their vector embeddings (stored as JSON string)
        c.execute('''CREATE TABLE IF NOT EXISTS documents
                     (id INTEGER PRIMARY KEY, content TEXT, embedding TEXT)''')
        conn.commit()
        conn.close()

    def is_db_empty(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM documents")
        count = c.fetchone()[0]
        conn.close()
        return count == 0

    def get_embedding(self, text: str) -> List[float]:
        """Generates embedding using Google GenAI."""
        try:
            # Using the standard gecko text embedding model
            result = client.models.embed_content(
                model="text-embedding-004",
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            print(f"Embedding Error: {e}")
            return []

    def add_document(self, text: str):
        embedding = self.get_embedding(text)
        if embedding:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO documents (content, embedding) VALUES (?, ?)",
                      (text, json.dumps(embedding)))
            conn.commit()
            conn.close()

    def search(self, query: str, top_k=2) -> str:
        """Vector search using Cosine Similarity."""
        query_embedding = self.get_embedding(query)
        if not query_embedding:
            return "Sorry, I couldn't process the search query."

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT content, embedding FROM documents")
        rows = c.fetchall()
        conn.close()

        results = []
        q_vec = np.array(query_embedding)
        norm_q = np.linalg.norm(q_vec)

        for content, emb_json in rows:
            doc_vec = np.array(json.loads(emb_json))
            norm_doc = np.linalg.norm(doc_vec)
            # Cosine Similarity: (A . B) / (||A|| * ||B||)
            score = np.dot(q_vec, doc_vec) / (norm_q * norm_doc)
            results.append((score, content))

        # Sort by score desc and take top_k
        results.sort(key=lambda x: x[0], reverse=True)
        top_results = [r[1] for r in results[:top_k]]

        return "\n\n".join(top_results)

    def populate_mock_data(self):
        """Injects the Mock Answers into the vector DB."""
        mock_data = [
            # Account & Onboarding
            "To open a OneCard account, download the app from Play Store/App Store. You need a PAN card and Aadhaar linked to your phone number. Verification usually takes 5-10 minutes instantly, but can take up to 24 hours.",
            "Eligibility criteria: Resident Indian, Age 21-60 years, Stable income (Salaried or Self-employed). Credit score of 750+ is preferred.",

            # Delivery
            "After approval, the physical metal card is dispatched within 2 working days via BlueDart/Delhivery. Delivery takes 5-7 business days.",
            "Delivery address is strictly the one mentioned on your KYC (Aadhaar). We cannot deliver to office addresses or allow store pickups for security reasons.",
            "You can track your card delivery status in the App under 'My Card' > 'Track Delivery'.",

            # Transactions
            "To make a transaction, use your physical card for POS or copy card details from the App for online payments. All transactions appear in the 'Activity' tab.",
            "If a transaction is declined, check if you have enabled 'Online/International' usage in App Settings. Also check your available credit limit.",
            "To dispute a transaction, click on the specific transaction in the App -> Select 'Report an Issue' -> Choose 'Dispute'.",

            # EMI
            "You can convert purchases above ₹2,500 into EMI. Go to the transaction -> Tap 'Convert to EMI'.",
            "EMI Interest rates vary between 13% to 16% p.a. based on tenure. Terms available: 3, 6, 9, 12 months.",
            "Foreclosure (Prepayment) of EMI is allowed after the 1st month with a 1% foreclosure fee + GST.",

            # Bill & Statement
            "Your bill is generated on the 1st of every month. The Due Date is usually the 18th or 20th. Check the App dashboard for the exact date.",
            "To download your statement: Go to Profile -> 'Statements' -> Select Month -> 'Download PDF'. Password is your DOB (DDMMYYYY).",
            "Bill charges include: GST on fees, Interest on revolving credit (if full amount not paid), and late payment fees if applicable."
        ]

        for text in mock_data:
            self.add_document(text)


# Initialize the RAG Service
rag_service = KnowledgeBaseService()

# --- Existing Mock Tools ---


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
    """Blocks (permanent) or Freezes (temporary) a card."""
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
    """Pays the credit card bill."""
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

# --- NEW TOOL: The Information Agent ---


def ask_knowledge_base_tool(query: str) -> str:
    """
    Use this tool for GENERAL questions about policies, how-to guides, rules, 
    eligibility, delivery times, or standard procedures.

    Do NOT use this for checking a specific user's balance or status.
    """
    print(f"DEBUG: Searching Knowledge Base for: {query}")
    return rag_service.search(query)


# --- System Instruction  ---
system_prompt = """
You are the **OneCard AI Assistant**. You help users manage their credit cards.

### OPERATIONAL GUIDELINES:
1. **Distinguish Query Types:**
   - **General/How-To/Policy:** Use `ask_knowledge_base_tool`. (e.g., "How do I apply?", "What are EMI rates?", "Where is my card?").
   - **Specific User Action:** Use specific API tools (e.g., "Block my card", "Pay my bill", "Convert last txn to EMI").
   
2. **Mandatory ID Check:** For ANY account-specific query (Balance, Bill, Block Card), you MUST ask for the `customer_id` first. Do NOT ask for ID if the user just asks a general question like "How to apply?".

3. **Safety & Confirmations:**
   - **Money Movement:** Before calling `make_payment_tool` or `convert_emi_tool`, explicitly confirm the amount and details.
   - **Blocking:** Verify if they want 'Freeze' (temporary) or 'Block' (Permanent).

4. **Collections Empathy:** If `check_risk_status_tool` returns "CRITICAL", adopt a supportive, calm tone.

### TOOL USAGE RULES:
- `ask_knowledge_base_tool`: Use for "How long does delivery take?", "Can I prepay EMI?", "How to dispute?".
- `open_account_tool`: Only for actually initiating a new application.
"""

# --- Agent & Runner Setup ---

agent = Agent(
    name="OneCardGenAI",
    model="gemini-2.5-flash-lite",
    instruction=system_prompt,
    tools=[
        # Informational Tool
        ask_knowledge_base_tool,
        # Action Tools
        open_account_tool, get_account_details_tool, track_card_tool,
        block_freeze_card_tool, get_bill_tool, make_payment_tool,
        get_transactions_tool, convert_emi_tool, report_dispute_tool,
        check_risk_status_tool
    ]
)

app = FastAPI(debug=True)
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
    # backend runs on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
