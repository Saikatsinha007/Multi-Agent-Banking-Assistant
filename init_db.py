from sqlalchemy import create_engine
from backend.models import Base, User, Account, Transaction, ServiceRequest
import os

# EXACT logic from dashboard/app.py to ensure we hit the same file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(PROJECT_ROOT, "app.db")
if os.name == 'nt':
    DB_PATH = DB_PATH.replace('\\', '/')
    
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"Initializing Database at: {DB_PATH}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)

print("Tables created successfully.")
