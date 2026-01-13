from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import User, Account, Transaction, ServiceRequest
from .agents import Orchestrator, CustomerSupportAgent, AccountsAgent, LoansAgent
import uvicorn

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed Initial Data
def seed_data(db: Session):
    if not db.query(User).first():
        user = User(name="John Doe", email="john@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        from datetime import datetime, timedelta
        
        # Create Account
        account = Account(user_id=user.id, account_type="Savings", balance=5000.00)
        db.add(account)
        db.commit()
        db.refresh(account)

        # Seed Transactions
        transactions = [
            Transaction(account_id=account.id, transaction_type="Credit", amount=3000.00, status="Success", description="Salary Update", timestamp=datetime.utcnow() - timedelta(days=10)),
            Transaction(account_id=account.id, transaction_type="Debit", amount=5.50, status="Success", description="Starbucks Coffee", timestamp=datetime.utcnow() - timedelta(days=1)),
            Transaction(account_id=account.id, transaction_type="Debit", amount=15.00, status="Success", description="Uber Ride", timestamp=datetime.utcnow() - timedelta(days=2)),
            Transaction(account_id=account.id, transaction_type="Debit", amount=120.00, status="Success", description="Grocery Store", timestamp=datetime.utcnow() - timedelta(days=3)),
            Transaction(account_id=account.id, transaction_type="Credit", amount=500.00, status="Success", description="Freelance Payment", timestamp=datetime.utcnow() - timedelta(days=5)),
        ]
        db.add_all(transactions)
        db.commit()
        
        print("Seeded initial data (User, Account, Transactions).")

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_data(db)

class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: str
    role: str = "model"

orchestrator = Orchestrator()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    # Mock User ID 1
    user_id = 1
    
    try:
        # 1. Route
        agent_type = orchestrator.route(request.message, request.history)
        print(f"Routed to: {agent_type}")
        
        # 2. Dispatch
        if agent_type == "ACCOUNTS":
            agent = AccountsAgent(db, user_id)
        elif agent_type == "LOANS_SERVICES":
            agent = LoansAgent(db, user_id)
        else:
            agent = CustomerSupportAgent(db, user_id)
            
        # 3. Process
        response_text = agent.process(request.message, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error processing request: {e}")
        return ChatResponse(response=f"Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
