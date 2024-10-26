import mysql.connector  
from mysql.connector import Error  
import logging  

def get_db_connection():  
    try:  
        connection = mysql.connector.connect(  
            host="localhost",  
            user="root",  
            password="",  # Nhập mật khẩu nếu có  
            database="library_db"  
        )  
        return connection  
    except Error as e:  
        logging.error(f"Error connecting to MySQL Platform: {e}")  
        return None  

def fetch_transactions(member_id):  
    connection = get_db_connection()  
    if connection is None:  
        return []  # Trả về danh sách rỗng nếu kết nối thất bại  
    
    transactions = []  
    cursor = None  # Khởi tạo con trỏ  
    try:  
        cursor = connection.cursor(dictionary=True)  # Trả về kết quả dưới dạng từ điển
        query = """  
        SELECT   
            t.id AS transaction_id,  
            m.id AS member_id,  
            m.name AS member_name,  
            b.title AS book_title,  
            t.borrow_date,  
            t.return_date,  
            t.status  
        FROM   
            transactions t  
        JOIN   
            members m ON t.member_id = m.id  
        JOIN   
            books b ON t.book_id = b.id  
        WHERE   
            m.id = %s;  
        """  
        
        cursor.execute(query, (member_id,))  
        transactions = cursor.fetchall()  

    except Error as e:  
        logging.error(f"Error fetching transactions: {e}")  

    finally:  
        if cursor:  
            cursor.close()  # Chỉ đóng nếu con trỏ tồn tại  
        if connection:  
            connection.close()  # Đóng kết nối  

    return transactions  # Trả về danh sách giao dịch
