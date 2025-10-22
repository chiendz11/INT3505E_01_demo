from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Lấy Origin của Frontend từ Config
    frontend_origin = app.config.get('FRONTEND_ORIGIN')
    
    # --- Cấu hình CORS ---
    # Thiết lập CORS chỉ cho phép Frontend Origin đã được cấu hình
    CORS(
        app,
        resources={r"/api/*": {"origins": [frontend_origin]}}, # CHỈ cho phép Origin đã được định nghĩa trong FRONTEND_ORIGIN
        supports_credentials=True, # Cho phép gửi cookies/headers xác thực
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
