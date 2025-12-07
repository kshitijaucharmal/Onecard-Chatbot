import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Float, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from faker import Faker

# --- Database Config ---
DATABASE_URL = "sqlite:///./onecard.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
fake = Faker('en_IN')

# --- Schema Definitions ---


class Customer(Base):
    __tablename__ = "customers"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True)
    status = Column(String, default="verified")  # verified, pending, blocked
    credit_limit = Column(Float, default=100000.0)
    balance_due = Column(Float, default=0.0)
    min_due = Column(Float, default=0.0)
    due_date = Column(Date, nullable=True)
    reward_points = Column(Float, default=0.0)  # New: Rewards tracking

    transactions = relationship("Transaction", back_populates="customer")
    cards = relationship("Card", back_populates="customer")


class Card(Base):
    __tablename__ = "cards"
    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    card_number = Column(String, unique=True)
    status = Column(String, default="active")  # active, blocked, frozen
    delivery_status = Column(String, default="delivered")
    tracking_id = Column(String, nullable=True)
    is_physical = Column(Boolean, default=True)

    customer = relationship("Customer", back_populates="cards")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    merchant = Column(String)
    amount = Column(Float)
    category = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    is_emi = Column(Boolean, default=False)
    dispute_status = Column(String, default="none")  # none, open, resolved

    customer = relationship("Customer", back_populates="transactions")

# --- Seeding Logic ---


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Customer).count() > 0:
        print("Database already contains data. Skipping seed.")
        return

    print("Seeding SQLite database with comprehensive mock data...")

    for _ in range(50):
        # Create Customer
        cust_id = f"cust_{uuid.uuid4().hex[:8]}"
        is_overdue = random.choice([True, False, False])
        balance = round(random.uniform(1000, 50000), 2) if is_overdue else 0
        due_date = datetime.now() + timedelta(days=random.randint(-5, 20))

        customer = Customer(
            id=cust_id,
            name=fake.name(),
            phone=fake.phone_number(),
            status="verified",
            credit_limit=random.choice([50000, 100000, 200000]),
            balance_due=balance,
            min_due=balance * 0.05,
            due_date=due_date.date(),
            reward_points=random.randint(0, 5000)
        )
        db.add(customer)

        # Create Card
        card = Card(
            id=f"card_{uuid.uuid4().hex[:8]}",
            customer_id=cust_id,
            card_number=fake.credit_card_number(card_type="visa"),
            status="active",
            delivery_status=random.choice(
                ["delivered", "in_transit", "pending"]),
            tracking_id=f"TRK_{uuid.uuid4().hex[:8].upper()}"
        )
        db.add(card)

        # Create Transactions
        for _ in range(random.randint(3, 8)):
            txn = Transaction(
                id=f"txn_{uuid.uuid4().hex[:8]}",
                customer_id=cust_id,
                merchant=fake.company(),
                amount=round(random.uniform(100, 10000), 2),
                category=random.choice(
                    ["Food", "Travel", "Utilities", "Shopping", "Entertainment"]),
                date=fake.date_time_between(start_date='-30d', end_date='now')
            )
            db.add(txn)

    db.commit()
    print("Seeding Complete. 'onecard.db' is ready.")
    db.close()


if __name__ == "__main__":
    seed_database()
