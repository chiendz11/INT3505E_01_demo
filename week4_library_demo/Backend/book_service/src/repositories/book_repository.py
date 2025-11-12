# book_service/src/repositories/book_repository.py

from ..database import db
from ..models.book_model import Book
from sqlalchemy import func

class BookRepository:
    """Tầng Repository: Chỉ nói chuyện với DB, không có logic nghiệp vụ."""

    def get_by_id(self, book_id):
        """Lấy một sách theo ID"""
        return Book.query.get(book_id)

    def find_by_title_and_author(self, title, author):
        """Tìm sách theo title và author (cho logic kiểm tra trùng lặp)"""
        return Book.query.filter_by(title=title, author=author).first()

    def get_total_count(self, author_filter=None):
        """Lấy tổng số bản ghi"""
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
        """Lấy sách theo Cursor-Based Pagination"""
        # (Giữ nguyên logic get_all_cursor của bạn... nó đã khá tốt)
        query = Book.query
        if author_filter:
            query = query.filter(func.lower(Book.author) == func.lower(author_filter))
        if cursor_id is not None:
            query = query.filter(Book.id > cursor_id)
        return query.order_by(Book.id.asc()).limit(limit).all()

    def save(self, book):
        """Lưu một đối tượng book (tạo mới hoặc cập nhật)"""
        db.session.add(book)
        db.session.commit()
        return book

    def delete(self, book):
        """Xóa một đối tượng book (đã được lấy ra từ DB)"""
        db.session.delete(book)
        db.session.commit()
        return True