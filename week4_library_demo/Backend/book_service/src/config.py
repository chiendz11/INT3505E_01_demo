# File: book_service/src/config.py

import os
from urllib.parse import quote_plus

# Cố gắng load .env (Cho môi trường Local Dev)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    """
    Cấu hình Book Service.
    Ưu tiên lấy cấu hình từ biến môi trường (Docker).
    """

    # ==========================================================
    # 1. CẤU HÌNH DATABASE (QUAN TRỌNG)
    # ==========================================================
    
    # Kiểm tra xem Docker có truyền chuỗi kết nối đầy đủ không
    _db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI")

    if _db_uri:
        # [TRƯỜNG HỢP DOCKER] Dùng luôn chuỗi từ docker-compose
        # (Sẽ kết nối đến host 'db' thay vì '127.0.0.1')
        SQLALCHEMY_DATABASE_URI = _db_uri
    else:
        # [TRƯỜNG HỢP LOCAL] Tự ghép chuỗi từ các biến lẻ (nếu chạy tay python app.py)
        print("⚠️ [BookService] Không tìm thấy SQLALCHEMY_DATABASE_URI, đang tự tạo từ các biến DB_...")
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_PORT = os.environ.get("DB_PORT", "3306")
        DB_USER = os.environ.get("DB_USER", "root")
        DB_PASS = os.environ.get("DB_PASSWORD", "")
        DB_NAME = os.environ.get("DB_DATABASE", "book_db") # Mặc định là book_db
        
        encoded_pass = quote_plus(DB_PASS)
        SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # ==========================================================
    # 2. TỐI ƯU HIỆU NĂNG (CONNECTION POOL)
    # ==========================================================
    # Giúp service chịu tải tốt hơn, tránh lỗi "Too many connections"
    
    SQLALCHEMY_POOL_SIZE = 20          # Số kết nối giữ sẵn
    SQLALCHEMY_MAX_OVERFLOW = 10       # Số kết nối tạo thêm khi quá tải
    SQLALCHEMY_POOL_RECYCLE = 3600     # Tự động tái tạo kết nối sau 1 giờ (3600s)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False