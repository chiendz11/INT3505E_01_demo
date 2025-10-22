from ..database import db
from ..models.transaction_model import Transaction
from sqlalchemy import func, case
import uuid

class TransactionRepository:
    def add(self, transaction):
        db.session.add(transaction)
        db.session.commit()
        return transaction

    def get_by_user_id(self, user_id):
        """Lấy toàn bộ lịch sử giao dịch của user."""
        return Transaction.query.filter_by(user_id=str(user_id)).order_by(Transaction.transaction_date.desc()).all()

    def get_currently_borrowed_by_user_id(self, user_id):
        """
        TÍNH TOÁN và trả về danh sách các sách đang được mượn.
        Chỉ truy vấn những sách có tổng mượn > tổng trả.
        """
        # Biểu thức tính toán: +quantity nếu là 'borrow', -quantity nếu là 'return'
        quantity_case = case(
            (Transaction.type == 'borrow', Transaction.quantity),
            (Transaction.type == 'return', -Transaction.quantity)
        )

        # Query để nhóm theo book_id và tính tổng số lượng ròng (net quantity)
        borrowed_summary = db.session.query(
            Transaction.book_id,
            func.sum(quantity_case).label('borrowed_count')
        ).filter(
            Transaction.user_id == str(user_id) # So sánh với chuỗi UUID
        ).group_by(
            Transaction.book_id
        ).having(
            func.sum(quantity_case) > 0  # Chỉ lấy những sách có số lượng đang mượn > 0
        ).all()
        
        return borrowed_summary

