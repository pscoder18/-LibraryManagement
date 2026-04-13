import mysql.connector

def update_db_for_report():
    config = {
        'host': "localhost",
        'user': "root",
        'password': "Madan1533@",
        'database': "LibrarySystem"
    }
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        # Add 'branch' column to Members if it doesn't exist
        print("Checking if 'branch' column exists in Members...")
        cursor.execute("SHOW COLUMNS FROM Members LIKE 'branch'")
        if not cursor.fetchone():
            print("Adding 'branch' column...")
            cursor.execute("ALTER TABLE Members ADD COLUMN branch VARCHAR(50) DEFAULT 'CSE'")
        
        # Insert/Update Alice Smith for the report queries
        print("Adding sample data for 'Alice Smith'...")
        cursor.execute("""
            INSERT INTO Members (name, email, password, branch) 
            VALUES ('Alice Smith', 'alice@student.srm.edu', '1234', 'CSE')
            ON DUPLICATE KEY UPDATE branch='CSE'
        """)

        # Add a placeholder for ECE branch to make join queries in report meaningful
        cursor.execute("""
            INSERT INTO Members (name, email, password, branch) 
            VALUES ('Bob ECE', 'bob@ece.srm.edu', '1234', 'ECE')
            ON DUPLICATE KEY UPDATE branch='ECE'
        """)

        conn.commit()
        print("✅ Database schema and data are now in sync with your report!")

    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    update_db_for_report()
