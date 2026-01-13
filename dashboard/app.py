import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import sys
import os
import altair as alt

# --- Configuration & Setup ---
st.set_page_config(
    page_title="NeoBank Operations",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robust Database Connection
try:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(PROJECT_ROOT, "app.db")
    if os.name == 'nt':
        DB_PATH = DB_PATH.replace('\\', '/')
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
except Exception as e:
    st.error(f"Failed to connect to database: {e}")
    st.stop()

# --- Custom CSS ---
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-label { font-size: 0.9rem; color: #666; }
    .metric-value { font-size: 2rem; font-weight: bold; color: #333; }
    .stApp { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
</style>
""", unsafe_allow_html=True)

# --- Utilities ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Main App ---
def main():
    # Import models explicitly here to avoid import errors if path varies
    sys.path.append(PROJECT_ROOT)
    from backend.models import Transaction, ServiceRequest, User, Account

    db = next(get_db())

    # Sidebar
    with st.sidebar:
        st.header("🏦 NeoBank Internal")
        st.markdown("---")
        nav = st.radio("Navigation", ["Overview", "Transactions", "Service Requests"])
        st.markdown("---")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        st.caption("v2.0.0 | Admin Panel")

    # Fetch Common Data
    total_customers = db.query(User).count()
    total_balance = db.query(func.sum(Account.balance)).scalar() or 0.0
    pending_requests = db.query(ServiceRequest).filter(ServiceRequest.status == "Under Review").count()
    
    # --- PAGE: OVERVIEW ---
    if nav == "Overview":
        st.title("📊 Operational Overview")
        
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", f"{total_customers}", "+2 this week")
        col2.metric("Total Deposits", f"${total_balance:,.2f}", "12% growth")
        col3.metric("Pending Approvals", f"{pending_requests}", delta=f"{pending_requests} pending", delta_color="inverse")
        col4.metric("System Status", "Online", delta="Stable")

        st.markdown("### Financial Pulse")
        
        # Transaction Query for Charts
        tx_query = db.query(Transaction).all()
        if tx_query:
            data = [{"Amount": t.amount, "Type": t.transaction_type, "Date": t.timestamp} for t in tx_query]
            df = pd.DataFrame(data)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Transaction Volume by Type**")
                chart = alt.Chart(df).mark_bar().encode(
                    x='Type',
                    y='sum(Amount)',
                    color='Type'
                )
                st.altair_chart(chart, use_container_width=True)
            
            with c2:
                st.markdown("**Recent Trend**")
                line = alt.Chart(df).mark_line(point=True).encode(
                    x='Date',
                    y='Amount',
                    color='Type'
                )
                st.altair_chart(line, use_container_width=True)
        else:
            st.info("No transaction data available for charts.")

    # --- PAGE: TRANSACTIONS ---
    elif nav == "Transactions":
        st.title("💳 Transaction Explorer")
        
        # Filter
        filter_col1, filter_col2 = st.columns([3, 1])
        search_term = filter_col1.text_input("Search (Description)", placeholder="Coffee, Salary...")
        tx_type_filter = filter_col2.selectbox("Type", ["All", "Credit", "Debit"])
        
        query = db.query(Transaction).join(Account).join(User)
        
        if search_term:
            query = query.filter(Transaction.description.ilike(f"%{search_term}%"))
        if tx_type_filter != "All":
            query = query.filter(Transaction.transaction_type == tx_type_filter)
            
        transactions = query.order_by(Transaction.timestamp.desc()).limit(100).all()
        
        data = []
        for t in transactions:
            data.append({
                "ID": t.id,
                "Customer": t.account.owner.name,
                "Description": t.description,
                "Type": t.transaction_type,
                "Amount": f"${t.amount:,.2f}",
                "Date": t.timestamp.strftime("%Y-%m-%d %H:%M"),
                "Status": t.status
            })
            
        if data:
            st.dataframe(
                pd.DataFrame(data),
                column_config={
                    "Type": st.column_config.TextColumn(
                        "Type",
                        help="Transaction Type",
                        validate="^(Debit|Credit|Transfer)$"
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No transactions found matching criteria.")

    # --- PAGE: SERVICE REQUESTS ---
    elif nav == "Service Requests":
        st.title("📝 Service Request Manager")
        
        st.info("Review and process customer applications below.")
        
        # Split into Pending and Processed
        tabs = st.tabs(["⏳ Pending Review", "✅ Processed"])
        
        with tabs[0]:
            pending = db.query(ServiceRequest).join(User).filter(ServiceRequest.status.in_(["Requested", "Under Review", "Pending"])).all()
            
            if pending:
                for req in pending:
                    with st.expander(f"#{req.id} - {req.service_type} by {req.owner.name}", expanded=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.markdown(f"**Details:**\n{req.details}")
                            st.caption(f"Submitted: {req.timestamp.strftime('%Y-%m-%d %H:%M')}")
                        with c2:
                            st.markdown(f"**Current Status:**\n`{req.status}`")
                        with c3:
                            # Action Buttons
                            if st.button("✅ Approve", key=f"app_{req.id}"):
                                req.status = "Approved"
                                db.commit()
                                st.success(f"Request #{req.id} Approved!")
                                st.rerun()
                                
                            if st.button("❌ Reject", key=f"rej_{req.id}"):
                                req.status = "Rejected"
                                db.commit()
                                st.error(f"Request #{req.id} Rejected.")
                                st.rerun()
            else:
                st.success("🎉 No pending requests! Good job.")
        
        with tabs[1]:
            history = db.query(ServiceRequest).join(User).filter(ServiceRequest.status.in_(["Approved", "Rejected"])).order_by(ServiceRequest.timestamp.desc()).limit(50).all()
            
            if history:
                for req in history:
                    with st.expander(f"{req.timestamp.strftime('%Y-%m-%d')} | {req.service_type} - {req.status}"):
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.write(f"**Customer:** {req.owner.name}")
                            st.write(f"**Details:** {req.details}")
                            st.caption(f"ID: {req.id}")
                        with c2:
                            if st.button("🗑️ Delete", key=f"del_{req.id}"):
                                db.delete(req)
                                db.commit()
                                st.success("Deleted.")
                                st.rerun()
            else:
                st.caption("No history to show.")

if __name__ == "__main__":
    main()
