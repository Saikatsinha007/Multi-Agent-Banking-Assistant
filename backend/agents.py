from groq import Groq
from .config import GROQ_API_KEY
from .database import SessionLocal
from .models import User, Account, Transaction, ServiceRequest
from sqlalchemy.orm import Session
import json
import time

# Configure Groq
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
    MODEL_NAME = "llama-3.3-70b-versatile" # Fast, smart, tool-capable model
else:
    client = None
    print("Warning: GROQ_API_KEY not set.")

class BankingAgent:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def process(self, message: str, history: list):
        raise NotImplementedError
        
    def _convert_history(self, history):
        # Gemini history was [{'role': 'user', 'parts': ['msg']}]
        # OpenAI/Groq history is [{'role': 'user', 'content': 'msg'}]
        # Need to normalize frontend history or adapt it here.
        # Assuming frontend sends compatible format or we convert.
        # Frontend app.js sends: { role: 'user', parts: [text] }
        
        new_history = []
        for h in history:
            role = h.get('role')
            if role == "model": role = "assistant"
            
            parts = h.get('parts', [])
            content = parts[0] if parts else ""
            
            new_history.append({"role": role, "content": content})
        return new_history

class CustomerSupportAgent(BankingAgent):
    def process(self, message: str, history: list):
        system_prompt = """
        You are a helpful Customer Support Agent for a bank.
        You can answer questions about:
        - Branch working hours (9 AM - 5 PM, Mon-Sat)
        - Customer care numbers (1-800-BANK-HELP)
        - Account opening (Need ID, Address Proof, Photo)
        - ATM availability (24/7)
        - Card blocking (Call support or use the app)
        
        If the user asks about personal details, account balance, or loans, politely say you can't help with that and they should ask the relevant department.
        """
        
        messages = [{"role": "system", "content": system_prompt}] + self._convert_history(history)
        messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7
        )
        return completion.choices[0].message.content

class AccountsAgent(BankingAgent):
    def process(self, message: str, history: list):
        system_prompt = """
        You are the Accounts Agent for NeoBank.
        You have DIRECT ACCESS to the user's database via tools.
        
        PERMISSIONS:
        - You ARE authorized to check balances and transactions.
        - You SHOULD NOT refuse to answer valid queries about the user's account.
        - When asked about transactions (like 'coffee' or 'deposits'), call 'get_recent_transactions' first, then analyze the result to answer.
        """
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_balance",
                    "description": "Get the current balance of the user's account",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recent_transactions",
                    "description": "Get the last 5 transactions for the account",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            }
        ]
        
        messages = [{"role": "system", "content": system_prompt}] + self._convert_history(history)
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            # Append the model's response (which contains the tool call) to history
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "get_balance":
                    function_response = self.get_balance()
                elif function_name == "get_recent_transactions":
                    function_response = self.get_recent_transactions()
                else:
                    function_response = "Error: Unknown function"
                
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )
            
            # Second call to get the final natural language response
            second_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            return second_response.choices[0].message.content
        else:
            return response_message.content

    def get_balance(self):
        account = self.db.query(Account).filter(Account.user_id == self.user_id).first()
        if account:
            return f"{account.balance} USD"
        return "Account not found."

    def get_recent_transactions(self):
        account = self.db.query(Account).filter(Account.user_id == self.user_id).first()
        if not account:
            return "Account not found."
        
        txs = self.db.query(Transaction).filter(Transaction.account_id == account.id).order_by(Transaction.timestamp.desc()).limit(10).all()
        return "\n".join([f"{t.timestamp.date()}: {t.transaction_type} ${t.amount} ({t.description}) - {t.status}" for t in txs])

class LoansAgent(BankingAgent):
    def process(self, message: str, history: list):
        system_prompt = """
        You are the Loans & Services Agent for NeoBank.
        You are authorized to submit applications on behalf of the user.
        
        INSTRUCTIONS:
        - If the user asks for a loan or service, ALWAYS use the provided tools to submit the request.
        - Do not ask for sensitive personal info (like SSN) in chat; just assume the user is authenticated and submit the request type/amount.
        """
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "apply_for_loan",
                    "description": "Apply for a new loan",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {"type": "number", "description": "The amount of money requested"},
                            "loan_type": {"type": "string", "description": "The type of loan (e.g. Personal, Home, Auto)"}
                        },
                        "required": ["amount", "loan_type"],
                    },
                },
            },
             {
                "type": "function",
                "function": {
                    "name": "request_service",
                    "description": "Request a bank service like checkbook or credit card",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service_type": {"type": "string", "description": "Type of service (e.g. Credit Card, Checkbook)"},
                            "details": {"type": "string", "description": "Additional details"}
                        },
                        "required": ["service_type"],
                    },
                },
            }
        ]
        
        # Ensure system prompt works
        messages = [{"role": "system", "content": system_prompt}] + self._convert_history(history)
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "apply_for_loan":
                    result = self.apply_for_loan(function_args.get("amount"), function_args.get("loan_type"))
                elif function_name == "request_service":
                    result = self.request_service(function_args.get("service_type"), function_args.get("details", ""))
                
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(result),
                    }
                )
            
            second_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages
            )
            return second_response.choices[0].message.content
        else:
            return response_message.content

    def apply_for_loan(self, amount: float, loan_type: str):
        sr = ServiceRequest(
            user_id=self.user_id,
            service_type=f"Loan Application - {loan_type}",
            details=f"Amount: {amount}",
            status="Under Review"
        )
        self.db.add(sr)
        self.db.commit()
        return f"Loan application for {amount} ({loan_type}) submitted successfully. Reference ID: {sr.id}"

    def request_service(self, service_type: str, details: str):
         sr = ServiceRequest(
            user_id=self.user_id,
            service_type=service_type,
            details=details,
             status="Requested"
        )
         self.db.add(sr)
         self.db.commit()
         return f"Service request '{service_type}' collected. Reference ID: {sr.id}"

class Orchestrator:
    def __init__(self):
        self.model = "llama-3.3-70b-versatile"

    def route(self, message: str, history: list) -> str:
        prompt = """
        You are a routing agent for a bank.
        Classify the user's message into one of these categories:
        - CUSTOMER_SUPPORT (general questions, hours, contact, FAQs)
        - ACCOUNTS (balance, transactions, money transfer)
        - LOANS_SERVICES (loans, credit cards, cheque books, service requests)
        
        Return ONLY the category name.
        """
        messages = [{"role": "system", "content": prompt}]
        messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0
        )
        
        category = completion.choices[0].message.content.strip().upper()
        
        if "ACCOUNT" in category: return "ACCOUNTS"
        if "LOAN" in category or "SERVICE" in category: return "LOANS_SERVICES"
        return "CUSTOMER_SUPPORT"
