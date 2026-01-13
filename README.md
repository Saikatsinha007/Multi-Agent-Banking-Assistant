# 🏦 Agentic AI Banking System

A comprehensive, AI-powered banking assistant that combines a chat interface for customer interaction with a powerful backend and an administrative dashboard for operations management.

## 📖 Overview

This project implements a "NeoBank" style system where customers can interact with an AI agent to check accounts, transfer money, apply for loans, and get support. The system uses an **Agentic Architecture** to route user intents to specialized agents.

### Key Features
*   **🤖 Intelligent Chat Agent**: Powered by Google Gemini 1.5 Flash, capable of handling natural language queries.
*   **🛣️ Smart Routing**: An Orchestrator classifies user requests to direct them to the correct specialist agent (Support, Accounts, or Loans).
*   **💳 Core Banking Operations**: Check balances, view transaction history, and detailed mock financial data.
*   **📝 Service Request Management**: Submit loan applications and service requests via chat.
*   **📊 Admin Dashboard**: A real-time Streamlit dashboard for bank staff to view metrics, approve/reject requests, and analyze data.
  
<img width="1371" height="838" alt="Screenshot 2026-01-13 095440" src="https://github.com/user-attachments/assets/09103a77-7a26-45f2-8c9f-56b360097be2" />
<img width="1650" height="743" alt="Screenshot 2026-01-06 160449" src="https://github.com/user-attachments/assets/3a18484e-6532-4bc2-b98b-9fed06d81aad" />

---

## 🏗️ System Architecture

The system is built using a modern decoupled architecture:

```mermaid
graph TD
    User([👤 User]) -->|Chat| Frontend[💻 Frontend (HTML/JS)]
    Staff([👨‍💼 Bank Staff]) -->|Manage| Dashboard[📊 Streamlit Dashboard]
    
    Frontend -->|POST /chat| Backend[🚀 Backend API (FastAPI)]
    
    subgraph "Backend System"
        Backend --> Orchestrator{🧭 Orchestrator}
        Orchestrator -->|General Queries| Support[💬 Support Agent]
        Orchestrator -->|Balance/Txns| Accounts[💰 Accounts Agent]
        Orchestrator -->|Loans/Services| Loans[📝 Loans Agent]
        
        Accounts <--> DB[(🗄️ SQLite Database)]
        Loans <--> DB
    end
    
    Dashboard <--> DB
```

### Component Breakdown
1.  **Frontend**: A lightweight, responsive chat interface built with vanilla HTML/CSS/JavaScript. It maintains chat history and renders Markdown responses.
2.  **Backend (FastAPI)**: The core server handling API requests. It initializes the database, manages the specialized agents, and exposes the `/chat` endpoint.
3.  **Database (SQLite)**: A relational database storing Users, Accounts, Transactions, and Service Requests. It uses SQLAlchemy ORM.
4.  **Dashboard (Streamlit)**: An administrative tool connecting directly to the database to visualize KPIs, transaction logs, and manage service request workflows.

---

## 📂 Project Structure

```text
banking-agent-2/
├── backend/                # FastAPI Application & Logic
│   ├── agents.py           # AI Agents (Support, Accounts, Loans)
│   ├── database.py         # DB Connection & Session
│   ├── main.py             # API Entry Point & Routing
│   ├── models.py           # SQLAlchemy Database Models
│   └── ...
├── dashboard/              # Streamlit Admin Panel
│   └── app.py              # Dashboard logic & UI
├── frontend/               # Customer Facing Chat UI
│   ├── index.html          # Chat Interface
│   └── app.js              # Frontend Logic
├── .env                    # Environment Variables (API Keys)
├── app.db                  # SQLite Database (Auto-generated)
├── requirements.txt        # Python Dependencies
└── README.md               # Project Documentation
```

---

## 🚀 Getting Started

Follow these steps to set up and run the system locally.

### 1️⃣ Prerequisites
*   Python 3.9 or higher installed.
*   A Google Gemini API Key (Get one [here](https://aistudio.google.com/)).

### 2️⃣ Installation

1.  **Clone the repository** (if applicable) or navigate to the project folder.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    *   Create a `.env` file in the root directory.
    *   Add your Gemini API key:
        ```ini
        GEMINI_API_KEY=your_actual_api_key_here
        ```

### 3️⃣ Running the Application

You need to run the Backend, Frontend, and Dashboard in separate terminals.

#### Terminal 1: backend 🚀
Start the FastAPI server. This will also create `app.db` and seed it with initial data if missing.
```bash
uvicorn backend.main:app --reload
```
*   Server runs at: `http://127.0.0.1:8000`
*   API Docs: `http://127.0.0.1:8000/docs`

#### Terminal 2: Dashboard 📊
Launch the admin dashboard.
```bash
streamlit run dashboard/app.py
```
*   Opens automatically in browser at `http://localhost:8501`

#### Terminal 3: Frontend 💻
Serve the static frontend files.
```bash
python -m http.server 8080 --directory frontend
```
*   Open your browser to: `http://localhost:8080`

---

## 🧪 Usage Examples

Once everything is running, go to the **Frontend** (`http://localhost:8080`) and try these prompts:

*   **Customer Support**:
    > "What are your branch opening hours?"
    > "How do I reset my password?"

*   **Account Services**:
    > "What is my current balance?"
    > "Show me my last 5 transactions."

*   **Loans & Services**:
    > "I want to apply for a personal loan of $50,000"
    > "Request new cheque book"

**Checking Results**: After making a request (like a loan application), go to the **Dashboard** (`http://localhost:8501`) under the "Service Requests" tab to see it appear in real-time!

---

## 🛠️ Tech Stack

*   **Language**: Python 3.9+
*   **Web Framework**: FastAPI
*   **Database**: SQLite + SQLAlchemy
*   **AI/LLM**: LangChain + Google Gemini 1.5 Flash
*   **Dashboard**: Streamlit
*   **Frontend**: HTML5, CSS3, JavaScript (Fetch API)

---

## ⚠️ Troubleshooting

1.  **Database Errors**: If you see DB connection errors, try deleting `app.db` and restarting the backend to re-seed data.
2.  **API Key Errors**: Ensure `GEMINI_API_KEY` is set correctly in `.env` and you have quota available.
3.  **CORS Issues**: The backend is configured to allow all origins (`*`) for development ease.
