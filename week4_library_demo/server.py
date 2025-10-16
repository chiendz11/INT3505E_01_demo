from pyngrok import ngrok
import json
import hashlib
import psycopg2
from flask import Flask, make_response, request, jsonify
from contextlib import contextmanager

app = Flask(__name__)

print("Starting server...")

# ==============================
# CẤU HÌNH KẾT NỐI DATABASE
# ==============================
# FIX LỖI XÁC THỰC MẬT KHẨU: 
# Chúng ta quay lại sử dụng dictionary config để truyền mật khẩu gốc (không mã hóa) 
# trực tiếp. Điều này giúp psycopg2 tránh mọi lỗi phân tích URL do ký tự đặc biệt.
DB_CONFIG = {
    "host": "db.kmsqyluflbifzochdqbn.supabase.co",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "Bop29042@@5" 
}

# ==============================
# DB CONNECTION MANAGER
# ==============================
@contextmanager
def get_db_connection():
    """Context manager để kết nối và đảm bảo kết nối được đóng (close)"""
    conn = None
    try:
        # Sử dụng DB_CONFIG dictionary
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        if conn:
            conn.rollback()
        # Vẫn raise exception để Flask biết request bị lỗi
        raise
    finally:
        if conn:
            conn.close()

# ==============================
# Helper: tạo ETag
# ==============================
def generate_etag(data):
    """Tạo ETag dựa trên nội dung JSON"""
    # Đảm bảo dữ liệu là JSON string đã sắp xếp để ETag luôn nhất quán
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_str.encode("utf-8")).hexdigest()

def row_to_dict(cursor, row):
    """Chuyển đổi kết quả truy vấn thành dictionary"""
    if row is None:
        return None
    cols = [col[0] for col in cursor.description]
    return dict(zip(cols, row))

def add_hateoas_book(book):
    """Thêm link HATEOAS cho resource Book"""
    BASE_URL = request.url_root.strip('/') # Sử dụng request.url_root để linh hoạt hơn
    book['links'] = [
        {"rel": "self", "href": f"{BASE_URL}/books/{book['id']}", "method": "GET"},
        {"rel": "update", "href": f"{BASE_URL}/books/{book['id']}", "method": "PUT"},
        {"rel": "delete", "href": f"{BASE_URL}/books/{book['id']}", "method": "DELETE"},
        {"rel": "borrow", "href": f"{BASE_URL}/transactions", "method": "POST"}
    ]
    return book

# ==============================
# Book API - Đã kết nối DB
# ==============================
@app.route('/books', methods=['GET'])
def list_books():
    """Lấy danh sách tất cả sách, có thể lọc theo tác giả"""
    author_filter = request.args.get('author')
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            sql = "SELECT id, title, author, available_copies FROM BOOKS"
            params = []
            
            if author_filter:
                sql += " WHERE LOWER(author) = LOWER(%s)"
                params.append(author_filter)

            cur.execute(sql, params)
            
            # Chuyển kết quả sang dạng list of dicts
            result = [row_to_dict(cur, row) for row in cur.fetchall()]

            # 1. TẠO ETag từ dữ liệu DB
            etag = generate_etag(result)
            
            # 2. KIỂM TRA ETag CACHE
            if request.headers.get('If-None-Match') == etag:
                return '', 304  # Dữ liệu không thay đổi

            # 3. TRẢ VỀ RESPONSE 200 MỚI
            response = make_response(jsonify(result), 200)
            response.headers['Cache-Control'] = 'public, max-age=60'
            response.headers['Content-Type'] = 'application/json'
            response.headers['ETag'] = etag
            return response


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, author, available_copies FROM BOOKS WHERE id = %s", (book_id,))
            book = row_to_dict(cur, cur.fetchone())

            if not book:
                return jsonify({"error": "Book not found"}), 404

            book = add_hateoas_book(book)
            etag = generate_etag(book)
            
            if request.headers.get('If-None-Match') == etag:
                return '', 304

            response = make_response(jsonify(book), 200)
            response.headers['Content-Type'] = 'application/json'
            response.headers['ETag'] = etag
            response.headers['Cache-Control'] = 'public, max-age=120'
            return response


