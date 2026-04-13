import mysql.connector
import os
from database_config import get_db_config

# Using centrally managed config
DB_CONFIG = get_db_config()

def update_covers():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        print("Updating Book Covers...")

        # Manually updating some famous book covers
        covers = {
            "1984": "1984.jpg",
            "Harry Potter and the Philosopher's Stone": "harry_potter.jpg",
            "The Great Gatsby": "gatsby.jpg",
            "The Hobbit": "hobbit.jpg"
        }

        for title, filename in covers.items():
            # Check if image exists in static/uploads
            if os.path.exists(os.path.join('static/uploads', filename)):
                cursor.execute("UPDATE Books SET image = %s WHERE title = %s", (filename, title))
                print(f"✅ Updated: {title} -> {filename}")
            else:
                print(f"⚠️ Skipping: {filename} not found in uploads folder.")

        conn.commit()
        print("\nCover update process finished.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_covers()
