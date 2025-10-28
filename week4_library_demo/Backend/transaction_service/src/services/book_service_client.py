from flask import current_app
import requests

class BookServiceClient:
    """Service client nội bộ để giao tiếp với Book Service."""

    _cache = None  # 👈 cache tạm thời cho eager loading

    def __init__(self):
        self.base_url = current_app.config['BOOK_SERVICE_URL']

    # ------------------- BATCH LOADING -------------------
    def get_books_details(self, book_ids):
        """
        Batch loading: Gửi danh sách ID để lấy thông tin chi tiết sách.
        Tránh N+1 query problem bằng 1 request duy nhất.
        """
        if not book_ids:
            return {}

        try:
            endpoint = f"{self.base_url}/internal/books/batch"
            response = requests.post(endpoint, json={"book_ids": book_ids}, timeout=5)
            response.raise_for_status()
            books = response.json()
            return {book["id"]: book for book in books}
        except requests.exceptions.RequestException as e:
            print(f"[BookServiceClient] Không thể kết nối tới Book Service: {e}")
            return {}
    
    def update_book_copies(book_id, quantity, tran_type, user_id):
        """
        Gọi sang Book Service để cập nhật số lượng sách (borrow/return).
        Trả về tuple: (success: bool, error_message: str | None, status_code: int)
        """
        book_service_url = current_app.config['BOOK_SERVICE_URL']
        update_endpoint = f"{book_service_url}/internal/books/{book_id}"

        payload = {
            "quantity": quantity,
            "type": tran_type,
            "user_id": user_id
        }

        try:
            response = requests.put(update_endpoint, json=payload, timeout=5)
            if response.status_code == 200:
                return True, None, 200
            else:
                error = response.json().get("error", "Lỗi từ Book Service")
                return False, error, response.status_code

        except requests.exceptions.RequestException as e:
            return False, f"Không thể kết nối đến Book Service: {e}", 503