@app.route('/books', methods=['POST'])
def create_book():
    data = request.json
    if not data or not all(k in data for k in ('title', 'author', 'available_copies')):
        return jsonify({"error": "Invalid input"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                # INSERT sách mới và trả về ID được tạo
                sql = "INSERT INTO BOOKS (title, author, available_copies) VALUES (%s, %s, %s) RETURNING id"
                cur.execute(sql, (data['title'], data['author'], data['available_copies']))
                book_id = cur.fetchone()[0]
                conn.commit()
                return jsonify({"message": "Book created", "book_id": book_id}), 201
            except Exception as e:
                conn.rollback()
                print(f"Error creating book: {e}")
                return jsonify({"error": "Database error while creating book"}), 500


@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    if not data or not all(k in data for k in ('title', 'author', 'available_copies')):
        return jsonify({"error": "Invalid input"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                sql = """
                    UPDATE BOOKS SET 
                        title = %s, author = %s, available_copies = %s 
                    WHERE id = %s
                """
                cur.execute(sql, (data['title'], data['author'], data['available_copies'], book_id))
                
                if cur.rowcount == 0:
                    return jsonify({"error": "Book not found"}), 404
                
                conn.commit()
                return jsonify({"message": "Book updated successfully"}), 200
            except Exception as e:
                conn.rollback()
                print(f"Error updating book: {e}")
                return jsonify({"error": "Database error while updating book"}), 500


@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("DELETE FROM BOOKS WHERE id = %s", (book_id,))
                
                if cur.rowcount == 0:
                    return jsonify({"error": "Book not found"}), 404
                
                conn.commit()
                return '', 204
            except Exception as e:
                conn.rollback()
                print(f"Error deleting book: {e}")
                return jsonify({"error": "Database error while deleting book"}), 500


# ==============================
# Transaction API - Đã kết nối DB
# ==============================
@app.route('/transactions', methods=['POST'])
def create_transaction():
    """Tạo một giao dịch mượn hoặc trả sách"""
    data = request.json
    if not data or not all(k in data for k in ('user_id', 'book_id', 'quantity', 'type')):
        return jsonify({"error": "Invalid input: Requires user_id, book_id, quantity, type"}), 400

    user_id = data['user_id']
    book_id = data['book_id']
    quantity = data['quantity']
    tran_type = data['type']

    if tran_type not in ['borrow', 'return']:
        return jsonify({"error": "Invalid transaction type, must be 'borrow' or 'return'"}), 400

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                # 1. KIỂM TRA SỰ TỒN TẠI VÀ SỐ LƯỢNG SẴN CÓ
                cur.execute("SELECT available_copies FROM BOOKS WHERE id = %s", (book_id,))
                book_row = cur.fetchone()
                if not book_row:
                    return jsonify({"error": "Book not found"}), 404
                available_copies = book_row[0]

                # 2. XỬ LÝ LOGIC MƯỢN/TRẢ VÀ CẬP NHẬT BOOKS
                new_copies = available_copies
                if tran_type == 'borrow':
                    if available_copies < quantity:
                        return jsonify({"error": "Not enough copies available"}), 400
                    new_copies = available_copies - quantity
                elif tran_type == 'return':
                    new_copies = available_copies + quantity
                
                # Cập nhật số lượng sách
                cur.execute("UPDATE BOOKS SET available_copies = %s WHERE id = %s", (new_copies, book_id))

                # 3. TẠO GIAO DỊCH MỚI
                sql_insert_tran = """
                    INSERT INTO TRANSACTIONS (user_id, book_id, quantity, type) 
                    VALUES (%s, %s, %s, %s) 
                    RETURNING id
                """
                cur.execute(sql_insert_tran, (user_id, book_id, quantity, tran_type))
                tran_id = cur.fetchone()[0]
                
                conn.commit()
                return jsonify({"message": "Transaction recorded successfully", "transaction_id": tran_id}), 201
            except Exception as e:
                conn.rollback()
                print(f"Error creating transaction: {e}")
                return jsonify({"error": "Database error: Could not process transaction (Check user_id existence)"}), 500


# ==============================
# User API - Đã kết nối DB
# ==============================
@app.route('/users/<int:user_id>/books', methods=['GET'])
def list_user_books(user_id):
    """Lấy danh sách các sách mà người dùng đã mượn hoặc trả"""

    # Check if user exists (Optional, but good practice)
    # cur.execute("SELECT id FROM USERS WHERE id = %s", (user_id,))
    # if not cur.fetchone():
    #     return jsonify({"error": "User not found"}), 404

    relation = request.args.get('relation', 'borrowed')
    if relation not in ['borrowed', 'returned']:
        return jsonify({"error": "Invalid relation type"}), 400

    tran_type = 'borrow' if relation == 'borrowed' else 'return'

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            sql = """
                SELECT 
                    b.id, b.title, b.author, 
                    t.quantity, t.type AS transaction_type, t.transaction_date AS date
                FROM TRANSACTIONS t
                JOIN BOOKS b ON t.book_id = b.id
                WHERE t.user_id = %s AND t.type = %s
            """
            cur.execute(sql, (user_id, tran_type))
            
            result = [row_to_dict(cur, row) for row in cur.fetchall()]

            etag = generate_etag(result)
            if request.headers.get('If-None-Match') == etag:
                return '', 304

            response = make_response(jsonify(result), 200)
            response.headers['Content-Type'] = 'application/json'
            response.headers['ETag'] = etag
            return response


# ==============================
# Run
# ==============================
if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    print(f"🚀 Public URL (ngrok): {public_url.public_url}")

    # Chạy Flask server
    app.run(port=5000)
