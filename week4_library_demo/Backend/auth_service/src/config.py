# File: auth_service/src/config.py

import os
from urllib.parse import quote_plus

# Cố gắng load .env (Cho môi trường Local Dev)
# Trong Docker, biến môi trường được truyền qua docker-compose nên dòng này có thể bỏ qua nếu lỗi
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """
    Cấu hình Auth Service.
    Ưu tiên lấy cấu hình từ biến môi trường (Docker).
    """

    # ==========================================================
    # 1. CẤU HÌNH DATABASE (QUAN TRỌNG)
    # ==========================================================
    
    # Kiểm tra xem Docker có truyền chuỗi kết nối đầy đủ không
    _db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI")

    if _db_uri:
        # [TRƯỜNG HỢP DOCKER] Dùng luôn chuỗi từ docker-compose
        SQLALCHEMY_DATABASE_URI = _db_uri
    else:
        # [TRƯỜNG HỢP LOCAL] Tự ghép chuỗi từ các biến lẻ
        print("⚠️ Không tìm thấy SQLALCHEMY_DATABASE_URI, đang tự tạo từ các biến DB_...")
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_PORT = os.environ.get("DB_PORT", "3306")
        DB_USER = os.environ.get("DB_USER", "root")
        DB_PASS = os.environ.get("DB_PASSWORD", "")
        DB_NAME = os.environ.get("DB_DATABASE", "auth_db")
        
        encoded_pass = quote_plus(DB_PASS)
        SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Cấu hình Pool kết nối (Tối ưu cho Production)
    SQLALCHEMY_POOL_SIZE = 20          # Số kết nối giữ sẵn
    SQLALCHEMY_MAX_OVERFLOW = 10       # Số kết nối vượt mức cho phép
    SQLALCHEMY_POOL_RECYCLE = 3600     # Tự động tái tạo kết nối sau 1 giờ
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================================
    # 2. CẤU HÌNH BẢO MẬT (JWT & SESSION)
    # ==========================================================
    
    # Secret Key cho Flask Session
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("FLASK_SECRET_KEY") or "dev_secret_key_mac_dinh"
    
    # JWT Keys
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt_secret_mac_dinh")
    JWT_REFRESH_SECRET_KEY = os.environ.get("JWT_REFRESH_SECRET_KEY", "jwt_refresh_secret_mac_dinh")

    # Session Settings
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Cookie Settings (Tự động Secure nếu là Production)
    is_prod = os.environ.get("FLASK_ENV") == "production"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", str(is_prod)).lower() == "true"
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")

    # ==========================================================
    # 3. CẤU HÌNH OAUTH (GOOGLE)
    # ==========================================================
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    
    # URL Gateway Public để Google redirect về đúng chỗ
    GATEWAY_PUBLIC_URL = os.environ.get("GATEWAY_PUBLIC_URL", "http://localhost:8080")
    GOOGLE_REDIRECT_URI = f"{GATEWAY_PUBLIC_URL}/api/auth/google/callback"