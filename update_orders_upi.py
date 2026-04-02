import sqlite3
import os

db_path = r'e:\Gemaura\instance\gemaura.db'

def update_db():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Columns to add to 'orders' table
    order_columns = [
        ('upi_id', 'VARCHAR(100)'),
        ('payment_status', "VARCHAR(50) DEFAULT 'pending'")
    ]

    cursor.execute("PRAGMA table_info(orders)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    for col_name, col_def in order_columns:
        if col_name not in existing_columns:
            print(f"Adding column '{col_name}' to 'orders' table...")
            try:
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}")
                print(f"Successfully added '{col_name}'.")
            except Exception as e:
                print(f"Error adding '{col_name}': {e}")
        else:
            print(f"Column '{col_name}' already exists.")

    conn.commit()
    conn.close()
    print("Database sync complete.")

if __name__ == "__main__":
    update_db()
