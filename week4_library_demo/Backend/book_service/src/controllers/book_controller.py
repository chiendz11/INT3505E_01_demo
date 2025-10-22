# book_service/src/controllers/book_controller.py

from flask import Blueprint, request, jsonify, make_response, current_app
from ..services.book_service import BookService

book_bp = Blueprint('book_bp', __name__)

# Khởi tạo service một lần duy nhất khi Blueprint được import
# Truyền app context khi app đã được tạo (sẽ ổn vì register_blueprint nằm trong app context)
service = None


@book_bp.record
def record_params(setup_state):
    """Hàm này được Flask gọi khi Blueprint được đăng ký vào app."""
    global service
    app = setup_state.app
    service = BookService()
    print("✅ BookService initialized successfully in Blueprint context!")


# ==============================
# Kiểm tra tham số đầu vào
# ==============================
def validate_pagination_params():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
    except ValueError:
        return jsonify({"error": "Page and limit must be valid integers"}), 400, None, None

    if page < 1 or limit < 1 or limit > 100:
        return jsonify({"error": "Invalid page or limit value (limit max 100)"}), 400, None, None
        
    return None, page, limit, request.args.get('author_filter')


def validate_cursor_params():
    try:
        limit = int(request.args.get('limit', 20))
        cursor_id = request.args.get('cursor_id', type=int)
    except ValueError:
        return jsonify({"error": "Limit and cursor_id must be valid integers"}), 400, None, None

    if limit < 1 or limit > 100:
        return jsonify({"error": "Invalid limit value (limit max 100)"}), 400, None, None
        
    return None, limit, cursor_id, request.args.get('author')


# ==============================
# Chiến lược 1: OFFSET/LIMIT Pagination
# ==============================
@book_bp.route('/books', methods=['GET'])
def list_books_offset_pagination():
    error_response, page, limit, author_filter = validate_pagination_params()
    if error_response: return error_response
    print(">>> Author filter nhận được từ FE:", author_filter)


    response_data = service.get_books_offset(page, limit, author_filter)

    etag = service.generate_etag(response_data)
    if request.headers.get('If-None-Match') == etag:
        return '', 304 
    
    response = make_response(jsonify(response_data), 200)
    response.headers['Cache-Control'] = 'public, max-age=60'
    response.headers['Content-Type'] = 'application/json'
    response.headers['ETag'] = etag
    return response


# ==============================
# Chiến lược 2: CURSOR Pagination
# ==============================
@book_bp.route('/books/cursor', methods=['GET'])
def list_books_cursor_pagination():
    error_response, limit, cursor_id, author_filter = validate_cursor_params()
    if error_response: return error_response

    response_data = service.get_books_cursor(limit, cursor_id, author_filter)

    etag = service.generate_etag(response_data)
    if request.headers.get('If-None-Match') == etag:
        return '', 304 
    
    response = make_response(jsonify(response_data), 200)
    response.headers['Cache-Control'] = 'public, max-age=60'
    response.headers['Content-Type'] = 'application/json'
    response.headers['ETag'] = etag
    return response


# ==============================
# CRUD (Single Resource)
# ==============================
@book_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = service.get_book_by_id(book_id)
    
    if not book:
        return jsonify({"error": "Book not found"}), 404

    etag = service.generate_etag(book)
    if request.headers.get('If-None-Match') == etag:
        return '', 304

    response = make_response(jsonify(book), 200)
    response.headers['Content-Type'] = 'application/json'
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=120'
    return response


@book_bp.route('/books', methods=['POST'])
def create_book():
    data = request.json
    if not data or not all(k in data for k in ('title', 'author', 'available_copies')):
        return jsonify({"error": "Invalid input"}), 400

    try:
        new_book = service.create_book(data)
        return jsonify({"message": "Book created", "book_id": new_book.id}), 201
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error while creating book"}), 500


@book_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    if not data or not all(k in data for k in ('title', 'author', 'available_copies')):
        return jsonify({"error": "Invalid input"}), 400

    try:
        updated_book = service.update_book(book_id, data)
        if not updated_book:
            return jsonify({"error": "Book not found"}), 404
        
        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error while updating book"}), 500


@book_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:
        if not service.delete_book(book_id):
            return jsonify({"error": "Book not found"}), 404
        return '', 204
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error while deleting book"}), 500


# ==============================
# Internal Endpoint
# ==============================
@book_bp.route('/internal/books/update_copies', methods=['PUT'])
def internal_update_book_copies():
    data = request.json
    if not data or not all(k in data for k in ('book_id', 'quantity', 'type')):
        return jsonify({"error": "Invalid internal input"}), 400
    
    book_id = data['book_id']
    quantity = data['quantity']
    tran_type = data['type']
    
    success, error_message = service.check_and_update_copies(book_id, quantity, tran_type)
    
    if success:
        return jsonify({"message": "Book copies updated successfully"}), 200
    else:
        status_code = 404 if error_message == "Book not found" else 400
        return jsonify({"error": error_message}), status_code
