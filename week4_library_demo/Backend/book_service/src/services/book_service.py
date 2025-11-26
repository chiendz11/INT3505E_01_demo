import json
import hashlib
from ..repositories.book_repository import BookRepository
from ..exceptions import (
    BookNotFoundError, BookAlreadyExistsError, 
    InvalidBookDataError, NotEnoughCopiesError
)
from ..models.book_model import Book 

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    # ============================================================
    # VERSIONING RESPONSE
    # ============================================================

    def book_to_v1_dict(self, book_obj, base_url=""):
        """V1 Response: sử dụng available_copies (alias từ stock_count)"""
        return self.add_hateoas_book({
            'id': book_obj.id,
            'title': book_obj.title,
            'author': book_obj.author,
            'available_copies': book_obj.stock_count
        }, base_url)


    def book_to_v2_dict(self, book_obj, base_url=""):
        """V2 Response: sử dụng stock_count (field chuẩn mới)"""
        return self.add_hateoas_book({
            'id': book_obj.id,
            'title': book_obj.title,
            'author': book_obj.author,
            'stock_count': book_obj.stock_count
        }, base_url)


    def get_book_by_id(self, book_id, base_url="", version='v1'):
        book = self.repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        
        if version == 'v2':
            return self.book_to_v2_dict(book, base_url)
        return self.book_to_v1_dict(book, base_url)


    # ============================================================
    # CRUD LOGIC
    # ============================================================

    def create_book(self, data):
        title = data.get('title')
        author = data.get('author')
        
        if not title or not author:
            raise InvalidBookDataError("Title and Author cannot be empty")
            
        if self.repo.find_by_title_and_author(title, author):
            raise BookAlreadyExistsError(f"Book '{title}' by {author} already exists")
            
        # ✅ Ưu tiên stock_count (V2) - fallback available_copies
        copies = data.get('stock_count', data.get('available_copies', 0))
        new_book = Book(title=title, author=author, stock_count=copies)
        
        return self.repo.save(new_book)


    def update_book(self, book_id, data):
        book = self.repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        
        if 'title' in data:
            book.title = data['title']
        if 'author' in data:
            book.author = data['author']
        
        # ✅ Hỗ trợ cả 2 version
        if 'stock_count' in data:
            book.stock_count = data['stock_count']
        elif 'available_copies' in data:
            book.stock_count = data['available_copies']
        
        if not book.title or not book.author:
            raise InvalidBookDataError("Title and Author cannot be empty")
            
        return self.repo.save(book)


    def delete_book(self, book_id):
        book = self.repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        return self.repo.delete(book)


    def check_and_update_copies(self, book_id, quantity, tran_type):
        if quantity <= 0:
             raise InvalidBookDataError("Quantity must be positive")

        quantity_change = quantity if tran_type == 'return' else -quantity
        
        try:
            updated_book = self.repo.update_copies_atomically(book_id, quantity_change)
            return updated_book.stock_count

        except Exception as e:
            if "Not found" in str(e):
                raise BookNotFoundError(f"Book with id {book_id} not found")
            if "check constraint" in str(e) or "out of stock" in str(e):
                 raise NotEnoughCopiesError(f"Not enough copies for book id {book_id}")
            raise e


    # ============================================================
    # HELPERS (Giữ nguyên)
    # ============================================================

    def get_books_offset(self, page, limit, author_filter=None, base_url=""):
        offset = (page - 1) * limit
        total_count = self.repo.get_total_count(author_filter)
        
        books = self.repo.get_all_offset(offset, limit, author_filter)
        result_dicts = [self.add_hateoas_book(book.to_dict(), base_url) for book in books]

        total_pages = (total_count + limit - 1) // limit
        
        return {
            "metadata": {
                "total_records": total_count,
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "pagination_strategy": "offset_limit"
            },
            "data": result_dicts,
            "links": self.paginate_links(
                base_url, '/books', limit=limit, 
                current_page=page, total_pages=total_pages, 
                author_filter=author_filter
            )
        }


    def generate_etag(self, data):
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode("utf-8")).hexdigest()


    def add_hateoas_book(self, book_dict, base_url):
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
            links['self'] = f"{BASE_URL}{endpoint}?page={current_page}&limit={limit}{filter_query}"
            links['first'] = f"{BASE_URL}{endpoint}?page=1&limit={limit}{filter_query}"
            if current_page > 1:
                links['prev'] = f"{BASE_URL}{endpoint}?page={current_page - 1}&limit={limit}{filter_query}"
            if current_page < total_pages:
                links['next'] = f"{BASE_URL}{endpoint}?page={current_page + 1}&limit={limit}{filter_query}"
            if total_pages > 0:
                links['last'] = f"{BASE_URL}{endpoint}?page={total_pages}&limit={limit}{filter_query}"
        return links
