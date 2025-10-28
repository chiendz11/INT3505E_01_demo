from flask import Blueprint, request, jsonify, current_app, Response, g
from ..auth.decorators import token_required, admin_required
from .auth_routes import _proxy_request # Dùng lại hàm proxy

book_bp = Blueprint('book_bp', __name__)

# Helper để lấy URL của Book Service
def get_book_service_url():
    return current_app.config['BOOK_SERVICE_URL']

# ==================================
# Public Routes (Chỉ cần đăng nhập)
# ==================================
@book_bp.route('/books', methods=['GET'])
@token_required # Bất kỳ 'user' nào cũng có thể xem
def list_books():
    return _proxy_request(get_book_service_url(), 'books')

@book_bp.route('/books/<int:book_id>', methods=['GET'])
@token_required
def get_book(book_id):
    return _proxy_request(get_book_service_url(), f'books/{book_id}')

# ==================================
# Admin Routes (Phải là 'admin')
# ==================================
@book_bp.route('/books', methods=['POST'])
@token_required
@admin_required # CHỈ ADMIN
def create_book():
    return _proxy_request(get_book_service_url(), 'books')

@book_bp.route('/books/<int:book_id>', methods=['PUT'])
@token_required
@admin_required # CHỈ ADMIN
def update_book(book_id):
    return _proxy_request(get_book_service_url(), f'books/{book_id}')

@book_bp.route('/books/<int:book_id>', methods=['DELETE'])
@token_required
@admin_required # CHỈ ADMIN
def delete_book(book_id):
    return _proxy_request(get_book_service_url(), f'books/{book_id}')

# =Example: Endpoint nội bộ của book_service
# Gateway KHÔNG NÊN expose endpoint /internal/* ra ngoài
# Nếu Transaction Service cần gọi Book Service, nó nên gọi TRỰC TIẾP
# (trong mạng nội bộ) mà không cần đi qua Gateway.