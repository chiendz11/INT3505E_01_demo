# book_service/src/__init__.py

from flask import Flask
from .config import Config      # <-- 1. Import lớp Config mới
from .database import db         # <-- 2. Import 'db' từ file database.py ở cấp src
from .controllers.book_controller import book_bp
from .controllers.book_internal_controller import book_internal_bp

def create_app():
    """Hàm Factory để tạo và cấu hình ứng dụng Flask."""
    
    app = Flask(__name__)

    # 3. Tải toàn bộ cấu hình từ lớp Config
    # Dòng này sẽ tự động đọc 'SQLALCHEMY_DATABASE_URI' và các biến khác
    app.config.from_object(Config)

    # 4. Khởi tạo SQLAlchemy với Flask App
    db.init_app(app)

    # (Tùy chọn) Lệnh này hữu ích khi phát triển: tự tạo bảng nếu chưa có
    # Khi deploy thực tế, bạn nên dùng công cụ migration như Alembic
    with app.app_context():
        db.create_all()

    # 5. Đăng ký Blueprint
    app.register_blueprint(book_bp)
    app.register_blueprint(book_internal_bp)

    print("Book Service Application Created Successfully!")
    return app
