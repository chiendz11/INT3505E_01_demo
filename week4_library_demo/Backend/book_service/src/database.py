# book_service/src/repositories/database.py

from flask_sqlalchemy import SQLAlchemy

# Chỉ khởi tạo, *không* gắn vào app
# Việc gắn app (db.init_app(app)) sẽ được làm trong __init__.py
db = SQLAlchemy()