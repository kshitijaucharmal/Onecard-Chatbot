from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

# Import local DB setup
from setup_database import Base, Customer, Transaction, Card, SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="OneCard Core Banking System", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependencies & Utilities ---


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Request Models ---


class AccountOpenRequest(BaseModel):
    name: str
    phone: str


class PaymentRequest(BaseModel):
    amount: float
    method: str  # UPI, Netbanking


class EMIRequest(BaseModel):
    txn_id: str
    tenure_months: int


class DisputeRequest(BaseModel):
    txn_id: str
    reason: str


class CardControlRequest(BaseModel):
    action: str  # block, unblock, freeze

# ==========================================
# 1. ACCOUNT & ONBOARDING
# ==========================================


@app.post("/account/open", tags=["Account"])
def open_account(req: AccountOpenRequest, db: Session = Depends(get_db)):
    """Simulates new user onboarding."""
    if db.query(Customer).filter(Customer.phone == req.phone).first():
        raise HTTPException(
            status_code=400, detail="Phone already registered.")

    new_cust = Customer(
        id=f"cust_{str(uuid.uuid4())[:8]}",
        name=req.name,
        phone=req.phone,
        status="pending_kyc",
        credit_limit=50000.0
    )
    db.add(new_cust)
    db.commit()
    return {"customer_id": new_cust.id, "message": "Account created. KYC Pending."}


@app.get("/account/details/{customer_id}", tags=["Account"])
def get_account_details(customer_id: str, db: Session = Depends(get_db)):
    """Fetch holistic account view including rewards."""
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(404, "Customer not found")

    return {
        "name": cust.name,
        "status": cust.status,
        "credit_limit": cust.credit_limit,
        "available_limit": cust.credit_limit - cust.balance_due,
        "reward_points": cust.reward_points
    }

# ==========================================
# 2. CARD MANAGEMENT & DELIVERY
# ==========================================


@app.get("/card/track/{customer_id}", tags=["Card"])
def track_card(customer_id: str, db: Session = Depends(get_db)):
    """Returns delivery status for physical kits."""
    card = db.query(Card).filter(Card.customer_id == customer_id).first()
    if not card:
        raise HTTPException(404, "No card found")

    eta = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    return {
        "card_number_mask": f"XXXX-XXXX-XXXX-{card.card_number[-4:]}",
        "delivery_status": card.delivery_status,
        "tracking_id": card.tracking_id,
        "estimated_arrival": eta if card.delivery_status == "in_transit" else "N/A"
    }


@app.post("/card/control/{customer_id}", tags=["Card"])
def manage_card_security(customer_id: str, req: CardControlRequest, db: Session = Depends(get_db)):
    """Handle locking/unlocking cards (Security)."""
    card = db.query(Card).filter(Card.customer_id == customer_id).first()
    if not card:
        raise HTTPException(404, "Card not found")

    if req.action == "block":
        card.status = "blocked"
        msg = "Card permanently blocked. Replacement initiated."
    elif req.action == "freeze":
        card.status = "frozen"
        msg = "Card temporarily frozen."
    elif req.action == "unblock":
        card.status = "active"
        msg = "Card active again."
    else:
        raise HTTPException(400, "Invalid action")

    db.commit()
    return {"status": "success", "new_card_status": card.status, "message": msg}

# ==========================================
# 3. BILLING & REPAYMENTS [cite: 10, 11]
# ==========================================


@app.get("/bill/summary/{customer_id}", tags=["Billing"])
def get_bill(customer_id: str, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(404, "Customer not found")

    overdue = cust.due_date and cust.due_date < datetime.now().date()

    return {
        "total_outstanding": cust.balance_due,
        "min_due": cust.min_due,
        "due_date": str(cust.due_date),
        "is_overdue": overdue,
        "statement_period": "Nov 1 - Nov 30"
    }


@app.post("/payment/pay/{customer_id}", tags=["Billing"])
def make_payment(customer_id: str, req: PaymentRequest, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(404, "Customer not found")

    cust.balance_due = max(0, cust.balance_due - req.amount)
    cust.min_due = max(0, cust.min_due - req.amount)

    # Record the payment as a transaction
    pay_txn = Transaction(
        id=f"PAY_{uuid.uuid4().hex[:6].upper()}",
        customer_id=customer_id,
        merchant="OneCard Payment",
        amount=req.amount,
        category="Payment",
        date=datetime.utcnow()
    )
    db.add(pay_txn)
    db.commit()

    return {"status": "success", "new_balance": cust.balance_due, "txn_ref": pay_txn.id}

# ==========================================
# 4. TRANSACTIONS & EMI [cite: 9]
# ==========================================


@app.get("/transactions/list/{customer_id}", tags=["Transactions"])
def list_transactions(customer_id: str, limit: int = 5, db: Session = Depends(get_db)):
    txns = db.query(Transaction).filter(Transaction.customer_id == customer_id)\
             .order_by(desc(Transaction.date)).limit(limit).all()
    return {"count": len(txns), "transactions": txns}


@app.post("/transactions/convert_emi", tags=["Transactions"])
def convert_emi(req: EMIRequest, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == req.txn_id).first()
    if not txn:
        raise HTTPException(404, "Transaction not found")

    if txn.amount < 2500:
        raise HTTPException(400, "Transaction too small for EMI (Min 2500).")

    interest = 0.15  # 15% PA mock
    total_pay = txn.amount * (1 + (interest * req.tenure_months/12))
    monthly = total_pay / req.tenure_months

    txn.is_emi = True
    txn.category += " (Converted to EMI)"
    db.commit()

    return {
        "status": "converted",
        "monthly_emi": round(monthly, 2),
        "tenure": req.tenure_months,
        "message": f"Converted to {req.tenure_months} months EMI."
    }


@app.post("/transactions/dispute", tags=["Transactions"])
def report_dispute(req: DisputeRequest, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter(Transaction.id == req.txn_id).first()
    if not txn:
        raise HTTPException(404, "Transaction not found")

    txn.dispute_status = "open"
    db.commit()
    return {"ticket_id": f"TKT_{uuid.uuid4().hex[:6]}", "status": "investigation_started"}

# ==========================================
# 5. COLLECTIONS (For Overdue)
# ==========================================


@app.get("/collections/check/{customer_id}", tags=["Collections"])
def check_collections_status(customer_id: str, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(404, "Customer not found")

    # Logic: High risk if overdue > 5000 AND date passed
    is_overdue = cust.due_date and cust.due_date < datetime.now().date()
    high_risk = is_overdue and cust.balance_due > 5000

    return {
        "risk_level": "CRITICAL" if high_risk else "NORMAL",
        "agent_assigned": True if high_risk else False,
        "settlement_offer_available": True if high_risk else False,
        "message": "Please pay immediately to avoid legal action." if high_risk else "Account is in good standing."
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
