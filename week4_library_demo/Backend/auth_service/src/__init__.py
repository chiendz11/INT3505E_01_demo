# auth_service/src/__init__.py

from flask import Flask, session
from flask_session import Session
from flask_bcrypt import Bcrypt
from .config import Config
from .database import db
from .controllers.auth_controller import auth_bp
from .services.oauth_service import init_oauth
import os

# [LESSON 10] Import
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics
from flask import request


bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- SESSION CONFIG ---
    SESSION_DIR = os.path.join(os.getcwd(), "flask_sessions")
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    # Kiểm tra môi trường để set Secure Cookie
    is_production = os.environ.get('FLASK_ENV') == 'production'

    app.config.update({
        "SESSION_TYPE": "filesystem",
        "SESSION_FILE_DIR": SESSION_DIR,
        "SESSION_PERMANENT": False,
        "SESSION_USE_SIGNER": True,
        "SESSION_REFRESH_EACH_REQUEST": True,
        "SESSION_COOKIE_NAME": "flask_auth_session",
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        # [PRODUCTION] Tự động bật Secure nếu là Prod
        "SESSION_COOKIE_SECURE": is_production, 
    })

    Session(app)

    # ====================================================================
    # [LESSON 10] AUTH SECURITY
    # ====================================================================
    # Rate Limit cho Auth Service (Quan trọng để chống dò mật khẩu)
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
    app.extensions['limiter'] = limiter

    # Metrics
    metrics = PrometheusMetrics(app)
    
    # ====================================================================

    db.init_app(app)
    bcrypt.init_app(app)
    init_oauth(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp, url_prefix="/auth")

    @app.route("/health")
    def health():
        return "Auth Service OK"

    return app