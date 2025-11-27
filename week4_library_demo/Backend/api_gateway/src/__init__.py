# api_gateway/src/__init__.py

from flask import Flask
from flask_cors import CORS
from .config import Config

# [LESSON 10] Thêm thư viện Monitoring & Security
from flask import request

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Lấy Origin của Frontend từ Config
    frontend_origin = app.config.get('FRONTEND_ORIGIN')
    swagger_ui_origin = "https://app.swaggerhub.com" # Đã sửa lỗi chính tả
    
    # --- Cấu hình CORS ---
    CORS(
        app,
        resources={r"/api/*": {"origins": [frontend_origin, swagger_ui_origin]}},
        supports_credentials=True, 
        allow_headers=['Content-Type', 'Authorization', 'If-None-Match', 'X-User-ID', 'X-User-Role'], 
    )

    # ====================================================================
    # [LESSON 10] CẤU HÌNH GATEWAY MONITORING & SECURITY
    # ====================================================================
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
    
    # 2. Prometheus Metrics (Đo traffic tổng của cả hệ thống)
    # Gateway là nơi tốt nhất để đo xem hệ thống có bao nhiêu request
    metrics = PrometheusMetrics(app)
    metrics.info('gateway_info', 'API Gateway', version='1.0.0')

    # ====================================================================

    # Đăng ký các blueprint
    from .routes.auth_routes import auth_bp
    from .routes.book_routes import book_bp
    from .routes.transaction_routes import transaction_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(book_bp, url_prefix='/api')
    app.register_blueprint(transaction_bp, url_prefix='/api')

    @app.route('/health')
    def health_check():
        return "API Gateway OK"

    return app