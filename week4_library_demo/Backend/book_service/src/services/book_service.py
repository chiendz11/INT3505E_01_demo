import json
import hashlib
# ❌ ĐÃ XÓA: from flask import request

# Khởi tạo Repository để giao tiếp với DB
from ..repositories.book_repository import BookRepository

class BookService:
    def __init__(self):
        self.repo = BookRepository()

    def generate_etag(self, data):
        """Helper: Tạo ETag dựa trên nội dung JSON"""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode("utf-8")).hexdigest()

    def add_hateoas_book(self, book_dict, base_url):
        """
        Thêm link HATEOAS cho resource Book.
        Nhận 'base_url' từ bên ngoài.
        """
        BASE_URL = base_url # Dùng base_url được truyền vào
        book_dict['links'] = [
            {"rel": "self", "href": f"{BASE_URL}/books/{book_dict['id']}", "method": "GET"},
            {"rel": "update", "href": f"{BASE_URL}/books/{book_dict['id']}", "method": "PUT"},
            {"rel": "delete", "href": f"{BASE_URL}/books/{book_dict['id']}", "method": "DELETE"},
            {"rel": "borrow", "href": f"{BASE_URL}/transactions", "method": "POST"}
        ]
        return book_dict

    def paginate_links(self, base_url, endpoint, limit,
                       # Dùng cho Offset
                       current_page=None, total_pages=None,
                       # Dùng cho Cursor
                       next_cursor=None, prev_cursor=None, 
                       # Dùng cho cả hai
                       author_filter=None):
        links = {}
        BASE_URL = base_url # Dùng base_url được truyền vào
        
        filter_query = f"&author_filter={author_filter}" if author_filter else ""
        
        # --- Logic Offset-based Pagination ---
        if current_page is not None and total_pages is not None:
            links['first'] = f"{BASE_URL}{endpoint}?page=1&limit={limit}{filter_query}"
            if current_page > 1:
                links['prev'] = f"{BASE_URL}{endpoint}?page={current_page - 1}&limit={limit}{filter_query}"
            if current_page < total_pages:
                links['next'] = f"{BASE_URL}{endpoint}?page={current_page + 1}&limit={limit}{filter_query}"
            links['last'] = f"{BASE_URL}{endpoint}?page={total_pages}&limit={limit}{filter_query}"

        # --- Logic Cursor-based Pagination ---
        elif next_cursor is not None or prev_cursor is not None:
            if next_cursor is not None:
                links['next'] = f"{BASE_URL}{endpoint}?limit={limit}&after_cursor={next_cursor}{filter_query}"
            if prev_cursor is not None:
                links['prev'] = f"{BASE_URL}{endpoint}?limit={limit}&before_cursor={prev_cursor}{filter_query}"
            links['first'] = f"{BASE_URL}{endpoint}?limit={limit}{filter_query}"

        return links
        

    # ====================================================================
    # LOGIC NGHIỆP VỤ
    # ====================================================================

    def get_books_offset(self, page, limit, author_filter=None, base_url=""):
        """Lấy sách dùng Offset Pagination (nhận base_url)"""
        offset = (page - 1) * limit
        total_count = self.repo.get_total_count(author_filter)
        
        books = self.repo.get_all_offset(offset, limit, author_filter)
        # ✅ Truyền base_url vào
        result_dicts = [self.add_hateoas_book(book.to_dict(), base_url) for book in books]

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
            # ✅ Truyền base_url vào
            "links": self.paginate_links(
                base_url, '/books', limit=limit, 
                current_page=page, total_pages=total_pages, 
                author_filter=author_filter
            )
        }
        return response_data

    def get_books_cursor(self, limit, cursor_value=None, direction='forward', author_filter=None, base_url=""):
        """Lấy sách dùng Cursor Pagination (nhận base_url)"""
        fetch_limit = limit + 1
        start_point = cursor_value
        
        books = self.repo.get_all_cursor(
            fetch_limit, 
            start_point, 
            direction, 
            author_filter
        )
        
        has_more = len(books) == fetch_limit
        
        if direction == 'backward':
            result_books = books[1:] if has_more else books 
            result_books.reverse()
        else:
            result_books = books[:limit]
        
        next_cursor = result_books[-1].id if result_books and has_more else None
        prev_cursor = result_books[0].id if result_books else None
        
        # ✅ Truyền base_url vào
        result_dicts = [self.add_hateoas_book(book.to_dict(), base_url) for book in result_books]
        
        response_data = {
            "metadata": {
                "pagination_strategy": "cursor_based",
                "limit": limit,
                "cursor_direction": direction,
                "used_cursor": cursor_value,
                "has_more": has_more,
                "next_cursor": next_cursor, 
                "prev_cursor": prev_cursor  
            },
            "data": result_dicts,
            # ✅ Truyền base_url vào
            "links": self.paginate_links(
                base_url, '/books', limit=limit, 
                next_cursor=next_cursor, prev_cursor=prev_cursor, 
                author_filter=author_filter
            ) 
        }
        return response_data

    def get_book_by_id(self, book_id, base_url=""):
        """Lấy sách đơn lẻ (nhận base_url)"""
        book = self.repo.get_by_id(book_id)
        if book:
            # ✅ Truyền base_url vào
            return self.add_hateoas_book(book.to_dict(), base_url)
        return None

    # ... (Các hàm create, update, delete, check_and_update_copies không cần base_url) ...

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
        """Dùng cho Transaction Service."""
        quantity_change = quantity if tran_type == 'return' else -quantity
        
        status, new_copies = self.repo.update_copies(book_id, quantity_change)
        
        if status == "Success":
            return True, None
        
        return False, status