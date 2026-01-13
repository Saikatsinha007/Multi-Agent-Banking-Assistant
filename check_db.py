from sqlalchemy import create_engine, inspect
import os

db_path = "app.db"
if not os.path.exists(db_path):
    print("app.db not found in current directory")
else:
    print(f"Checking {os.path.abspath(db_path)}")
    engine = create_engine(f"sqlite:///{db_path}")
    inspector = inspect(engine)
    print("Tables:", inspector.get_table_names())
