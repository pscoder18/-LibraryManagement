import mysql.connector
from database_config import get_db_config

# Using centrally managed config
DB_CONFIG = get_db_config()

def upgrade_final():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("Finalizing Database Schema...")

        # 1. Create View for Full Inventory
        cursor.execute("""
            CREATE OR REPLACE VIEW FullInventory AS
            SELECT b.book_id, b.title, a.author_name, c.category_name, b.place, b.status, b.image, b.price, b.copies
            FROM Books b
            JOIN Authors a ON b.author_id = a.author_id
            LEFT JOIN Categories c ON b.category_id = c.category_id
        """)
        print("✅ Created View: FullInventory")

        # 2. Create View for Detailed Transactions
        cursor.execute("""
            CREATE OR REPLACE VIEW DetailedTransactions AS
            SELECT t.trans_id, b.title, m.name as member_name, t.issue_date, t.return_date
            FROM Transactions t
            JOIN Books b ON t.book_id = b.book_id
            JOIN Members m ON t.member_id = m.member_id
        """)
        print("✅ Created View: DetailedTransactions")

        # 3. Create Procedure to Issue Book
        cursor.execute("DROP PROCEDURE IF EXISTS IssueBook")
        cursor.execute("""
            CREATE PROCEDURE IssueBook(IN p_book_id INT, IN p_member_id INT)
            BEGIN
                DECLARE v_copies INT;
                SELECT copies INTO v_copies FROM Books WHERE book_id = p_book_id;
                IF v_copies > 0 THEN
                    INSERT INTO Transactions (book_id, member_id, issue_date) VALUES (p_book_id, p_member_id, CURDATE());
                    UPDATE Books SET copies = copies - 1, status = CASE WHEN copies - 1 = 0 THEN 'Issued' ELSE 'Available' END WHERE book_id = p_book_id;
                ELSE
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No copies available for issue.';
                END IF;
            END
        """)
        print("✅ Created Procedure: IssueBook")

        # 4. Create Procedure to Return Book
        cursor.execute("DROP PROCEDURE IF EXISTS ReturnBook")
        cursor.execute("""
            CREATE PROCEDURE ReturnBook(IN p_book_id INT, IN p_member_id INT)
            BEGIN
                UPDATE Transactions SET return_date = CURDATE() WHERE book_id = p_book_id AND member_id = p_member_id AND return_date IS NULL;
                UPDATE Books SET copies = copies + 1, status = 'Available' WHERE book_id = p_book_id;
            END
        """)
        print("✅ Created Procedure: ReturnBook")

        # 5. Create AwardWinners table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AwardWinners (
                AwardID INT AUTO_INCREMENT PRIMARY KEY,
                AuthorName VARCHAR(100) NOT NULL UNIQUE
            )
        """)
        print("✅ Table AwardWinners Created")

        # 6. Insert some winners
        winners = ['George Orwell', 'J.R.R. Tolkien', 'F. Scott Fitzgerald', 'Harper Lee']
        for winner in winners:
            cursor.execute("INSERT IGNORE INTO AwardWinners (AuthorName) VALUES (%s)", (winner,))

        conn.commit()
        print("\n--- Final upgrade successful! ---")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    upgrade_final()
