from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="Madan1533@", database="LibrarySystem"
    )

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': 
        login_id, password, role = request.form['login_id'], request.form['password'], request.form['role']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if role == 'admin':
            cursor.execute("SELECT * FROM Admins WHERE login_id=%s AND password=%s", (login_id, password))
            user = cursor.fetchone()
            if user:
                session['user_id'], session['user_name'], session['role'] = user['admin_id'], user['name'], 'admin'
                return redirect(url_for('dashboard'))
        else:
            cursor.execute("SELECT * FROM Members WHERE email=%s AND password=%s", (login_id, password))
            user = cursor.fetchone()
            if user:
                if user.get('status') == 'Blocked': return "Your account is Blocked."
                session['user_id'], session['user_name'], session['role'] = user['member_id'], user['name'], 'member'
                return redirect(url_for('dashboard'))
        flash("Invalid Credentials!", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM FullInventory")
    books = cursor.fetchall()

    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM DetailedTransactions ORDER BY issue_date DESC")
        trans = cursor.fetchall()
        cursor.execute("SELECT * FROM Members")
        members = cursor.fetchall()
        cursor.execute("SELECT * FROM Authors")
        authors = cursor.fetchall()
        
        # Calculate TOTAL Library Value
        cursor.execute("SELECT SUM(price) as total_val FROM Books")
        lib_value = cursor.fetchone()['total_val']
        return render_template('admin.html', books=books, transactions=trans, members=members, authors=authors, total_lib_val=lib_value)
    else:
        cursor.execute("SELECT * FROM Members WHERE member_id = %s", (session['user_id'],))
        member_info = cursor.fetchone()
        
        cursor.execute("""
            SELECT b.* FROM FullInventory b 
            JOIN Transactions t ON b.book_id = t.book_id 
            WHERE t.member_id = %s AND t.return_date IS NULL
        """, (session['user_id'],))
        my_books = cursor.fetchall()
        
        # Calculate Total Price of My Issued Books
        cursor.execute("""
            SELECT SUM(b.price) as my_total FROM Books b 
            JOIN Transactions t ON b.book_id = t.book_id 
            WHERE t.member_id = %s AND t.return_date IS NULL
        """, (session['user_id'],))
        total_price = cursor.fetchone()['my_total'] or 0
        
        return render_template('member.html', books=books, my_books=my_books, info=member_info, my_total=total_price)

@app.route('/issue_book/<int:book_id>')
def issue_book(book_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('IssueBook', [book_id, session['user_id']])
        conn.commit()
        flash("Book Issued Successfully!", "success")
    except mysql.connector.Error as err: flash(f"Error: {err.msg}", "danger")
    finally: conn.close()
    return redirect(url_for('dashboard'))

@app.route('/return_book/<int:book_id>')
def return_book(book_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('ReturnBook', [book_id, session['user_id']])
        conn.commit()
        flash("Book Returned Successfully!", "success")
    except mysql.connector.Error as err: flash(f"Error: {err.msg}", "danger")
    finally: conn.close()
    return redirect(url_for('dashboard'))

@app.route('/add_book', methods=['POST'])
def add_book():
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    title, author_id, place, price, copies = request.form['title'], request.form['author_id'], request.form['place'], request.form['price'], request.form['copies']
    img_name = 'default_book.png'
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            img_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Books (title, author_id, place, status, image, price, copies) VALUES (%s, %s, %s, 'Available', %s, %s, %s)", (title, author_id, place, img_name, price, copies))
    conn.commit()
    return redirect(url_for('dashboard'))

@app.route('/update_copies/<int:id>', methods=['POST'])
def update_copies(id):
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    new_copies = request.form['copies']
    conn = get_db_connection()
    cursor = conn.cursor()
    # Update copies and also reset status to Available if copies > 0
    cursor.execute("UPDATE Books SET copies = %s, status = CASE WHEN %s > 0 THEN 'Available' ELSE 'Issued' END WHERE book_id = %s", (new_copies, new_copies, id))
    conn.commit()
    flash("Copies updated successfully!", "success")
    return redirect(url_for('dashboard'))

@app.route('/add_member', methods=['POST'])
def add_member():
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    name, email, password = request.form['name'], request.form['email'], request.form['password']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Members (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        flash("Member Registered Successfully!", "success")
    except mysql.connector.Error as err:
        flash(f"Error: {err.msg}", "danger")
    finally: conn.close()
    return redirect(url_for('dashboard'))

@app.route('/edit_member/<int:id>', methods=['POST'])
def edit_member(id):
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    name, email, password = request.form['name'], request.form['email'], request.form['password']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Members SET name=%s, email=%s, password=%s WHERE member_id=%s", (name, email, password, id))
        conn.commit()
        flash("Member Details Updated!", "success")
    except mysql.connector.Error as err:
        flash(f"Error: {err.msg}", "danger")
    finally: conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_member/<int:id>')
def delete_member(id):
    if session.get('role') != 'admin': return redirect(url_for('dashboard'))
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Members WHERE member_id=%s", (id,))
        conn.commit()
        flash("Member Deleted!", "warning")
    except mysql.connector.Error as err:
        flash(f"Error: {err.msg}", "danger")
    finally: conn.close()
    return redirect(url_for('dashboard'))

@app.route('/stats')
def stats():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. SET OPERATIONS (UNION) - Combined User Directory
    cursor.execute("""
        SELECT name, phone_no as contact, 'Admin' as role FROM admins
        UNION
        SELECT name, mobile_no as contact, 'Member' as role FROM members
    """)
    user_directory = cursor.fetchall()

    # 2. SET OPERATIONS (EXCEPT) - Books NEVER issued
    cursor.execute("""
        SELECT title FROM books
        EXCEPT
        SELECT b.title FROM books b JOIN transactions t ON b.book_id = t.book_id
    """)
    never_issued = cursor.fetchall()

    # 3. ADVANCED AGGREGATION (GROUP BY + HAVING) - Active Authors
    cursor.execute("""
        SELECT author_name, COUNT(*) as book_count
        FROM FullInventory
        GROUP BY author_name
        HAVING book_count >= 2
    """)
    top_authors = cursor.fetchall()

    # 3b. CATEGORY ANALYTICS (GROUP BY + HAVING)
    cursor.execute("""
        SELECT category_name, COUNT(*) as total_books, SUM(price) as category_value
        FROM FullInventory
        GROUP BY category_name
        HAVING total_books > 0
    """)
    category_stats = cursor.fetchall()

    # 3c. MEMBER ACTIVITY (GROUP BY + HAVING)
    cursor.execute("""
        SELECT m.name, COUNT(t.trans_id) as issue_count
        FROM members m
        JOIN transactions t ON m.member_id = t.member_id
        GROUP BY m.member_id
        HAVING issue_count >= 1
    """)
    active_members = cursor.fetchall()

    # 4. NESTED SUBQUERY - Award Winning Authors
    cursor.execute("""
        SELECT title, author_name 
        FROM FullInventory 
        WHERE author_name IN (SELECT AuthorName FROM awardwinners)
    """)
    award_books = cursor.fetchall()

    # 5. CORRELATED SUBQUERY - Premium Books (Price > Avg in Category)
    cursor.execute("""
        SELECT b1.title, b1.price, b1.category_name
        FROM FullInventory b1
        WHERE b1.price > (
            SELECT AVG(b2.price) 
            FROM books b2 
            WHERE b2.category_id = (SELECT category_id FROM categories WHERE category_name = b1.category_name)
        )
    """)
    premium_books = cursor.fetchall()

    # 6. PL/SQL: Call Procedure
    cursor.callproc('GenerateMonthlyReport')
    # Fetch result from the SELECT statement inside procedure
    results = []
    for result in cursor.stored_results():
        results.append(result.fetchall())
    author_report = results[0] if results else []

    return render_template('stats.html', 
        user_directory=user_directory, 
        never_issued=never_issued,
        top_authors=top_authors,
        category_stats=category_stats,
        active_members=active_members,
        award_books=award_books,
        premium_books=premium_books,
        author_report=author_report
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
