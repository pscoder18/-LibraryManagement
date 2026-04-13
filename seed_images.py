import mysql.connector
import os
import urllib.request

# Configuration
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "Madan1533@",
    'database': "LibrarySystem"
}

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def update_book_images():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Get all books without custom images
        cursor.execute("SELECT book_id, title FROM Books WHERE image = 'default_book.png' OR image IS NULL")
        books = cursor.fetchall()

        if not books:
            print("All books already have custom images.")
            return

        print(f"Assigning placeholder images for {len(books)} books...")

        for book in books:
            book_id = book['book_id']
            # Generate a unique placeholder image filename
            filename = f"book_{book_id}.jpg"
            save_path = os.path.join(UPLOAD_FOLDER, filename)

            # Download a placeholder image from Lorem Picsum or similar
            # Use book_id to get a consistent unique image
            image_url = f"https://picsum.photos/seed/{book_id}/220/280"
            
            try:
                urllib.request.urlretrieve(image_url, save_path)
                # Update database
                cursor.execute("UPDATE Books SET image = %s WHERE book_id = %s", (filename, book_id))
                print(f"Updated Book ID {book_id}: {filename}")
            except Exception as e:
                print(f"Failed to download image for Book ID {book_id}: {e}")

        conn.commit()
        print("\nAll available books updated successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_book_images()
