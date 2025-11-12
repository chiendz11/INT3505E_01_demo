# book_service/src/controllers/book_controller.py

from flask import Blueprint, request, jsonify, make_response
from ..services.book_service import BookService

# 1. Import các exception
from ..exceptions import (
    BookNotFoundError, 
    BookAlreadyExistsError, 
    InvalidBookDataError,
    NotEnoughCopiesError
)

book_bp = Blueprint('book_bp', __name__)

# ====================================================================
# 2. ĐỊNH NGHĨA CÁC TRÌNH XỬ LÝ LỖI (ERROR HANDLERS)
# Flask sẽ tự động gọi các hàm này khi service ném ra exception.
# ====================================================================

@book_bp.errorhandler(BookNotFoundError)
def handle_book_not_found(error):
    """Xử lý lỗi 404 (Không tìm thấy)"""
    return jsonify({"error": str(error)}), 404

@book_bp.errorhandler(InvalidBookDataError)
def handle_invalid_data(error):
    """Xử lý lỗi 400 (Dữ liệu vào không hợp lệ)"""
    return jsonify({"error": str(error)}), 400

@book_bp.errorhandler(BookAlreadyExistsError)
def handle_book_exists(error):
    """Xử lý lỗi 409 (Tài nguyên bị trùng)"""
    return jsonify({"error": str(error)}), 409

@book_bp.errorhandler(NotEnoughCopiesError)
def handle_not_enough_copies(error):
    """Xử lý lỗi 400 (Logic nghiệp vụ thất bại)"""
    return jsonify({"error": str(error)}), 400

@book_bp.errorhandler(Exception)
def handle_generic_exception(error):
    """Xử lý các lỗi 500 (Lỗi server chung)"""
    # Ghi log lỗi này ra console hoặc file log
    print(f"Internal Server Error: {error}")
    return jsonify({"error": "An internal server error occurred"}), 500

# ====================================================================
# (Hàm validate pagination của bạn - Giữ nguyên)
# ====================================================================

def validate_pagination_params():
    """
    Kiểm tra các tham số, ưu tiên Cursor-based.
    Hàm này không ném exception mà trả về lỗi trực tiếp vì nó
    liên quan đến 'request.args', không phải logic service.
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

# ====================================================================
# 3. CÁC ROUTE (ENDPOINT) - GIỜ ĐÃ RẤT SẠCH SẼ
# ====================================================================

@book_bp.route('/books', methods=['GET'])
def list_books():
    # 1. Validate query params (hàm này trả về lỗi trực tiếp)
    error_response, pagination_type, limit, page, cursor_value, cursor_direction, author_filter = validate_pagination_params()
    if error_response: 
        return error_response
    
    # 2. Gọi service (hàm này không ném lỗi nghiệp vụ)
    service = BookService()
    base_url = request.url_root.strip('/') 

    if pagination_type == 'offset':
        response_data = service.get_books_offset(page, limit, author_filter, base_url=base_url)
    else: # (cursor or default)
        response_data = service.get_books_cursor(limit, cursor_value, cursor_direction, author_filter, base_url=base_url) 
        
    # 3. Xử lý ETag và trả về (đã tốt)
    etag = service.generate_etag(response_data)
    if request.headers.get('If-None-Match') == etag:
        return '', 304 
    
    response = make_response(jsonify(response_data), 200)
    response.headers['Cache-Control'] = 'public, max-age=60'
    response.headers['ETag'] = etag
    return response

# ------------------------------
# CRUD (Single Resource)
# ------------------------------

@book_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    # Chỉ cần gọi. Nếu lỗi, @errorhandler sẽ bắt.
    service = BookService()
    base_url = request.url_root.strip('/') 
    book = service.get_book_by_id(book_id, base_url=base_url)
    
    # Logic ETag
    etag = service.generate_etag(book)
    if request.headers.get('If-None-Match') == etag:
        return '', 304

    response = make_response(jsonify(book), 200)
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=120'
    return response


@book_bp.route('/books', methods=['POST'])
def create_book():
    data = request.json
    if not data:
        # Lỗi này đơn giản, ném ra để handler bắt
        raise InvalidBookDataError("Invalid input, JSON body required")

    # Chỉ cần gọi. Nếu lỗi, @errorhandler sẽ bắt.
    service = BookService()
    new_book = service.create_book(data)
    
    return jsonify({"message": "Book created", "book_id": new_book.id}), 201


@book_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    if not data:
        raise InvalidBookDataError("Invalid input, JSON body required")

    # Chỉ cần gọi. Nếu lỗi, @errorhandler sẽ bắt.
    service = BookService()
    service.update_book(book_id, data)
    
    return jsonify({"message": "Book updated successfully"}), 200


@book_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    # Chỉ cần gọi. Nếu lỗi, @errorhandler sẽ bắt.
    service = BookService()
    service.delete_book(book_id)
    
    # 204 No Content là chuẩn cho DELETE
    return '', 204  