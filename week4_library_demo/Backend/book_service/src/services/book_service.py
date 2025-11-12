# book_service/src/services/book_service.py

import json
import hashlib
from ..repositories.book_repository import BookRepository
# Import các lỗi nghiệp vụ
from ..exceptions import (
    BookNotFoundError, BookAlreadyExistsError, 
    InvalidBookDataError, NotEnoughCopiesError
)
# Import Model để tạo đối tượng mới
from ..models.book_model import Book 

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    # ====================================================================
    # LOGIC NGHIỆP VỤ (CRUD)
    # ====================================================================

    def create_book(self, data):
        """
        Tạo sách mới VÀ kiểm tra logic nghiệp vụ.
        Ném ra Exception nếu thất bại.
        """
        title = data.get('title')
        author = data.get('author')
        
        # SAD PATH 1: Validate data đầu vào
        if not title or not author:
            raise InvalidBookDataError("Title and Author cannot be empty")
            
        # SAD PATH 2: Business Rule - Kiểm tra sách đã tồn tại
        if self.repo.find_by_title_and_author(title, author):
            raise BookAlreadyExistsError(f"Book '{title}' by {author} already exists")
            
        # HAPPY PATH:
        copies = data.get('available_copies', 0)
        new_book = Book(title=title, author=author, available_copies=copies)
        
        return self.repo.save(new_book)

    def update_book(self, book_id, data):
        """
        Cập nhật sách VÀ kiểm tra logic.
        Ném ra Exception nếu thất bại.
        """
        # SAD PATH 1: Sách có tồn tại không?
        book = self.repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        
        # Cập nhật các trường
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.available_copies = data.get('available_copies', book.available_copies)
        
        # SAD PATH 2: Validate data sau khi cập nhật
        if not book.title or not book.author:
            raise InvalidBookDataError("Title and Author cannot be empty")
            
        # HAPPY PATH:
        return self.repo.save(book)

    def delete_book(self, book_id):
        """
        Xóa sách.
        Ném ra Exception nếu thất bại.
        """
        # SAD PATH 1: Sách có tồn tại không?
        book = self.repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with id {book_id} not found")
            
        # HAPPY PATH:
        return self.repo.delete(book)

    def check_and_update_copies(self, book_id, quantity, tran_type):
        """
        Kiểm tra và cập nhật số lượng (dùng cho Transaction).
        Ném ra Exception nếu thất bại.
        """
        # SAD PATH 1: Sách có tồn tại không?
        book = self.repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with id {book_id} not found")

        quantity_change = quantity if tran_type == 'return' else -quantity
        new_copies = book.available_copies + quantity_change
        
        # SAD PATH 2: Business Rule - Kiểm tra số lượng
        if new_copies < 0:
            raise NotEnoughCopiesError(f"Not enough copies for book id {book_id}")
            
        # HAPPY PATH:
        book.available_copies = new_copies
        self.repo.save(book)
        return book.available_copies # Trả về số lượng mới

    def get_book_by_id(self, book_id, base_url=""):
        """Lấy sách đơn lẻ (Thêm HATEOAS)"""
        # SAD PATH:
        book = self.repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        
        # HAPPY PATH:
        return self.add_hateoas_book(book.to_dict(), base_url)

    # ====================================================================
    # LOGIC PHÂN TRANG VÀ HELPERS (Giữ nguyên)
    # ====================================================================

    def get_books_offset(self, page, limit, author_filter=None, base_url=""):
        """Lấy sách dùng Offset Pagination (Giữ nguyên logic của bạn)"""
        offset = (page - 1) * limit
        total_count = self.repo.get_total_count(author_filter)
        
        books = self.repo.get_all_offset(offset, limit, author_filter)
        result_dicts = [self.add_hateoas_book(book.to_dict(), base_url) for book in books]

        total_pages = (total_count + limit - 1) // limit
        
        response_data = {
            "metadata": {
                "total_records": total_count,
                "page": page, 
                "limit": limit,
                "total_pages": total_pages
            },
            "data": result_dicts,
            "links": self.paginate_links(
                base_url, '/books', limit=limit, 
                current_page=page, total_pages=total_pages, 
                author_filter=author_filter
            )
        }
        return response_data
        
    # (Các hàm get_books_cursor, generate_etag, add_hateoas_book, paginate_links...)
    # (Bạn có thể dán các hàm đó vào đây, chúng không cần thay đổi logic)

    def generate_etag(self, data):
        """Helper: Tạo ETag dựa trên nội dung JSON"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode("utf-8")).hexdigest()

    def add_hateoas_book(self, book_dict, base_url):
        """Thêm link HATEOAS cho resource Book."""
        BASE_URL = base_url
        book_dict['links'] = [
            {"rel": "self", "href": f"{BASE_URL}/books/{book_dict['id']}", "method": "GET"},
            {"rel": "update", "href": f"{BASE_URL}/books/{book_dict['id']}", "method": "PUT"},
            {"rel": "delete", "href": f"{BASE_URL}/books/{book_dict['id']}", "method": "DELETE"},
            {"rel": "borrow", "href": f"{BASE_URL}/transactions", "method": "POST"}
        ]
        return book_dict

    def paginate_links(self, base_url, endpoint, limit,
                       current_page=None, total_pages=None,
                       next_cursor=None, prev_cursor=None, 
                       author_filter=None):
        links = {}
        BASE_URL = base_url
        filter_query = f"&author_filter={author_filter}" if author_filter else ""
        
        if current_page is not None and total_pages is not None:
            links['first'] = f"{BASE_URL}{endpoint}?page=1&limit={limit}{filter_query}"
            if current_page > 1:
                links['prev'] = f"{BASE_URL}{endpoint}?page={current_page - 1}&limit={limit}{filter_query}"
            if current_page < total_pages:
                links['next'] = f"{BASE_URL}{endpoint}?page={current_page + 1}&limit={limit}{filter_query}"
            links['last'] = f"{BASE_URL}{endpoint}?page={total_pages}&limit={limit}{filter_query}"
        
        elif next_cursor is not None or prev_cursor is not None:
             # (Logic cursor của bạn)
             pass 
        return links