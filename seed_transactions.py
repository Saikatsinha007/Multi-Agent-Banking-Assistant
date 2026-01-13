from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User, Account, Transaction
from datetime import datetime, timedelta
import os

# Connect to DB
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "app.db")
if os.name == 'nt':
    DB_PATH = DB_PATH.replace('\\', '/')
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Check user
user = db.query(User).first()
if not user:
    print("Creating User...")
    user = User(name="John Doe", email="john@example.com")
    db.add(user)
    db.commit()

# Check account
account = db.query(Account).filter(Account.user_id == user.id).first()
if not account:
    print("Creating Account...")
    account = Account(user_id=user.id, account_type="Savings", balance=5000.00)
    db.add(account)
    db.commit()

# Add Transactions if empty
if db.query(Transaction).count() == 0:
    print("Seeding Transactions...")
    transactions = [
        Transaction(account_id=account.id, transaction_type="Credit", amount=3000.00, status="Success", description="Salary Update", timestamp=datetime.utcnow() - timedelta(days=10)),
        Transaction(account_id=account.id, transaction_type="Debit", amount=5.50, status="Success", description="Starbucks Coffee", timestamp=datetime.utcnow() - timedelta(days=1)),
        Transaction(account_id=account.id, transaction_type="Debit", amount=15.00, status="Success", description="Uber Ride", timestamp=datetime.utcnow() - timedelta(days=2)),
        Transaction(account_id=account.id, transaction_type="Debit", amount=120.00, status="Success", description="Grocery Store", timestamp=datetime.utcnow() - timedelta(days=3)),
        Transaction(account_id=account.id, transaction_type="Credit", amount=500.00, status="Success", description="Freelance Payment", timestamp=datetime.utcnow() - timedelta(days=5)),
    ]
    db.add_all(transactions)
    db.commit()
    print("Transactions Added!")
else:
    print("Transactions already exist.")

db.close()
