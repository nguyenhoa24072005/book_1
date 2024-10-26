from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from datetime import date
import logging

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Kết nối đến cơ sở dữ liệu MySQL
def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Enter your actual password if you have one
            database="library_db"  # Ensure this matches the created database
        )
        return connection
    except Error as e:
        logging.error(f"Error connecting to MySQL Platform: {e}")
        return None

# Trang chủ, hiển thị danh sách thành viên và sách
@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('index.html', members=members, books=books)

# Đăng ký thành viên mới
@app.route('/register_member', methods=['GET', 'POST'])
def register_member():
    if request.method == 'POST':
        name = request.form['name']
        birthdate = request.form['birthdate']
        address = request.form['address']
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO members (name, dob, address) VALUES (%s, %s, %s)", 
                       (name, birthdate, address))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Member registered successfully!", "success")
        return redirect(url_for('index'))
    
    return render_template("register_member.html")

# Thêm sách mới vào thư viện
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", 
                       (title, author))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("Book added successfully!", "success")
        return redirect(url_for('index'))
    
    return render_template("add_book.html")

# Trang mượn sách
@app.route('/borrow_book_page', methods=['GET'])
def borrow_book_page():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    
    cursor.execute("SELECT * FROM books WHERE status = 'available'")
    available_books = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('borrow_book.html', members=members, available_books=available_books)

# Trang trả sách
@app.route('/return_book_page', methods=['GET'])
def return_book_page():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT t.id, m.name AS member_name, b.title AS book_title, t.borrow_date
        FROM transactions t
        JOIN members m ON t.member_id = m.id
        JOIN books b ON t.book_id = b.id
        WHERE t.status = 'Đang mượn'
    """)
    transactions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('return_book.html', transactions=transactions)


# Xem báo cáo giao dịch
@app.route('/report')
def report():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""  
        SELECT t.id, m.name AS member_name, m.dob, m.address, b.title AS book_title, 
               t.borrow_date, t.return_date, t.status 
        FROM transactions t  
        JOIN members m ON t.member_id = m.id  
        JOIN books b ON t.book_id = b.id  
        ORDER BY t.borrow_date DESC  
    """)
    transactions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("report.html", transactions=transactions)


# Xem báo cáo giao dịch của thành viên
@app.route('/members_report')
def members_report():
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT m.id, m.name, m.dob, m.address, b.title,
               t.borrow_date, t.return_date, t.status
        FROM transactions t
        JOIN members m ON t.member_id = m.id
        JOIN books b ON t.book_id = b.id
        ORDER BY t.borrow_date DESC
    """)
    members_report = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("members_report.html", members_report=members_report)


# Chạy ứng dụng Flask
if __name__ == '__main__':
    app.run(debug=True)
