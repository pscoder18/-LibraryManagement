import mysql.connector
import os
import urllib.request
import urllib.parse
import json
import time

# Database Configuration
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "Madan1533@",
    'database': "LibrarySystem"
}

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_real_covers():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # Fetch all books
        cursor.execute("SELECT book_id, title FROM Books")
        books = cursor.fetchall()

        print(f"Attempting to find real covers for {len(books)} books...")

        for book in books:
            book_id = book['book_id']
            title = book['title']
            
            # 1. Search Open Library for the book title
            search_query = urllib.parse.quote(title)
            search_url = f"https://openlibrary.org/search.json?title={search_query}"
            
            try:
                print(f"Searching for: {title}...", end=" ", flush=True)
                with urllib.request.urlopen(search_url) as response:
                    data = json.loads(response.read().decode())
                
                if data['docs'] and 'cover_i' in data['docs'][0]:
                    cover_id = data['docs'][0]['cover_i']
                    cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
                    
                    # 2. Download the actual cover
                    img_filename = f"real_cover_{book_id}.jpg"
                    save_path = os.path.join(UPLOAD_FOLDER, img_filename)
                    
                    urllib.request.urlretrieve(cover_url, save_path)
                    
                    # 3. Update the database
                    cursor.execute("UPDATE Books SET image = %s WHERE book_id = %s", (img_filename, book_id))
                    print(f"✅ Found and updated!")
                else:
                    print(f"❌ No cover found on Open Library.")
                
                # Sleep briefly to be polite to the API
                time.sleep(1)

            except Exception as e:
                print(f"⚠️ Error searching for {title}: {e}")

        conn.commit()
        print("\nFinished updating real covers!")

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    get_real_covers()
