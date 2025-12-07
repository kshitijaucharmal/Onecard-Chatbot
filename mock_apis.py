from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc

# Import from the SQLite setup script
from setup_database import Base, Customer, Transaction, Card, SessionLocal, engine

# Create tables if they don't exist (safety check)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OneCard GenAI Assistant APIs (SQLite)",
    description="Mock APIs backed by a local SQLite database file.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency ---


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models ---


class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    method: str


class AccountOpenRequest(BaseModel):
    phone: str
    name: str


class EMIRequest(BaseModel):
    txn_id: str
    tenure_months: int = Field(..., ge=3, le=24)

# --- Endpoints ---


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "active", "db": "SQLite Local File"}


@app.post("/account/open", tags=["Account"], status_code=status.HTTP_201_CREATED)
def open_account(req: AccountOpenRequest, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.phone == req.phone).first():
        raise HTTPException(
            status_code=400, detail="Phone number already registered.")

    new_cust = Customer(
        id=f"cust_{str(uuid.uuid4())[:8]}",
        name=req.name,
        phone=req.phone,
        status="pending_verification",
        due_date=None
    )
    db.add(new_cust)
    db.commit()
    return {"customer_id": new_cust.id, "message": "Account created. Please complete KYC."}


@app.get("/account/status/{customer_id}", tags=["Account"])
def get_account_status(customer_id: str, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "customer_id": cust.id,
        "name": cust.name,
        "status": cust.status,
        "balance_due": cust.balance_due
    }


@app.get("/card/status/{customer_id}", tags=["Card"])
def get_card_status(customer_id: str, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.customer_id == customer_id).first()
    if not card:
        raise HTTPException(
            status_code=404, detail="No card found for this customer")

    eta = (datetime.now() + timedelta(days=2)
           ).strftime("%Y-%m-%d") if card.delivery_status == "in_transit" else "N/A"

    return {
        "status": card.status,
        "delivery_stage": card.delivery_status,
        "tracking_id": card.tracking_id,
        "eta": eta
    }


@app.get("/bill/{customer_id}", tags=["Billing"])
def get_current_bill(customer_id: str, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    is_overdue = False
    if cust.due_date and cust.balance_due > 0:
        # Convert date to string or compare date objects directly
        if datetime.now().date() > cust.due_date:
            is_overdue = True

    return {
        "total_due": cust.balance_due,
        "minimum_due": cust.min_due,
        "due_date": cust.due_date,
        "status": "overdue" if is_overdue else "unpaid"
    }


@app.post("/payment/initiate/{customer_id}", tags=["Payments"])
def initiate_payment(customer_id: str, req: PaymentRequest, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    if cust.balance_due <= 0:
        return {"message": "No dues pending."}

    cust.balance_due = max(0, cust.balance_due - req.amount)

    payment_txn = Transaction(
        id=f"PAY_{uuid.uuid4().hex[:8].upper()}",
        customer_id=customer_id,
        merchant="Credit Card Repayment",
        amount=-req.amount,
        category="Repayment",
        date=datetime.now()
    )
    db.add(payment_txn)
    db.commit()

    return {
        "status": "success",
        "new_balance": cust.balance_due,
        "txn_id": payment_txn.id
    }


@app.get("/transactions/{customer_id}", tags=["Transactions"])
def get_transactions(customer_id: str, limit: int = 5, db: Session = Depends(get_db)):
    txns = db.query(Transaction)\
             .filter(Transaction.customer_id == customer_id)\
             .order_by(desc(Transaction.date))\
             .limit(limit)\
             .all()

    return {"count": len(txns), "transactions": txns}


@app.get("/collections/status/{customer_id}", tags=["Collections"])
def get_overdue_status(customer_id: str, db: Session = Depends(get_db)):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(status_code=404, detail="Customer not found")

    is_critical = cust.balance_due > 5000

    return {
        "total_outstanding": cust.balance_due,
        "risk_category": "High" if is_critical else "Low",
        "action_required": "Immediate Payment" if is_critical else "None"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
