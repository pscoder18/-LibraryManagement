import mysql.connector

def upgrade_mysql_advanced():
    config = {
        'host': "localhost",
        'user': "root",
        'password': "Madan1533@",
        'database': "LibrarySystem"
    }
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        print("--- 1. UPGRADING PROCEDURES (ACID & LOCKING) ---")
        
        # Advanced IssueBook with ACID logic
        cursor.execute("DROP PROCEDURE IF EXISTS IssueBook")
        cursor.execute("""
            CREATE PROCEDURE IssueBook(IN p_book_id INT, IN p_member_id INT)
            BEGIN
                DECLARE v_copies INT DEFAULT 0;
                DECLARE v_status VARCHAR(20);
                DECLARE v_mem_stat VARCHAR(20);
                
                -- Error Handler for ATOMICITY
                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    ROLLBACK;
                    RESIGNAL;
                END;

                SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
                START TRANSACTION;

                -- Lock member row for CONCURRENCY CONTROL
                SELECT status INTO v_mem_stat FROM members WHERE member_id = p_member_id FOR UPDATE;
                IF v_mem_stat != 'Active' THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: Member is Blocked.';
                END IF;

                -- Lock book row and check CONSISTENCY
                SELECT copies, status INTO v_copies, v_status FROM books WHERE book_id = p_book_id FOR UPDATE;
                IF v_copies <= 0 THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: No copies available.';
                END IF;

                -- Perform the operations
                INSERT INTO transactions (book_id, member_id, issue_date) VALUES (p_book_id, p_member_id, CURDATE());
                UPDATE books SET copies = copies - 1 WHERE book_id = p_book_id;
                
                COMMIT; -- DURABILITY
            END
        """)

        # Advanced ReturnBook
        cursor.execute("DROP PROCEDURE IF EXISTS ReturnBook")
        cursor.execute("""
            CREATE PROCEDURE ReturnBook(IN p_book_id INT, IN p_member_id INT)
            BEGIN
                DECLARE v_trans_id INT DEFAULT NULL;
                DECLARE EXIT HANDLER FOR SQLEXCEPTION
                BEGIN
                    ROLLBACK;
                    RESIGNAL;
                END;

                START TRANSACTION;
                
                -- Find active issue
                SELECT trans_id INTO v_trans_id FROM transactions 
                WHERE book_id = p_book_id AND member_id = p_member_id AND return_date IS NULL FOR UPDATE;
                
                IF v_trans_id IS NULL THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'ERROR: No active issue found.';
                END IF;

                UPDATE transactions SET return_date = CURDATE() WHERE trans_id = v_trans_id;
                UPDATE books SET copies = copies + 1 WHERE book_id = p_book_id;
                
                COMMIT;
            END
        """)

        print("--- 2. ADDING TRIGGERS ---")
        
        # Trigger for automatic status update
        cursor.execute("DROP TRIGGER IF EXISTS BeforeBookUpdate")
        cursor.execute("""
            CREATE TRIGGER BeforeBookUpdate
            BEFORE UPDATE ON books
            FOR EACH ROW BEGIN
                IF NEW.copies = 0 THEN
                    SET NEW.status = 'Out of Stock';
                ELSEIF NEW.copies > 0 AND OLD.copies = 0 THEN
                    SET NEW.status = 'Available';
                END IF;
            END
        """)

        # Trigger for Admin security
        cursor.execute("DROP TRIGGER IF EXISTS PreventAdminDeletion")
        cursor.execute("""
            CREATE TRIGGER PreventAdminDeletion
            BEFORE DELETE ON admins
            FOR EACH ROW BEGIN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Security Violation: Admin accounts cannot be deleted.';
            END
        """)

        print("--- 3. ADDING CURSOR PROCEDURE ---")
        
        # Cursor for heavy borrowers
        cursor.execute("DROP PROCEDURE IF EXISTS ReportHeavyBorrowers")
        cursor.execute("""
            CREATE PROCEDURE ReportHeavyBorrowers()
            BEGIN
                DECLARE done INT DEFAULT FALSE;
                DECLARE v_name VARCHAR(100);
                DECLARE v_count INT;
                DECLARE cur_borrowers CURSOR FOR 
                    SELECT m.name, COUNT(t.trans_id) 
                    FROM members m 
                    JOIN transactions t ON m.member_id = t.member_id 
                    GROUP BY m.member_id HAVING COUNT(t.trans_id) > 3;
                DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
                
                OPEN cur_borrowers;
                read_loop: LOOP
                    FETCH cur_borrowers INTO v_name, v_count;
                    IF done THEN LEAVE read_loop; END IF;
                    SELECT CONCAT(v_name, ' is a heavy borrower with ', v_count, ' books.') AS Report;
                END LOOP;
                CLOSE cur_borrowers;
            END
        """)

        conn.commit()
        print("✅ DATABASE SUCCESSFULLY UPGRADED TO MATCH YOUR REPORT!")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    upgrade_mysql_advanced()
