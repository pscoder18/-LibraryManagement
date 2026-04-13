import mysql.connector
from database_config import get_db_config

# Using centrally managed config
DB_CONFIG = get_db_config()

def sync_data():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        print("🔄 Syncing Database with Current Reports...")

        # 1. Update Book Status based on Transactions
        cursor.execute("""
            UPDATE Books 
            SET status = 'Issued' 
            WHERE book_id IN (SELECT book_id FROM Transactions WHERE return_date IS NULL)
        """)
        
        cursor.execute("""
            UPDATE Books 
            SET status = 'Available' 
            WHERE book_id NOT IN (SELECT book_id FROM Transactions WHERE return_date IS NULL)
        """)

        # 2. Cleanup orphaned transactions (optional)
        # cursor.execute("DELETE FROM Transactions WHERE book_id NOT IN (SELECT book_id FROM Books)")

        conn.commit()
        print("✅ Database sync complete!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    sync_data()
