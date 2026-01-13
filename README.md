# 🏦 Agentic AI Banking System

A chat-based AI banking assistant that handles customer support, account inquiries, and loan services.

## 🏗 System Architecture

- **Frontend**: HTML/JS Chat Interface
- **Backend**: FastAPI (Python)
- **Database**: SQLite (SQLAlchemy)
- **AI Agent**: Google Gemini 1.5 Flash
- **Dashboard**: Streamlit

### Agent Routing
The system uses an **Orchestrator** to classify user intent into three categories:
1.  **Customer Support**: Handles FAQs (Generative).
2.  **Accounts**: Fetches balance and transaction history (Tool Calling).
3.  **Loans & Services**: Submits loan applications and service requests (Tool Calling).

## 🚀 How to Run

### 1. Prerequisites
- Python 3.9+
- A Google Gemini API Key

### 2. Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Set your API Key in `.env`:
    ```
    GEMINI_API_KEY=your_actual_api_key_here
    ```

### 3. Run Backend
Start the FastAPI server:
```bash
uvicorn backend.main:app --reload
```
The API will run at `http://127.0.0.1:8000`.

### 4. Run Dashboard
Start the operations dashboard:
```bash
streamlit run dashboard/app.py
```

### 5. Start Chat
Open `frontend/index.html` in your browser.

## 🧪 Sample Conversations

**User**: What are your working hours?
**Agent**: (Support) Our branches are open Mon-Sat, 9 AM - 5 PM.

**User**: Check my balance.
**Agent**: (Accounts) Your current balance is 5000.0 USD.

**User**: apply for a personal loan of 50000
**Agent**: (Loans) Loan application for 50000 (personal limit) submitted successfully. Reference ID: 1.
