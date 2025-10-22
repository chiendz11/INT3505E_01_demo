import json
import hashlib
from flask import request

# Khởi tạo Repository để giao tiếp với DB
from ..repositories.book_repository import BookRepository

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    def generate_etag(self, data):
        """Helper: Tạo ETag dựa trên nội dung JSON"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode("utf-8")).hexdigest()

    def add_hateoas_book(self, book_dict):
        """Thêm link HATEOAS cho resource Book"""
        # Lưu ý: Chúng ta giả định BASE_URL là của API Gateway khi chạy qua Gateway,
        # nhưng ở đây ta dùng URL của Service này (port 5001) để test độc lập.
        BASE_URL = request.url_root.strip('/') 
        book_dict['links'] = [
            {"rel": "self", "href": f"{BASE_URL}books/{book_dict['id']}", "method": "GET"},
            {"rel": "update", "href": f"{BASE_URL}books/{book_dict['id']}", "method": "PUT"},
            {"rel": "delete", "href": f"{BASE_URL}books/{book_dict['id']}", "method": "DELETE"},
            # Link này sẽ trỏ đến Transaction Service (qua Gateway)
            {"rel": "borrow", "href": f"{BASE_URL}transactions", "method": "POST"}
        ]
        return book_dict

    def paginate_links(self, endpoint, current_page, limit, total_count=None, cursor_id=None, last_id=None):
        """Helper: Tạo các liên kết điều hướng cho phân trang"""
        links = {}
        BASE_URL = request.url_root.strip('/')

        if endpoint == '/books': # Offset-based pagination
            if total_count is not None:
                total_pages = (total_count + limit - 1) // limit
                
                links['first'] = f"{BASE_URL}{endpoint}?page=1&limit={limit}"
                
                if current_page > 1:
                    links['prev'] = f"{BASE_URL}{endpoint}?page={current_page - 1}&limit={limit}"
                
                if current_page < total_pages:
                    links['next'] = f"{BASE_URL}{endpoint}?page={current_page + 1}&limit={limit}"
                
                links['last'] = f"{BASE_URL}{endpoint}?page={total_pages}&limit={limit}"
            
        elif endpoint == '/books/cursor': # Cursor-based pagination
            if last_id is not None:
                links['next'] = f"{BASE_URL}{endpoint}?limit={limit}&cursor_id={last_id}"
                
            links['first'] = f"{BASE_URL}{endpoint}?limit={limit}"
            
        return links

    # ====================================================================
    # LOGIC NGHIỆP VỤ
    # ====================================================================

    def get_books_offset(self, page, limit, author_filter=None):
        """Lấy sách dùng Offset Pagination"""
        offset = (page - 1) * limit
        total_count = self.repo.get_total_count(author_filter)
        
        books = self.repo.get_all_offset(offset, limit, author_filter)
        result_dicts = [self.add_hateoas_book(book.to_dict()) for book in books]

        total_pages = (total_count + limit - 1) // limit
        
        response_data = {
            "metadata": {
                "pagination_strategy": "offset_limit",
                "total_records": total_count,
                "page": page, 
                "limit": limit,
                "total_pages": total_pages
            },
            "data": result_dicts,
            "links": self.paginate_links('/books', page, limit, total_count=total_count)
        }
        return response_data

    def get_books_cursor(self, limit, cursor_id=None, author_filter=None):
        """Lấy sách dùng Cursor Pagination"""
        books = self.repo.get_all_cursor(limit, cursor_id, author_filter)
        result_dicts = [self.add_hateoas_book(book.to_dict()) for book in books]
        
        # Xác định cursor cho trang tiếp theo (ID cuối cùng)
        last_id = books[-1].id if books and len(books) == limit else None
        
        response_data = {
            "metadata": {
                "pagination_strategy": "cursor_based",
                "limit": limit,
                "current_cursor_id": cursor_id if cursor_id is not None else "start",
                "next_cursor_id": last_id if last_id is not None else "end_of_data"
            },
            "data": result_dicts,
            "links": self.paginate_links('/books/cursor', 1, limit, cursor_id=cursor_id, last_id=last_id)
        }
        return response_data

    def get_book_by_id(self, book_id):
        """Lấy sách đơn lẻ"""
        book = self.repo.get_by_id(book_id)
        if book:
            return self.add_hateoas_book(book.to_dict())
        return None

    def create_book(self, data):
        """Tạo sách mới"""
        return self.repo.create(data['title'], data['author'], data['available_copies'])

    def update_book(self, book_id, data):
        """Cập nhật sách"""
        return self.repo.update(book_id, data['title'], data['author'], data['available_copies'])

    def delete_book(self, book_id):
        """Xóa sách"""
        return self.repo.delete(book_id)

    def check_and_update_copies(self, book_id, quantity, tran_type):
        """
        Dùng cho Transaction Service.
        Đây là logic nghiệp vụ liên quan đến việc cập nhật số lượng sách.
        """
        quantity_change = quantity if tran_type == 'return' else -quantity
        
        status, new_copies = self.repo.update_copies(book_id, quantity_change)
        
        if status == "Success":
            return True, None
        
        # Trả về lỗi nếu không thành công
        return False, status
