from ..database import db
from sqlalchemy import Enum, String  # <-- ĐÃ SỬA: Dùng String, bỏ mysql
from uuid import uuid4
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    # --- ĐÃ SỬA ---
    # Dùng String(36) thay vì kiểu UUID của MySQL
    # default phải là lambda để trả về string
    id = db.Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(String(36), nullable=False, index=True)
    # --- KẾT THÚC SỬA ---
    
    book_id = db.Column(db.Integer, nullable=False)
    
    # Dòng Enum này đã đúng từ lần sửa trước
    type = db.Column(Enum('borrow', 'return', name='transaction_type'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'book_id': self.book_id,
            'type': self.type,
            'quantity': self.quantity,
            'transaction_date': self.transaction_date.isoformat()
        }