from fastapi import FastAPI, HTTPException, status, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timedelta

# --- Configuration & Setup ---
app = FastAPI(
    title="OneCard GenAI Assistant APIs",
    description="Mock APIs for Credit Card Bot Assignment handling Accounts, Bills, and Transactions.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-Memory Database (Simulated Persistence) ---
# This simulates a real DB. Changes (like payments) will persist until the server restarts.
mock_db: Dict[str, dict] = {
    "cust_001": {
        "name": "Arjun Mehta",
        "phone": "+919876543210",
        "status": "verified",
        "balance_due": 5234.50,
        "min_due": 1500.00,
        "due_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
        "transactions": [
            {"id": "TXN_001", "merchant": "Amazon India", "amount": 2500.00, "date": "2023-12-01"},
            {"id": "TXN_002", "merchant": "Swiggy", "amount": 450.00, "date": "2023-12-02"},
            {"id": "TXN_003", "merchant": "Uber", "amount": 1200.00, "date": "2023-12-03"}
        ]
    }
}

# --- Pydantic Models (Input Validation) ---

class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    method: str = Field(..., pattern="^(UPI|Card|Netbanking)$", description="Payment method: UPI, Card, or Netbanking")

class EMIRequest(BaseModel):
    txn_id: str
    tenure_months: int = Field(..., ge=3, le=24, description="Tenure must be between 3 and 24 months")

class AccountOpenRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15, description="Valid phone number")
    name: str

# --- Helper Functions ---

def get_customer_or_404(customer_id: str):
    if customer_id not in mock_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Customer ID {customer_id} not found."
        )
    return mock_db[customer_id]

# --- Endpoints ---

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "active", "timestamp": datetime.now()}

# 1. Account & Onboarding 
@app.post("/account/open", tags=["Account"], status_code=status.HTTP_201_CREATED)
def open_account(req: AccountOpenRequest):
    """Simulates opening a new account."""
    customer_id = f"cust_{str(uuid.uuid4())[:6]}"
    
    mock_db[customer_id] = {
        "name": req.name,
        "phone": req.phone,
        "status": "pending_verification",
        "balance_due": 0.0,
        "min_due": 0.0,
        "due_date": None,
        "transactions": []
    }
    
    return {
        "customer_id": customer_id, 
        "message": "Account created successfully.",
        "next_step": "Please complete KYC verification."
    }

@app.get("/account/status/{customer_id}", tags=["Account"])
def get_account_status(customer_id: str):
    customer = get_customer_or_404(customer_id)
    return {
        "customer_id": customer_id,
        "name": customer["name"],
        "status": customer["status"],
        "is_active": customer["status"] == "verified"
    }

# 2. Card Delivery 
@app.get("/card/status/{customer_id}", tags=["Card"])
def get_card_status(customer_id: str):
    get_customer_or_404(customer_id) # Validate user exists
    
    # Dynamic ETA: 3 days from now
    eta_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    
    return {
        "status": "in_transit",
        "tracking_id": f"TRK_{uuid.uuid4().hex[:8].upper()}",
        "courier": "BlueDart",
        "eta": eta_date,
        "location": "Local Distribution Hub"
    }

# 3. Bill & Statement 
@app.get("/bill/{customer_id}", tags=["Billing"])
def get_current_bill(customer_id: str):
    customer = get_customer_or_404(customer_id)
    
    total = customer["balance_due"]
    
    return {
        "total_due": total,
        "minimum_due": customer["min_due"],
        "due_date": customer["due_date"],
        "currency": "INR",
        "status": "overdue" if total > 0 and datetime.now() > datetime.strptime(customer["due_date"], "%Y-%m-%d") else "unpaid"
    }

# 4. Repayments (Action Execution) [cite: 11, 18]
@app.post("/payment/initiate/{customer_id}", tags=["Payments"])
def initiate_payment(customer_id: str, req: PaymentRequest):
    """
    Simulates a payment. 
    Crucially, this updates the mock DB state, so subsequent bill checks reflect the payment.
    """
    customer = get_customer_or_404(customer_id)
    
    # Logic: Prevent paying if balance is 0 (optional constraint)
    if customer["balance_due"] <= 0:
        return {"message": "No dues pending. Payment not required."}

    # Update State
    txn_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
    new_balance = max(0, customer["balance_due"] - req.amount)
    customer["balance_due"] = new_balance
    
    # Record this as a transaction
    payment_record = {
        "id": txn_id,
        "merchant": "Credit Card Repayment",
        "amount": -req.amount, # Negative to show credit
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    customer["transactions"].insert(0, payment_record)

    return {
        "transaction_id": txn_id,
        "status": "success",
        "amount_paid": req.amount,
        "remaining_balance": new_balance,
        "message": f"Payment of INR {req.amount} received via {req.method}."
    }

# 5. Transactions 
@app.get("/transactions/{customer_id}", tags=["Transactions"])
def get_transactions(customer_id: str, limit: int = 5):
    customer = get_customer_or_404(customer_id)
    return {
        "customer_id": customer_id,
        "count": len(customer["transactions"]),
        "transactions": customer["transactions"][:limit]
    }

# 6. EMI Conversion 
@app.post("/emi/convert", tags=["EMI"])
def convert_to_emi(req: EMIRequest):
    # Mock logic: Calculate dummy EMI
    interest_rate = 14.0 # 14% p.a.
    # Simple Interest Logic for mock
    monthly_installment = (5000 + (5000 * interest_rate / 100)) / req.tenure_months
    
    return {
        "emi_id": f"EMI_{req.txn_id}",
        "original_txn_id": req.txn_id,
        "tenure_months": req.tenure_months,
        "interest_rate_pa": f"{interest_rate}%",
        "estimated_monthly_installment": round(monthly_installment, 2),
        "status": "active",
        "message": f"Transaction {req.txn_id} converted to EMI successfully."
    }

# 7. Collections (For overdue customers) 
@app.get("/collections/status/{customer_id}", tags=["Collections"])
def get_overdue_status(customer_id: str):
    customer = get_customer_or_404(customer_id)
    
    # Mock logic: If balance > 5000, consider them in 'collections' risk
    is_critical = customer["balance_due"] > 5000
    
    return {
        "total_outstanding": customer["balance_due"],
        "risk_category": "High" if is_critical else "Low",
        "settlement_offer_eligible": is_critical,
        "recommended_action": "Pay immediately to avoid charges" if is_critical else "Pay by due date"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)