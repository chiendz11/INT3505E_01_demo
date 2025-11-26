# book_service/src/models/book_model.py

# Import này đã chính xác!
from ..database import db

# Định nghĩa Book Model
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    # ✅ NEW FIELD (V2 - field chính trong DB)
    stock_count = db.Column(db.Integer, nullable=False, default=0)


    # ❗ Giữ available_copies để tương thích ngược với logic cũ (V1)
    # Field này KHÔNG còn là nguồn dữ liệu chính
    @property
    def available_copies(self):
        return self.stock_count


    @available_copies.setter
    def available_copies(self, value):
        self.stock_count = value


    def to_dict(self):
        """Dữ liệu gốc từ DB (chuẩn theo V2)"""
        return {
        'id': self.id,
        'title': self.title,
        'author': self.author,
        'stock_count': self.stock_count
        }