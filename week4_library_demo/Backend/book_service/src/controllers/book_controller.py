# book_service/src/controllers/book_controller.py

from flask import Blueprint, request, jsonify, make_response, current_app
from ..services.book_service import BookService

book_bp = Blueprint('book_bp', __name__)

# --- ĐÃ XÓA GLOBAL SERVICE VÀ @book_bp.record ---


def validate_pagination_params():
    """
    Kiểm tra các tham số, ưu tiên Cursor-based.
    """
    limit = request.args.get('limit', 20)
    try:
        limit = int(limit)
    except ValueError:
        return jsonify({"error": "Limit must be a valid integer"}), 400, None, None, None, None, None
    if limit < 1 or limit > 100:
        return jsonify({"error": "Invalid limit value (limit max 100)"}), 400, None, None, None, None, None

    author_filter = request.args.get('author_filter', request.args.get('author', '').strip())
    
    after_cursor = request.args.get('after_cursor')
    before_cursor = request.args.get('before_cursor')
    
    if after_cursor and before_cursor:
        return jsonify({"error": "Cannot use both after_cursor and before_cursor"}), 400, None, None, None, None, None
    
    if after_cursor or before_cursor:
        cursor_value = after_cursor if after_cursor else before_cursor
        cursor_direction = 'forward' if after_cursor else 'backward'
        return None, 'cursor', limit, None, cursor_value, cursor_direction, author_filter

    page = request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        return jsonify({"error": "Page must be a valid integer"}), 400, None, None, None, None, None
    if page < 1:
        return jsonify({"error": "Invalid page value"}), 400, None, None, None, None, None

    return None, 'offset', limit, page, None, None, author_filter

# ==============================
# Endpoint Chung: list_books
# ==============================
@book_bp.route('/books', methods=['GET'])
def list_books():
    error_response, pagination_type, limit, page, cursor_value, cursor_direction, author_filter = validate_pagination_params()
    
    if error_response: 
        return error_response
    
    print(f">>> Pagination Type: {pagination_type}")
    print(f">>> Filter: {author_filter}")

    service = BookService()
    # ✅ LẤY BASE_URL TỪ CONTROLLER
    base_url = request.url_root.strip('/') 

    if pagination_type == 'offset':
        # ✅ TRUYỀN base_url vào service
        response_data = service.get_books_offset(page, limit, author_filter, base_url=base_url)
    
    elif pagination_type == 'cursor':
        # ✅ TRUYỀN base_url vào service
        response_data = service.get_books_cursor(limit, cursor_value, cursor_direction, author_filter, base_url=base_url) 
        
    else:
        # ✅ TRUYỀN base_url vào service
        response_data = service.get_books_offset(1, limit, author_filter, base_url=base_url)

    # Xử lý Caching và Response
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
    service = BookService()
    # ✅ LẤY BASE_URL TỪ CONTROLLER
    base_url = request.url_root.strip('/') 
    
    # ✅ TRUYỀN base_url vào service
    book = service.get_book_by_id(book_id, base_url=base_url)
    
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
        service = BookService()
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
        service = BookService()
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
        service = BookService()
        if not service.delete_book(book_id):
            return jsonify({"error": "Book not found"}), 404
        return '', 204
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Database error while deleting book"}), 500