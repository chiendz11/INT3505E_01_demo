import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Tải các biến từ file .env
load_dotenv()

class Config:
    """Lớp Config, đọc các biến từ môi trường để kết nối MySQL."""

    # Đọc các biến môi trường cho database
    DB_HOST = os.environ.get("DB_HOST")
    DB_PORT = os.environ.get("DB_PORT")
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD_RAW = os.environ.get("DB_PASSWORD")
    DB_DATABASE = os.environ.get("DB_DATABASE")
    
    # Kiểm tra các biến bắt buộc của database
    if not all([DB_HOST, DB_PORT, DB_USER, DB_PASSWORD_RAW, DB_DATABASE]):
        raise ValueError("Một hoặc nhiều biến môi trường database (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE) chưa được thiết lập.")

    # Mã hóa mật khẩu để xử lý các ký tự đặc biệt một cách an toàn
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD_RAW)

    # Xây dựng chuỗi kết nối cho SQLAlchemy với driver mysqlconnector
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD_ENCODED}@"
        f"{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
    
    # ✅ ==========================================================
    # ✅ THÊM 3 DÒNG NÀY ĐỂ SỬA LỖI NGHẼN CỔ CHAI (BOTTLENECK)
    # ✅ ==========================================================
    
    # Tăng "bể" kết nối chính (mặc định chỉ là 5)
    SQLALCHEMY_POOL_SIZE = 50
    
    # Cho phép tạo thêm kết nối "vượt" khi bể đầy
    SQLALCHEMY_MAX_OVERFLOW = 20
    
    # Tự động làm mới kết nối sau 300 giây (rất tốt cho MySQL)
    SQLALCHEMY_POOL_RECYCLE = 300
    
    # ==========================================================
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False