from database_config import get_db_config
import mysql.connector

config = get_db_config()

def export_database():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        with open('database_summary.txt', 'w', encoding='utf-8') as f:
            f.write("==================================================\n")
            f.write("      LIBRARY SYSTEM DATABASE COMPLETE REPORT      \n")
            f.write("==================================================\n\n")

            # Get list of all tables and views
            cursor.execute("SHOW FULL TABLES")
            items = cursor.fetchall()
            
            for item in items:
                name = list(item.values())[0]
                is_view = list(item.values())[1] == 'VIEW'
                
                f.write(f"--- {'VIEW' if is_view else 'TABLE'}: {name} ---\n\n")
                
                # 1. Get CREATE Query
                if is_view:
                    cursor.execute(f"SHOW CREATE VIEW `{name}`")
                    res = cursor.fetchone()
                    f.write("CREATE QUERY:\n")
                    f.write(res['Create View'] + ";\n\n")
                else:
                    cursor.execute(f"SHOW CREATE TABLE `{name}`")
                    res = cursor.fetchone()
                    f.write("CREATE QUERY:\n")
                    f.write(res['Create Table'] + ";\n\n")
                
                # 2. Get Data Output
                f.write("TABLE DATA OUTPUT:\n")
                cursor.execute(f"SELECT * FROM `{name}`")
                rows = cursor.fetchall()
                
                if not rows:
                    f.write("(No data found in this table)\n")
                else:
                    # Header
                    headers = rows[0].keys()
                    f.write(" | ".join(headers) + "\n")
                    f.write("-" * 50 + "\n")
                    # Rows
                    for row in rows:
                        f.write(" | ".join(str(val) for val in row.values()) + "\n")
                
                f.write("\n" + "="*50 + "\n\n")

            print("✅ Database summary exported to 'database_summary.txt'")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    export_database()
