from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import ServiceRequest
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

# Count before
count = db.query(ServiceRequest).count()
print(f"Found {count} service requests.")

if count > 0:
    confirm = input("Are you sure you want to DELETE ALL service requests? (yes/no): ")
    if confirm.lower() == "yes":
        db.query(ServiceRequest).delete()
        db.commit()
        print("All service requests have been deleted.")
    else:
        print("Operation cancelled.")
else:
    print("Nothing to delete.")

db.close()
