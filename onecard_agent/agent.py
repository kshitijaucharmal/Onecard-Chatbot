from google.adk.tools import AgentTool, FunctionTool, google_search
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

import os
import requests
from typing import Optional

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"

# --- 1. Tool Definitions ---


def open_account(name: str, phone: str) -> dict:
    """
    Opens a new credit card account for a customer.
    Use this when a user explicitly asks to 'sign up', 'register', or 'get a card'.

    Args:
        name: The full name of the customer.
        phone: A valid 10-digit phone number.

    Returns:
        dict: Contains the new 'customer_id' which MUST be shown to the user.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/account/open", json={"name": name, "phone": phone})
        return response.json()
    except Exception as e:
        return {"error": f"Connection failed: {str(e)}"}


def get_account_status(customer_id: str) -> dict:
    """
    Retrieves the verification status (e.g., Verified, Pending) and balance overview.

    Args:
        customer_id: The unique string ID (e.g., 'cust_12345').
    """
    try:
        response = requests.get(f"{API_BASE_URL}/account/status/{customer_id}")
        if response.status_code == 404:
            return {"error": "Customer ID not found."}
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def check_card_delivery(customer_id: str) -> dict:
    """
    Checks where the physical card is (e.g., In Transit, Delivered) and provides ETA.
    Use this for queries like "Where is my card?" or "When will it arrive?".
    """
    try:
        response = requests.get(f"{API_BASE_URL}/card/status/{customer_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_current_bill(customer_id: str) -> dict:
    """
    Fetches the current billing details including total amount due, minimum due, and due date.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/bill/{customer_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def make_payment(customer_id: str, amount: float, method: str) -> dict:
    """
    Initiates a bill payment. 

    Args:
        customer_id: The unique customer ID.
        amount: The amount in INR to pay.
        method: The payment mode. MUST be one of: 'UPI', 'Card', or 'Netbanking'.
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
    Fetches the list of recent transactions.

    Args:
        customer_id: The unique customer ID.
        limit: Number of transactions to return (default is 5).
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/transactions/{customer_id}", params={"limit": limit})
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def convert_to_emi(txn_id: str, tenure_months: int) -> dict:
    """
    Converts a specific transaction into EMI installments.

    Args:
        txn_id: The ID of the transaction to convert (e.g., 'txn_abc123').
        tenure_months: Duration in months. MUST be between 3 and 24.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/emi/convert",
            json={"txn_id": txn_id, "tenure_months": tenure_months}
        )
        if response.status_code == 400:
            return {"error": "Invalid request. Transaction might be too small or tenure invalid."}
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def check_collections_status(customer_id: str) -> dict:
    """
    Checks if the customer is in a high-risk category due to overdue payments.
    Use this if the customer mentions 'collections agent' or 'harassment'.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/collections/status/{customer_id}")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# --- 2. System Instruction ---


system_prompt = """
You are the **OneCard GenAI Assistant**, a helpful and professional banking bot.

### YOUR CAPABILITIES:
You have access to a real-time banking system. You can check balances, track cards, convert payments to EMI, and help open accounts.

### RULES OF ENGAGEMENT:
1.  **Identity Verification:** * For almost all actions (checking bill, status, etc.), you MUST ask the user for their `customer_id` first if they haven't provided it. 
    * The ONLY exception is `open_account`, which generates a new ID.
2.  **Safety First:** * Before executing money actions (`make_payment` or `convert_to_emi`), summarize the details (Amount, Tenure) and ask for explicit confirmation (e.g., "Shall I proceed?").
3.  **Data Presentation:** * When showing a bill or list of transactions, use clear bullet points.
    * If a transaction was converted to EMI, mention the monthly installment amount clearly.
4.  **Tone:**
    * Be polite, empathetic, and concise. 
    * If the user is stressed about `collections`, be calm and helpful.

### EXAMPLES:
* User: "I want to pay my bill."
    Bot: "I can help with that. Please provide your Customer ID and the amount you wish to pay."
* User: "Convert my last transaction to EMI."
    Bot: "I'll need your Customer ID to check your recent transactions first."
"""

# --- 3. Agent Initialization ---

root_agent = Agent(
    name="OneCardBot",
    # Note: Ensure this model name is valid in your ADK version.
    # Fallback to "gemini-1.5-flash" if "lite" is unavailable.
    model="gemini-2.5-flash-lite",
    instruction=system_prompt,
    tools=[
        open_account,
        get_account_status,
        check_card_delivery,
        get_current_bill,
        make_payment,
        get_recent_transactions,
        convert_to_emi,
        check_collections_status
    ],
    output_key="final_response",
)
