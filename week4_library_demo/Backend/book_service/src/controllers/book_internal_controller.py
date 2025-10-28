# book_service/src/controllers/internal/book_internal_controller.py

from flask import Blueprint, request, jsonify
from ..services.book_service import BookService

book_internal_bp = Blueprint('book_internal_bp', __name__)

# --- ĐÃ XÓA GLOBAL SERVICE VÀ @book_internal_bp.record ---


# ==============================
# Internal Endpoint — chỉ cho phép các service nội bộ gọi
# ==============================

@book_internal_bp.route('/internal/books/<book_id>', methods=['PUT'])
def internal_update_book(book_id):
    """
    Internal API: được TransactionService hoặc InventoryService gọi sang khi có borrow/return.
    Không được FE gọi trực tiếp.
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('quantity', 'type')):
        return jsonify({"error": "Invalid internal input"}), 400

    quantity = data['quantity']
    tran_type = data['type']

    # KHỞI TẠO SERVICE TẠI ĐÂY
    service = BookService()
    success, error_message = service.check_and_update_copies(book_id, quantity, tran_type)

    if success:
        return jsonify({"message": f"Book {book_id} updated successfully"}), 200
    else:
        status_code = 404 if error_message == "Book not found" else 400
        return jsonify({"error": error_message}), status_code   