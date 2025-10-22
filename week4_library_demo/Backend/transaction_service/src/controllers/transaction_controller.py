from flask import Blueprint, request, jsonify, g
from ..services.transaction_service import TransactionService
import uuid

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """Endpoint để user tạo giao dịch (mượn/trả)"""
    data = request.json
    # AN TOÀN: Lấy user_id từ request đã được gateway xác thực
    user_id = data.get('user_id') 
    book_id = data.get('book_id')
    quantity = data.get('quantity')
    tran_type = data.get('type')

    if not all([user_id, book_id, quantity, tran_type]):
        return jsonify({"error": "Thiếu thông tin cần thiết"}), 400

    service = TransactionService()
    transaction, error, status_code = service.create_transaction(uuid.UUID(user_id), book_id, quantity, tran_type)

    if error:
        return jsonify({"error": error}), status_code
    return jsonify(transaction), status_code

@transaction_bp.route('/users/<uuid:user_id>/borrowed-books', methods=['GET'])
def get_user_borrowed_books(user_id):
    """
    ENDPOINT MỚI: Lấy danh sách sách đang mượn của một user cụ thể.
    Gateway sẽ gọi endpoint này sau khi xác thực token.
    """
    service = TransactionService()
    borrowed_books = service.get_currently_borrowed_for_user(user_id)
    return jsonify(borrowed_books), 200

@transaction_bp.route('/users/<uuid:user_id>/transactions', methods=['GET'])
def get_user_transactions(user_id):
    """Endpoint nội bộ để lấy TOÀN BỘ lịch sử giao dịch của một user"""
    service = TransactionService()
    transactions = service.get_transactions_for_user(user_id)
    return jsonify(transactions), 200

