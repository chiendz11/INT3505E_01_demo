from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Lấy Origin của Frontend từ Config
    frontend_origin = app.config.get('FRONTEND_ORIGIN')
    swager_ui_origin = "https://app.swaggerhub.com"
    
    # --- Cấu hình CORS ---
    # Thiết lập CORS chỉ cho phép Frontend Origin đã được cấu hình
    CORS(
        app,
        resources={r"/api/*": {"origins": [frontend_origin, swager_ui_origin]}},
        supports_credentials=True, 
        # !!! THÊM THAM SỐ allowed_headers !!!
        # Cần thêm 'If-None-Match' để hỗ trợ ETag.
        # Thêm 'Content-Type' và 'Authorization' (nếu dùng cho token/cookies) là thực tế.
        allow_headers=['Content-Type', 'Authorization', 'If-None-Match'], 
    )

    # Đăng ký các blueprint với một prefix chung là /api
    from .routes.auth_routes import auth_bp
    from .routes.book_routes import book_bp
    from .routes.transaction_routes import transaction_bp
    
    # Mọi route trong auth_bp và book_bp giờ sẽ bắt đầu bằng /api
    # CORS đã được áp dụng ở trên
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(book_bp, url_prefix='/api')
    app.register_blueprint(transaction_bp, url_prefix='/api')

    @app.route('/health')
    def health_check():
        return "API Gateway OK"

    return app
