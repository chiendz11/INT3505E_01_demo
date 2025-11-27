# book_service/src/controllers/book_controller.py

import time
import logging
import json
import traceback
from flask import Blueprint, request, jsonify, make_response, current_app
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
# [LESSON 10] CẤU HÌNH LOGGING & HELPER
# ====================================================================

# Thiết lập logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BookServiceMonitor")

def log_audit(action, target_id, details=None):
    """
    [SECURITY] Audit Logs: Ghi lại các hành động thay đổi dữ liệu (Create/Update/Delete).
    Giúp truy vết ai đã làm gì vào lúc nào.
    """
    user_id = request.headers.get('X-User-ID', 'Anonymous') # Giả lập lấy ID từ Gateway
    
    audit_record = {
        "event_type": "AUDIT_LOG",
        "timestamp": time.time(),
        "actor": user_id,
        "action": action,
        "target_resource": "book",
        "target_id": target_id,
        "ip": request.remote_addr,
        "details": details or {}
    }
    # Ghi log INFO (Thực tế sẽ đẩy vào bảng Audit DB hoặc ELK)
    logger.info(json.dumps(audit_record))


# ====================================================================
# [LESSON 10] MIDDLEWARE: OBSERVABILITY (LOGS & METRICS)
# ====================================================================

@book_bp.before_request
def start_timer():
    """Bắt đầu đo thời gian xử lý request"""
    request.start_time = time.time()

@book_bp.after_request
def log_access_request(response):
    """
    [MONITORING] Ghi Access Log dạng JSON sau khi request hoàn tất.
    Dùng để đo độ trễ (Latency) và theo dõi trạng thái HTTP.
    """
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        
        log_data = {
            "event_type": "ACCESS_LOG",
            "method": request.method,
            "path": request.path,
            "ip": request.remote_addr,
            "status": response.status_code,
            "duration_seconds": round(duration, 4),
            "user_agent": request.headers.get('User-Agent')
        }
        
        # Phân loại log
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
            
    return response

# ====================================================================
# ERROR HANDLERS (DEBUGGING)
# ====================================================================

@book_bp.errorhandler(BookNotFoundError)
def handle_book_not_found(error):
    return jsonify({"error": str(error)}), 404

@book_bp.errorhandler(InvalidBookDataError)
def handle_invalid_data(error):
    return jsonify({"error": str(error)}), 400

@book_bp.errorhandler(BookAlreadyExistsError)
def handle_book_exists(error):
    return jsonify({"error": str(error)}), 409

@book_bp.errorhandler(NotEnoughCopiesError)
def handle_not_enough_copies(error):
    return jsonify({"error": str(error)}), 400

@book_bp.errorhandler(Exception)
def handle_generic_exception(error):
    """
    [DEBUGGING] Xử lý lỗi 500: In ra traceback chi tiết để Dev dễ fix bug.
    """
    error_traceback = traceback.format_exc()
    logger.error(f"INTERNAL SERVER ERROR:\n{error_traceback}")
    return jsonify({"error": "An internal server error occurred"}), 500


# ====================================================================
# HELPER FUNCTIONS
# ====================================================================

def _handle_get_book_response(book_id, api_version):
    """Helper xử lý Versioning cho GET Single Book"""
    service = BookService()
    base_url = request.url_root.strip('/') 
    
    book = service.get_book_by_id(book_id, base_url=base_url, version=api_version)
    
    etag = service.generate_etag(book)
    if request.headers.get('If-None-Match') == etag:
        return '', 304

    response = make_response(jsonify(book), 200)
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'public, max-age=120'
    
    # Header cảnh báo Deprecation cho V1
    if api_version == 'v1':
        response.headers['Warning'] = '299 - "API V1 is deprecated. Please upgrade to V2."'
        response.headers['X-API-Lifecycle'] = 'deprecated'

    return response

def validate_pagination_params():
    """Helper validate tham số phân trang"""
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
# ROUTES
# ====================================================================

@book_bp.route('/books', methods=['GET'])
def list_books():
    # [SECURITY] RATE LIMITING
    # Giới hạn 10 request/phút cho endpoint này để chống Spam/Cào dữ liệu
    limiter = current_app.extensions['limiter']
    
    with limiter.limit("10 per minute"):
        # 1. Validate
        error_response, pagination_type, limit, page, cursor_value, cursor_direction, author_filter = validate_pagination_params()
        if error_response: 
            return error_response
        
        # 2. Call Service
        service = BookService()
        base_url = request.url_root.strip('/') 

        if pagination_type == 'offset':
            response_data = service.get_books_offset(page, limit, author_filter, base_url=base_url)
        else:
            response_data = service.get_books_cursor(limit, cursor_value, cursor_direction, author_filter, base_url=base_url) 
            
        # 3. Cache & Response
        etag = service.generate_etag(response_data)
        if request.headers.get('If-None-Match') == etag:
            return '', 304 
        
        response = make_response(jsonify(response_data), 200)
        response.headers['Cache-Control'] = 'public, max-age=60'
        response.headers['ETag'] = etag
        return response

# --- CRUD (Single Resource) & Versioning ---

@book_bp.route('/v1/books/<int:book_id>', methods=['GET'])
def get_book_v1_url(book_id):
    return _handle_get_book_response(book_id, 'v1')

@book_bp.route('/v2/books/<int:book_id>', methods=['GET'])
def get_book_v2_url(book_id):
    return _handle_get_book_response(book_id, 'v2')

@book_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book_default(book_id):
    version_query = request.args.get('v')
    if version_query in ['2', 'v2']:
        return _handle_get_book_response(book_id, 'v2')
    
    accept_header = request.headers.get('Accept', '')
    if 'application/vnd.book-service.v2+json' in accept_header:
        return _handle_get_book_response(book_id, 'v2')
        
    return _handle_get_book_response(book_id, 'v1')


# --- WRITE OPERATIONS (With Audit Logs) ---

@book_bp.route('/books', methods=['POST'])
def create_book():
    data = request.json
    if not data:
        raise InvalidBookDataError("Invalid input, JSON body required")

    service = BookService()
    new_book = service.create_book(data)
    
    # [SECURITY] AUDIT LOG: Ghi lại hành động tạo sách
    log_audit("CREATE", new_book.id, {"title": new_book.title})
    
    return jsonify({"message": "Book created", "book_id": new_book.id}), 201


@book_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    if not data:
        raise InvalidBookDataError("Invalid input, JSON body required")

    service = BookService()
    service.update_book(book_id, data)
    
    # [SECURITY] AUDIT LOG: Ghi lại hành động cập nhật
    log_audit("UPDATE", book_id, data)
    
    return jsonify({"message": "Book updated successfully"}), 200


@book_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    service = BookService()
    service.delete_book(book_id)
    
    # [SECURITY] AUDIT LOG: Ghi lại hành động xóa
    log_audit("DELETE", book_id)
    
    return '', 204