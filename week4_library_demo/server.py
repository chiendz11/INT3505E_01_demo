from pyngrok import ngrok
import json
import hashlib
import psycopg2
from flask import Flask, make_response, request, jsonify, url_for
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
# Helper: Tạo HATEOAS cho Pagination
# ==============================
def paginate_links(endpoint, current_page, limit, total_count=None, cursor=None, last_id=None):
    """Tạo các liên kết điều hướng cho phân trang (Offset hoặc Cursor)"""
    links = {}
    BASE_URL = request.url_root.strip('/')

    if endpoint == '/books': # Chiến lược 1: Offset-based pagination
        if total_count is not None:
            total_pages = (total_count + limit - 1) // limit
            
            # Link đầu tiên
            links['first'] = f"{BASE_URL}{endpoint}?page=1&limit={limit}"
            
            # Link trước
            if current_page > 1:
                links['prev'] = f"{BASE_URL}{endpoint}?page={current_page - 1}&limit={limit}"
            
            # Link sau
            if current_page < total_pages:
                links['next'] = f"{BASE_URL}{endpoint}?page={current_page + 1}&limit={limit}"
            
            # Link cuối
            links['last'] = f"{BASE_URL}{endpoint}?page={total_pages}&limit={limit}"
        
    elif endpoint == '/books/cursor': # Chiến lược 2: Cursor-based pagination
        # Link tiếp theo
        if last_id is not None:
            # Nếu có kết quả, next cursor là ID cuối cùng
            links['next'] = f"{BASE_URL}{endpoint}?limit={limit}&cursor_id={last_id}"
            
        # Link đầu tiên (Reset)
        links['first'] = f"{BASE_URL}{endpoint}?limit={limit}"
        
    return links

# ==============================
# Chiến lược 1: OFFSET/LIMIT Pagination
# ==============================
@app.route('/books', methods=['GET'])
def list_books_offset_pagination():
    """
    Chiến lược 1: Phân trang theo OFFSET/LIMIT (dùng tham số page và limit)
    Sử dụng cho Page Numbering.
    """
    # Lấy tham số cho Pagination
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        return jsonify({"error": "Page and limit must be valid integers"}), 400

    if page < 1 or limit < 1 or limit > 100:
        return jsonify({"error": "Invalid page or limit value (limit max 100)"}), 400

    offset = (page - 1) * limit
    author_filter = request.args.get('author')
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. LẤY TỔNG SỐ LƯỢNG (cho HATEOAS)
            count_sql = "SELECT COUNT(id) FROM BOOKS"
            count_params = []

            if author_filter:
                count_sql += " WHERE LOWER(author) = LOWER(%s)"
                count_params.append(author_filter)
            
            cur.execute(count_sql, count_params)
            total_count = cur.fetchone()[0]
            
            # 2. LẤY DỮ LIỆU CỦA TRANG HIỆN TẠI
            sql = "SELECT id, title, author, available_copies FROM BOOKS"
            params = []
            
            if author_filter:
                sql += " WHERE LOWER(author) = LOWER(%s)"
                params.append(author_filter)
                
            sql += " ORDER BY id ASC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cur.execute(sql, params)
            
            # Chuyển kết quả sang dạng list of dicts
            result = [add_hateoas_book(row_to_dict(cur, row)) for row in cur.fetchall()]

            # 3. TẠO RESPONSE BAO GỒM METADATA VÀ LINKS
            total_pages = (total_count + limit - 1) // limit
            response_data = {
                "metadata": {
                    "pagination_strategy": "offset_limit",
                    "total_records": total_count,
                    "page": page,   
                    "limit": limit,
                    "total_pages": total_pages
                },
                "data": result,
                "links": paginate_links('/books', page, limit, total_count=total_count)
            }

            # 4. ETag & CACHE
            etag = generate_etag(response_data)
            
            if request.headers.get('If-None-Match') == etag:
                return '', 304 
            
            response = make_response(jsonify(response_data), 200)
            response.headers['Cache-Control'] = 'public, max-age=60'
            response.headers['Content-Type'] = 'application/json'
            response.headers['ETag'] = etag
            return response


# ==============================
# Chiến lược 2: CURSOR-BASED Pagination
# ==============================
@app.route('/books/cursor', methods=['GET'])
def list_books_cursor_pagination():
    """
    Chiến lược 2: Phân trang theo CURSOR (Keyset Pagination)
    Sử dụng ID của bản ghi cuối cùng làm "cursor" để tìm trang tiếp theo.
    """
    try:
        limit = int(request.args.get('limit', 20))
        # cursor_id là ID của bản ghi cuối cùng của trang TRƯỚC ĐÓ
        cursor_id = request.args.get('cursor_id', type=int) 
    except ValueError:
        return jsonify({"error": "Limit and cursor_id must be valid integers"}), 400

    if limit < 1 or limit > 100:
        return jsonify({"error": "Invalid limit value (limit max 100)"}), 400
        
    author_filter = request.args.get('author')
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            sql = "SELECT id, title, author, available_copies FROM BOOKS"
            params = []
            
            where_clauses = []
            if author_filter:
                where_clauses.append("LOWER(author) = LOWER(%s)")
                params.append(author_filter)
            
            # KeySet Logic: chỉ lấy các ID lớn hơn ID cursor
            if cursor_id is not None:
                where_clauses.append("id > %s")
                params.append(cursor_id)
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
                
            sql += " ORDER BY id ASC LIMIT %s"
            params.append(limit)

            cur.execute(sql, params)
            
            result = [add_hateoas_book(row_to_dict(cur, row)) for row in cur.fetchall()]
            
            # Xác định cursor cho trang tiếp theo (ID cuối cùng của kết quả)
            last_id = result[-1]['id'] if result and len(result) == limit else None
            
            # 3. TẠO RESPONSE BAO GỒM METADATA VÀ LINKS
            response_data = {
                "metadata": {
                    "pagination_strategy": "cursor_based",
                    "limit": limit,
                    "current_cursor_id": cursor_id if cursor_id is not None else "start",
                    "next_cursor_id": last_id if last_id is not None else "end_of_data"
                },
                "data": result,
                "links": paginate_links('/books/cursor', 1, limit, cursor=cursor_id, last_id=last_id)
            }

            # 4. ETag & CACHE
            etag = generate_etag(response_data)
            
            if request.headers.get('If-None-Match') == etag:
                return '', 304 
            
            response = make_response(jsonify(response_data), 200)
            response.headers['Cache-Control'] = 'public, max-age=60'
            response.headers['Content-Type'] = 'application/json'
            response.headers['ETag'] = etag
            return response


# ==============================
# Chiến lược 3: SINGLE RESOURCE (Không phân trang)
# ==============================
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Chiến lược 3: Không phân trang (Single Resource Retrieval)"""
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
# Transaction API - KHÔNG THAY ĐỔI
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
# User API - KHÔNG THAY ĐỔI
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
    app.run(host="0.0.0.0", port=5000)
