import sqlite3
import os

db_path = 'e:/Gemaura/instance/gemaura.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE orders ADD COLUMN refund_status VARCHAR(50) DEFAULT 'na'")
    print("Added refund_status column")
except sqlite3.OperationalError as e:
    print(f"refund_status error: {e}")

try:
    cursor.execute("ALTER TABLE orders ADD COLUMN cancel_reason VARCHAR(255)")
    print("Added cancel_reason column")
except sqlite3.OperationalError as e:
    print(f"cancel_reason error: {e}")

try:
    cursor.execute("ALTER TABLE orders ADD COLUMN cancel_date DATETIME")
    print("Added cancel_date column")
except sqlite3.OperationalError as e:
    print(f"cancel_date error: {e}")

conn.commit()
conn.close()
print("Migration completed successfully.")
