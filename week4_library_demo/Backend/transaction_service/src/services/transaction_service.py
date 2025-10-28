from flask import current_app
import requests
from ..models.transaction_model import Transaction
from ..repositories.transaction_repository import TransactionRepository
from .book_service_client import BookServiceClient
import uuid

class TransactionService:
    def __init__(self):
        self.repo = TransactionRepository()
        self.book_client = BookServiceClient()

    def get_transactions_for_user(self, user_id):
        transactions = self.repo.get_by_user_id(user_id)
        return [t.to_dict() for t in transactions]
    
    # batch loading để tránh N+1 query problem
    def get_currently_borrowed_for_user(self, user_id):
        """
        Batch loading: chỉ gọi 1 lần sang BookService để lấy thông tin các sách liên quan.
        """
        borrowed_summary = self.repo.get_currently_borrowed_by_user_id(user_id)
        book_ids = [item.book_id for item in borrowed_summary]

        books_details = self.book_client.get_books_details(book_ids)

        result = []
        for item in borrowed_summary:
            book_info = books_details.get(item.book_id, {})
            result.append({
                "book_id": item.book_id,
                "book_title": book_info.get("title", f"Sách (ID: {item.book_id})"),
                "borrowed_count": item.borrowed_count
            })
        return result



# Ví dụ về khi mắc N+1 query problem:
# result = []
# for item in borrowed_summary:
#     # ❌ Gọi 1 request riêng lẻ cho mỗi sách
#     response = requests.get(f"{book_service_url}/books/{item.book_id}")
#     book_info = response.json()
#     result.append({
#         "book_id": item.book_id,
#         "book_title": book_info.get("title")
#     })
    
    def create_transaction(self, user_id, book_id, quantity, tran_type):
        """Tạo giao dịch và cập nhật số lượng sách qua Book Service."""
        success, error_message, status = self.book_client.update_book_copies(
            book_id, quantity, tran_type, user_id
        )

        if not success:
            return None, error_message, status

        new_transaction = Transaction(
            user_id=str(user_id),
            book_id=book_id,
            quantity=quantity,
            type=tran_type
        )

        saved_transaction = self.repo.add(new_transaction)
        return saved_transaction.to_dict(), None, 201

