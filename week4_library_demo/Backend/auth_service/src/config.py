import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Tải các biến từ file .env
load_dotenv()

class Config:
    """Lớp Config, đọc các biến từ môi trường cho Database, JWT, và OAuth."""

    # --- Cấu hình Database ---
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD_RAW = os.environ.get("DB_PASSWORD")
    DB_DATABASE = os.environ.get("DB_DATABASE")
    
    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD_RAW, DB_DATABASE]):
        raise ValueError("Một hoặc nhiều biến môi trường database chưa được thiết lập.")

    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD_ENCODED}@"
        f"{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- Cấu hình JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY = os.environ.get("JWT_REFRESH_SECRET_KEY")

    if not all([JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY]):
        raise ValueError("JWT_SECRET_KEY và JWT_REFRESH_SECRET_KEY phải được thiết lập.")

    # --- Cấu hình Flask Session (BẮT BUỘC) ---
    # Tên biến này PHẢI là SECRET_KEY để Flask có thể mã hóa Session.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    
    # --- Cấu hình Google OAuth 2.0 ---
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not SECRET_KEY:
         raise ValueError("FLASK_SECRET_KEY (được ánh xạ thành SECRET_KEY) phải được thiết lập.")

    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
        raise ValueError("GOOGLE_CLIENT_ID và GOOGLE_CLIENT_SECRET phải được thiết lập để sử dụng đăng nhập Google.")
    
    # --- Cấu hình Session (rất quan trọng để giữ state giữa login và callback) ---
    SESSION_TYPE = "filesystem"  # hoặc 'redis' nếu bạn dùng Redis để lưu session
    SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "None")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_PERMANENT = False  # tránh session bị giữ quá lâu
    GATEWAY_PUBLIC_URL = os.environ.get("GATEWAY_PUBLIC_URL") 
    GOOGLE_REDIRECT_URI = f"{GATEWAY_PUBLIC_URL}/api/auth/google/callback"
     # Tăng "bể" kết nối chính (mặc định chỉ là 5)
    SQLALCHEMY_POOL_SIZE = 50
    
    # Cho phép tạo thêm kết nối "vượt" khi bể đầy
    SQLALCHEMY_MAX_OVERFLOW = 20
    
    # Tự động làm mới kết nối sau 300 giây (rất tốt cho MySQL)
    SQLALCHEMY_POOL_RECYCLE = 300
    
    # ==========================================================
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
