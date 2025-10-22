from flask import current_app
import requests
from ..models.transaction_model import Transaction
from ..repositories.transaction_repository import TransactionRepository
import uuid

class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()

    def get_transactions_for_user(self, user_id):
        transactions = self.repo.get_by_user_id(user_id)
        return [t.to_dict() for t in transactions]
    
    def get_currently_borrowed_for_user(self, user_id):
        """Service để lấy danh sách sách đang mượn, đã được làm giàu thông tin."""
        borrowed_summary = self.repo.get_currently_borrowed_by_user_id(user_id)
        
        book_ids = [item.book_id for item in borrowed_summary]
        if not book_ids:
            return []

        # Gọi sang Book Service để lấy thông tin chi tiết (tên sách,...)
        books_details = {}
        try:
            book_service_url = current_app.config['BOOK_SERVICE_URL']
            books_info_endpoint = f"{book_service_url}/internal/books/details"
            response = requests.post(books_info_endpoint, json={"book_ids": book_ids}, timeout=5)
            response.raise_for_status()
            books_details = {book['id']: book for book in response.json()}
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not connect to Book Service. {e}")

        # Kết hợp kết quả từ DB và Book Service
        result = []
        for item in borrowed_summary:
            book_info = books_details.get(item.book_id, {})
            result.append({
                "book_id": item.book_id,
                "book_title": book_info.get("title", f"Sách (ID: {item.book_id})"),
                "borrowed_count": item.borrowed_count
            })
        return result

    def create_transaction(self, user_id, book_id, quantity, tran_type):
        """Logic tạo giao dịch, có gọi sang Book Service để cập nhật số lượng."""
        # ... (Phần logic này giữ nguyên không đổi)
        book_service_url = current_app.config['BOOK_SERVICE_URL']
        update_copies_endpoint = f"{book_service_url}/internal/books/update_copies"

        payload = {"book_id": book_id, "quantity": quantity, "type": tran_type}
        try:
            response = requests.put(update_copies_endpoint, json=payload, timeout=5)
            if response.status_code != 200:
                return None, response.json().get("error", "Lỗi từ Book Service"), response.status_code
        except requests.exceptions.RequestException as e:
            return None, f"Không thể kết nối đến Book Service: {e}", 503

        new_transaction = Transaction(
            user_id=str(user_id),
            book_id=book_id,
            quantity=quantity,
            type=tran_type
        )
        saved_transaction = self.repo.add(new_transaction)
        return saved_transaction.to_dict(), None, 201

