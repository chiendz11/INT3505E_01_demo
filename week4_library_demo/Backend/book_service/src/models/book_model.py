# book_service/src/models/book_model.py

# Import này đã chính xác!
from ..database import db

# Định nghĩa Book Model
class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    available_copies = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        """Chuyển đổi đối tượng Model sang Dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
        }