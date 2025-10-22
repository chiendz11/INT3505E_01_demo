from flask import Flask, session
from flask_session import Session
from flask_bcrypt import Bcrypt
from .config import Config
from .database import db
from .controllers.auth_controller import auth_bp
from .services.oauth_service import init_oauth
import os

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    print("FLASK SECRET_KEY:", app.config.get("SECRET_KEY"))

    # 🧩 Thư mục lưu session
    SESSION_DIR = os.path.join(os.getcwd(), "flask_sessions")
    os.makedirs(SESSION_DIR, exist_ok=True)

    # ✅ Cấu hình session (đã sửa chi tiết)
    app.config.update({
        "SESSION_TYPE": "filesystem",
        "SESSION_FILE_DIR": SESSION_DIR,
        "SESSION_PERMANENT": False,
        "SESSION_USE_SIGNER": True,
        "SESSION_REFRESH_EACH_REQUEST": True,   # ⚡ đảm bảo cookie luôn được gửi
        "SESSION_COOKIE_NAME": "flask_auth_session",
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",      # ⚠️ BẮT BUỘC None nếu khác port
        "SESSION_COOKIE_SECURE": False,         # ⚠️ True nếu HTTPS
    })

    # ⚡ Phải khởi tạo Session SAU config
    Session(app)

    # Debug session
    @app.before_request
    def debug_before():
        print("📂 SESSION BEFORE:", dict(session))

    @app.after_request
    def debug_after(response):
        print("📤 SESSION AFTER:", dict(session))
        print("🍪 Set-Cookie:", response.headers.get("Set-Cookie"))
        return response

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
