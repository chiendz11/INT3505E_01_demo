from ..database import db  # <-- SỬA Ở ĐÂY: import từ file cùng cấp
from ..models.book_model import Book  # <-- Import này đã đúng
from sqlalchemy import func

class BookRepository:
    """Tầng Repository: Chịu trách nhiệm giao tiếp với Database thông qua SQLAlchemy."""

    def get_total_count(self, author_filter=None):
        """Lấy tổng số bản ghi (dùng cho offset pagination)"""
        query = db.session.query(func.count(Book.id))
        if author_filter:
            query = query.filter(func.lower(Book.author) == func.lower(author_filter))
        return query.scalar()

    def get_all_offset(self, offset, limit, author_filter=None):
        """Lấy sách theo OFFSET/LIMIT"""
        query = Book.query
        if author_filter:
            query = query.filter(func.lower(Book.author) == func.lower(author_filter))
            
        return query.order_by(Book.id.asc()).offset(offset).limit(limit).all()

    def get_all_cursor(self, limit, cursor_id=None, author_filter=None):
        """Lấy sách theo Cursor-Based Pagination (Keyset)"""
        query = Book.query

        if author_filter:
            query = query.filter(func.lower(Book.author) == func.lower(author_filter))

        if cursor_id is not None:
            # Lấy các ID lớn hơn cursor_id
            query = query.filter(Book.id > cursor_id)
            
        return query.order_by(Book.id.asc()).limit(limit).all()

    def get_by_id(self, book_id):
        """Lấy một sách theo ID"""
        return Book.query.get(book_id)

    def create(self, title, author, available_copies):
        """Tạo sách mới"""
        new_book = Book(title=title, author=author, available_copies=available_copies)
        db.session.add(new_book)
        db.session.commit()
        return new_book

    def update(self, book_id, title, author, available_copies):
        """Cập nhật sách"""
        book = self.get_by_id(book_id)
        if book:
            book.title = title
            book.author = author
            book.available_copies = available_copies
            db.session.commit()
            return book
        return None
    
    def update_copies(self, book_id, quantity_change):
        """Cập nhật số lượng sách (dùng cho Transaction Service gọi)"""
        book = self.get_by_id(book_id)
        if book:
            new_copies = book.available_copies + quantity_change
            if new_copies < 0:
                return "Not enough copies", None
            
            book.available_copies = new_copies
            db.session.commit()
            return "Success", book.available_copies
        return "Book not found", None


    def delete(self, book_id):
        """Xóa sách"""
        book = self.get_by_id(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return True
        return False
