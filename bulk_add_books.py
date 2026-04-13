import mysql.connector
import os
import urllib.request
import random
from database_config import get_db_config

# Database Configuration
DB_CONFIG = get_db_config()

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# List of 20 Books to Add
books_data = [
    ("The Great Gatsby", "F. Scott Fitzgerald", "Shelf A-1"),
    ("To Kill a Mockingbird", "Harper Lee", "Shelf A-2"),
    ("1984", "George Orwell", "Shelf A-3"),
    ("Pride and Prejudice", "Jane Austen", "Shelf B-1"),
    ("The Hobbit", "J.R.R. Tolkien", "Shelf B-2"),
    ("Fahrenheit 451", "Ray Bradbury", "Shelf B-3"),
    ("The Catcher in the Rye", "J.D. Salinger", "Shelf C-1"),
    ("The Alchemist", "Paulo Coelho", "Shelf C-2"),
    ("Brave New World", "Aldous Huxley", "Shelf C-3"),
    ("The Lord of the Rings", "J.R.R. Tolkien", "Shelf B-2"),
    ("Crime and Punishment", "Fyodor Dostoevsky", "Shelf D-1"),
    ("The Chronicles of Narnia", "C.S. Lewis", "Shelf D-2"),
    ("The Book Thief", "Markus Zusak", "Shelf D-3"),
    ("Moby Dick", "Herman Melville", "Shelf E-1"),
    ("War and Peace", "Leo Tolstoy", "Shelf E-2"),
    ("The Odyssey", "Homer", "Shelf E-3"),
    ("Ulysses", "James Joyce", "Shelf F-1"),
    ("The Divine Comedy", "Dante Alighieri", "Shelf F-2"),
    ("Gulliver's Travels", "Jonathan Swift", "Shelf F-3"),
    ("Great Expectations", "Charles Dickens", "Shelf G-1")
]

def seed_library():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        print("Starting bulk book import...")

        for title, author_name, place in books_data:
            # 1. Ensure Author exists and get ID
            cursor.execute("SELECT author_id FROM Authors WHERE author_name = %s", (author_name,))
            author = cursor.fetchone()
            
            if author:
                author_id = author['author_id']
            else:
                cursor.execute("INSERT INTO Authors (author_name) VALUES (%s)", (author_name,))
                author_id = cursor.lastrowid
                print(f"Added Author: {author_name}")

            # 2. Check if book already exists
            cursor.execute("SELECT book_id FROM Books WHERE title = %s", (title,))
            if cursor.fetchone():
                print(f"Skipping: '{title}' already exists.")
                continue

            # 3. Generate Image Filename and Download
            # Using random seed to get different high-quality placeholder images
            image_id = random.randint(1, 1000)
            img_filename = f"cover_{image_id}.jpg"
            save_path = os.path.join(UPLOAD_FOLDER, img_filename)
            image_url = f"https://picsum.photos/seed/{image_id}/300/450"

            try:
                urllib.request.urlretrieve(image_url, save_path)
                
                # 4. Insert Book into Database
                cursor.execute(
                    "INSERT INTO Books (title, author_id, place, status, image) VALUES (%s, %s, %s, 'Available', %s)",
                    (title, author_id, place, img_filename)
                )
                print(f"✅ Added: {title} ({author_name}) at {place}")
            except Exception as e:
                print(f"❌ Failed to download image for {title}: {e}")

        conn.commit()
        print("\n--- Bulk Import Complete! ---")
        print(f"Go to your dashboard to see your 20 new books.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed_library()
