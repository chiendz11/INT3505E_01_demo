from ..database import db
from uuid import uuid4
from datetime import datetime
from sqlalchemy import UniqueConstraint # <-- 1. IMPORT THÊM

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=True)
    hashed_password = db.Column(db.String(255), nullable=True)
    
    # --- [MỚI] Thêm 2 trường cho V2 ---
    full_name = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(1024), nullable=True) # Dùng 1024 cho URL dài
    # --- --------------------------- ---

    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    oauth_identities = db.relationship('OAuthIdentity', backref='user', lazy=True, cascade="all, delete-orphan")


class OAuthIdentity(db.Model):
    """Bảng mới để lưu liên kết tài khoản mạng xã hội."""
    __tablename__ = 'oauth_identities'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True) # Thêm index để tra cứu nhanh hơn
    provider = db.Column(db.String(50), nullable=False)
    provider_user_id = db.Column(db.String(255), nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user'),
    )

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True) # Thêm index
    jti = db.Column(db.String(255), unique=True, nullable=False)
    is_revoked = db.Column(db.Boolean, nullable=False, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)