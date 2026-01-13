from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    
    accounts = relationship("Account", back_populates="owner")
    service_requests = relationship("ServiceRequest", back_populates="owner")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    account_type = Column(String) # Savings, Current
    balance = Column(Float, default=0.0)
    
    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    transaction_type = Column(String) # Debit, Credit, Transfer
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String) # Pending, Success, Failed
    description = Column(String)

    account = relationship("Account", back_populates="transactions")

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_type = Column(String) # Loan, Credit Card, etc.
    details = Column(String) # JSON or text details
    status = Column(String, default="Requested")
    timestamp = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="service_requests")
