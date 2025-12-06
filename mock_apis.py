from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timedelta

app = FastAPI(title="OneCard Mock APIs")

# Mock customer data
customers = {
    "cust_001": {"name": "John Doe", "phone": "+919876543210"},
    "cust_002": {"name": "Jane Smith", "phone": "+918765432109"}
}


class PaymentRequest(BaseModel):
    amount: float
    method: str  # "UPI", "Card", "Netbanking"


class EMIRequest(BaseModel):
    txn_id: str
    tenure_months: int


@app.get("/account/status/{customer_id}")
def get_account_status(customer_id: str):
    return {
        "customer_id": customer_id,
        "status": "verified" if customer_id == "cust_001" else "pending",
        "submitted_at": "2025-12-01",
        "verified_at": "2025-12-05" if customer_id == "cust_001" else None
    }


@app.post("/account/open")
def open_account(phone: str):
    customer_id = f"cust_{str(uuid.uuid4())[:6]}"
    customers[customer_id] = {"name": "New Customer", "phone": phone}
    return {"customer_id": customer_id, "next_step": "upload_documents"}


@app.get("/card/status/{customer_id}")
def get_card_status(customer_id: str):
    return {
        "status": "shipped",
        "tracking_id": "TK123456",
        "eta": "2025-12-08",
        "location": "Mumbai Sorting Facility"
    }


@app.get("/bill/{customer_id}")
def get_current_bill(customer_id: str):
    return {
        "total_due": 5234.50,
        "minimum_due": 1500.00,
        "due_date": "2025-12-15",
        "breakdown": {
            "principal": 4500.00,
            "interest": 234.50,
            "fees": 500.00
        }
    }


@app.post("/payment/initiate")
def initiate_payment(customer_id: str, req: PaymentRequest):
    txn_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
    return {
        "transaction_id": txn_id,
        "status": "success",
        "amount_paid": req.amount,
        "new_balance": 3734.50 if req.amount == 1500 else 0,
        "confirmation": f"Payment {txn_id} completed"
    }


@app.get("/transactions/{customer_id}")
def get_transactions(customer_id: str, limit: int = 10):
    return [
        {"id": "TXN001", "amount": 2500.00,
            "merchant": "Amazon", "date": "2025-12-03"},
        {"id": "TXN002", "amount": 734.50, "merchant": "Swiggy", "date": "2025-12-04"}
    ]


@app.post("/emi/convert")
def convert_to_emi(req: EMIRequest):
    return {
        "emi_id": f"EMI_{req.txn_id}",
        "monthly_amount": 850.00,
        "tenure": req.tenure_months,
        "interest_rate": 14.5,
        "status": "active"
    }


@app.get("/overdue/{customer_id}")
def get_overdue(customer_id: str):
    return {
        "overdue_amount": 2345.00,
        "days_overdue": 7,
        "next_due_date": "2025-12-13",
        "payment_options": ["full_payment", "installments", "settlement"]
    }
