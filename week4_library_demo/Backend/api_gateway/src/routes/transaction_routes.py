from flask import Blueprint, request, jsonify, current_app, g
from ..auth.decorators import token_required
from .auth_routes import _proxy_request

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/transactions', methods=['POST'])
@token_required
def create_transaction():
    """Tạo giao dịch cho user đang đăng nhập."""
    data = request.json
    data['user_id'] = g.user.get('user_id') 
    url = current_app.config['TRANSACTION_SERVICE_URL']
    return _proxy_request(url, 'transactions', new_data=data)

@transaction_bp.route('/me/borrowed-books', methods=['GET'])
@token_required
def get_my_borrowed_books():
    """
    ROUTE MỚI: Lấy danh sách sách đang mượn của user hiện tại.
    """
    user_id = g.user.get('user_id')
    url = current_app.config['TRANSACTION_SERVICE_URL']
    # Gọi đến endpoint mới của service: /users/{user_id}/borrowed-books
    return _proxy_request(url, f'users/{user_id}/borrowed-books')

@transaction_bp.route('/me/transactions', methods=['GET'])
@token_required
def get_my_transactions():
    """Lấy toàn bộ lịch sử giao dịch của user hiện tại."""
    user_id = g.user.get('user_id')
    url = current_app.config['TRANSACTION_SERVICE_URL']
    return _proxy_request(url, f'users/{user_id}/transactions')
