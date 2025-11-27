# book_service/src/__init__.py

from flask import Flask
from .config import Config      # <-- 1. Import lớp Config mới
from .database import db         # <-- 2. Import 'db' từ file database.py ở cấp src
from .controllers.book_controller import book_bp
from .controllers.book_internal_controller import book_internal_bp

from flask import request

# [LESSON 10] Import Flask-Limiter
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    """Hàm Factory để tạo và cấu hình ứng dụng Flask."""
    
    app = Flask(__name__)

    # 3. Tải toàn bộ cấu hình từ lớp Config
    app.config.from_object(Config)

    # ====================================================================
    # [LESSON 10] CẤU HÌNH RATE LIMITER (SECURITY)
    # ====================================================================
    # Khởi tạo Limiter:
    # - key_func: Định danh user dựa trên IP (get_remote_address)
    # - default_limits: Giới hạn mặc định cho toàn bộ API (nếu không set riêng)
    def should_exempt():
        return request.path == "/metrics"
    
    # 1. Rate Limiter (Gateway chặn tổng thể: 1000 req/giờ mỗi IP)
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["2000 per day", "500 per hour"],
        storage_uri="memory://",
    )
    limiter.request_filter(should_exempt)
    
    # Lưu limiter vào app.extensions để có thể gọi ở Controller/Blueprint
    app.extensions['limiter'] = limiter

    # Tự động tạo endpoint /metrics
    metrics = PrometheusMetrics(app)
    
    # (Tùy chọn) Thêm thông tin tĩnh về app
    metrics.info('app_info', 'Application info', version='1.0.0')

    # 4. Khởi tạo SQLAlchemy với Flask App
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # 5. Đăng ký Blueprint
    app.register_blueprint(book_bp)
    app.register_blueprint(book_internal_bp)

    print("Book Service Application Created Successfully!")
    return app