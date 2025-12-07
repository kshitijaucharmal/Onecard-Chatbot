import os
import requests
from typing import Optional

# Import ADK components
from google.adk.agents import Agent
from google.adk.model import Model 

# --- Configuration ---
# os.environ["GOOGLE_API_KEY"] = "YOUR_KEY"
API_BASE_URL = "http://localhost:8000"

# --- 1. Tool Definitions (Bridge to your API) ---

def open_account(name: str, phone: str) -> dict:
    """
    Opens a new credit card account for a customer.
    Args:
        name: The full name of the customer.
        phone: A valid phone number.
    """
    try:
        response = requests.post(f"{API_BASE_URL}/account/open", json={"name": name, "phone": phone})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_account_status(customer_id: str) -> dict:
    """Retrieves the verification status of a customer account."""
    try:
        response = requests.get(f"{API_BASE_URL}/account/status/{customer_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_card_delivery(customer_id: str) -> dict:
    """Checks the delivery status and tracking ETA of the physical card."""
    try:
        response = requests.get(f"{API_BASE_URL}/card/status/{customer_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_current_bill(customer_id: str) -> dict:
    """Fetches the current billing details including total due and due date."""
    try:
        response = requests.get(f"{API_BASE_URL}/bill/{customer_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def make_payment(customer_id: str, amount: float, method: str) -> dict:
    """
    Initiates a payment.
    Args:
        customer_id: The unique ID.
        amount: Amount to pay.
        method: 'UPI', 'Card', or 'Netbanking'.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/payment/initiate/{customer_id}", 
            json={"amount": amount, "method": method}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_recent_transactions(customer_id: str, limit: int = 5) -> dict:
    """
    Fetches recent transactions.
    Args:
        customer_id: The unique ID.
        limit: Number of transactions (default 5).
    """
    try:
        response = requests.get(f"{API_BASE_URL}/transactions/{customer_id}", params={"limit": limit})
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def convert_to_emi(txn_id: str, tenure_months: int) -> dict:
    """
    Converts a specific transaction into EMI installments.
    Args:
        txn_id: The ID of the transaction.
        tenure_months: Duration in months (3-24).
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/emi/convert", 
            json={"txn_id": txn_id, "tenure_months": tenure_months}
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_collections_status(customer_id: str) -> dict:
    """Checks if the customer is in a high-risk category due to overdue payments."""
    try:
        response = requests.get(f"{API_BASE_URL}/collections/status/{customer_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- 2. System Instruction & Model Setup ---

system_instruction_text = """
You are the 'OneCard GenAI Assistant'. You help customers manage their credit cards.

CORE RULES:
1. **Identification:** Always identify the user by `customer_id` before performing actions (except for 'open_account').
2. **Safety:** Before processing a payment or EMI conversion, explicitly confirm the details (amount/tenure) with the user.
3. **Data Handling:** When you get data (like a bill or transaction list), summarize it clearly.
4. **Tone:** Be professional, empathetic, and concise.
"""

# FIX: Create the Model object explicitly and pass system_instruction here
# The 'Model' class handles the prompt configuration, while 'Agent' handles the execution loop.
model_config = Model(
    model="gemini-2.5-flash",
    system_instruction=system_instruction_text
)

# --- 3. Agent Initialization ---

onecard_agent = Agent(
    name="OneCardBot",
    model=model_config,  # Pass the configured Model object, not a string
    tools=[
        open_account,
        get_account_status,
        check_card_delivery,
        get_current_bill,
        make_payment,
        get_recent_transactions,
        convert_to_emi,
        check_collections_status
    ]
)

# --- 4. Run Loop ---

def run_chat_session():
    print(f"🤖 {onecard_agent.name} (ADK) is ready! (Type 'exit' to quit)")
    print("---------------------------------------------------------")
    
    # Start session
    session = onecard_agent.start_session()

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            # The ADK Agent class handles tool calling internally
            response = session.send(user_input)
            
            # Depending on ADK version, response might be an object or string.
            # Usually response.text or just response
            if hasattr(response, 'text'):
                print(f"Bot: {response.text}")
            else:
                print(f"Bot: {response}")

        except Exception as e:
            print(f"Bot: Error encountered - {e}")

if __name__ == "__main__":
    run_chat_session()