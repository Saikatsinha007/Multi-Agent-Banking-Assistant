from sqlalchemy import create_engine, text
import os

db_path = "app.db"
if not os.path.exists(db_path):
    print("app.db not found")
else:
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        print("Users:", conn.execute(text("SELECT COUNT(*) FROM users")).scalar())
        print("Accounts:", conn.execute(text("SELECT COUNT(*) FROM accounts")).scalar())
        print("Transactions:", conn.execute(text("SELECT COUNT(*) FROM transactions")).scalar())
