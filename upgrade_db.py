import mysql.connector
from database_config import get_db_config

# Using centrally managed config
DB_CONFIG = get_db_config()

def upgrade_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Updating Database Schema...")

        # 1. Add Price Column to Books
        try:
            cursor.execute("ALTER TABLE Books ADD COLUMN price DECIMAL(10,2) DEFAULT 0.00")
            print("✅ Column 'price' added to Books")
        except: print("⚠️ Column 'price' already exists")

        # 2. Add Copies Column to Books
        try:
            cursor.execute("ALTER TABLE Books ADD COLUMN copies INT DEFAULT 1")
            print("✅ Column 'copies' added to Books")
        except: print("⚠️ Column 'copies' already exists")

        # 3. Create Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Categories (
                category_id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(50) NOT NULL UNIQUE
            )
        """)
        print("✅ Categories Table Created")

        # 4. Add Category Foreign Key to Books
        try:
            cursor.execute("ALTER TABLE Books ADD COLUMN category_id INT")
            cursor.execute("ALTER TABLE Books ADD FOREIGN KEY (category_id) REFERENCES Categories(category_id)")
            print("✅ Foreign Key category_id added to Books")
        except: print("⚠️ Category reference already exists")

        # 5. Insert Default Categories
        categories = ['Classic', 'Fantasy', 'Sci-Fi', 'Dystopian', 'Romance', 'Mystery']
        for cat in categories:
            cursor.execute("INSERT IGNORE INTO Categories (category_name) VALUES (%s)", (cat,))
        
        # 6. Randomly assign categories to books
        cursor.execute("SELECT book_id FROM Books")
        books = cursor.fetchall()
        for book in books:
            import random
            cursor.execute("UPDATE Books SET category_id = %s WHERE book_id = %s", (random.randint(1, len(categories)), book[0]))

        conn.commit()
        print("\n--- Database upgrade successful! ---")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    upgrade_database()
