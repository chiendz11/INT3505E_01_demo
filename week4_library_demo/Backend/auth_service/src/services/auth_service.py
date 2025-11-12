# auth_service/src/services/auth_service.py

import jwt
import uuid
from datetime import datetime, timedelta
from flask import current_app
from flask_bcrypt import Bcrypt
from ..models.user_model import User, RefreshToken
from ..repositories.user_repository import UserRepository
from sqlalchemy.orm import joinedload, selectinload

# ✅ BƯỚC 1: Import các exception (Giả sử bạn đã tạo file exceptions.py)
from ..exceptions import (
    AuthError, InvalidLoginError, UserInactiveError, 
    UserAlreadyExistsError, InvalidTokenError
)

bcrypt = Bcrypt()

class AuthService:
    def __init__(self):
        self.repo = UserRepository()

    def register_user(self, email, username, password):
        """
        Đăng ký user.
        Ném ra Exception nếu thất bại.
        """
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            email=email.lower(),
            username=username.lower(),
            hashed_password=hashed_password,
            role='user' 
        )
        
        user, error = self.repo.add_user(new_user)
        
        # ✅ BƯỚC 2: Dịch lỗi từ Repo -> Exception nghiệp vụ
        if error:
            if 'users_email_key' in error:
                raise UserAlreadyExistsError("Email đã tồn tại")
            if 'users_username_key' in error:
                raise UserAlreadyExistsError("Username đã tồn tại")
            # Lỗi DB chung
            raise AuthError(f"Lỗi không xác định khi đăng ký: {error}")
            
        return user # Trả về user khi thành công

    def login_user(self, login_identifier, password):
        """
        Xác thực người dùng.
        Ném ra Exception nếu thất bại.
        Trả về (user, access_token, refresh_token_data) nếu thành công.
        """
        user = self.repo.get_user_by_login(login_identifier.lower())
        
        # ✅ BƯỚC 2: Ném lỗi cụ thể thay vì return tuple
        if not user or not user.hashed_password or not bcrypt.check_password_hash(user.hashed_password, password):
            raise InvalidLoginError("Email/Username hoặc mật khẩu không chính xác")
        
        if not user.is_active:
            raise UserInactiveError("Tài khoản đã bị khóa")
            
        # 3. Thành công
        access_token = self._generate_access_token(user)
        refresh_token_data = self._generate_refresh_token(user)
        
        # Trả về 3 giá trị khi thành công
        return user, access_token, refresh_token_data
        
    def refresh_access_token(self, refresh_token):
        """Ném ra InvalidTokenError nếu thất bại."""
        try:
            payload = jwt.decode(
                refresh_token,
                current_app.config['JWT_REFRESH_SECRET_KEY'],
                algorithms=['HS256']
            )
            jti = payload['jti']
            user_id = payload['sub']

            # ✅ BƯỚC 2: Ném lỗi cụ thể
            db_token = self.repo.get_refresh_token(jti)
            if not db_token or db_token.expires_at < datetime.utcnow():
                raise InvalidTokenError("Refresh token không hợp lệ hoặc đã hết hạn")
            
            user = self.repo.get_user_by_id(user_id)
            if not user:
                raise InvalidTokenError("Không tìm thấy người dùng của token")
            
            # Chỉ trả về access token khi thành công
            return self._generate_access_token(user)

        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Refresh token đã hết hạn")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Refresh token không hợp lệ")

    def logout_user(self, refresh_token):
        """Ném ra InvalidTokenError nếu thất bại."""
        try:
            payload = jwt.decode(
                refresh_token,
                current_app.config['JWT_REFRESH_SECRET_KEY'],
                algorithms=['HS256']
            )
            jti = payload['jti']
            
            # ✅ BƯỚC 2: Ném lỗi cụ thể
            if not self.repo.revoke_refresh_token(jti):
                raise InvalidTokenError("Token không tìm thấy hoặc đã bị thu hồi")
            
            return True # Thành công
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Token không hợp lệ")

    def validate_access_token(self, access_token):
        """Ném ra InvalidTokenError nếu thất bại."""
        try:
            payload = jwt.decode(
                access_token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            # Trả về thông tin user khi thành công
            return {'user_id': payload['sub'], 'role': payload['role']}
        except jwt.ExpiredSignatureError:
            raise InvalidTokenError("Token đã hết hạn")
        except jwt.InvalidTokenError:
            raise InvalidTokenError("Token không hợp lệ")

    # ==========================================================
    # CÁC HÀM HELPER VÀ DEBUG (Giữ nguyên, không cần sửa)
    # ==========================================================

    def _generate_access_token(self, user):
        payload = {
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=15),
            'sub': user.id,
            'role': user.role,
            'username': user.username
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    def _generate_refresh_token(self, user):
        jti = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=7) 
        payload = {
            'iat': datetime.utcnow(),
            'exp': expires_at,
            'sub': user.id,
            'jti': jti 
        }
        token = jwt.encode(payload, current_app.config['JWT_REFRESH_SECRET_KEY'], algorithm='HS256')
        
        new_token_db = RefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at
        )
        self.repo.add_refresh_token(new_token_db)
        return {'token': token, 'jti': jti, 'expires_at': expires_at}
        
    def get_users_with_nplus1(self):
        """❌ Ví dụ gây ra N+1 Query Problem"""
        users = User.query.all()  # 1 query
        result = []
        for user in users:
            providers = [identity.provider for identity in user.oauth_identities]  # N query
            result.append({
                "id": user.id,
                "username": user.username,
                "providers": providers
            })
        return result

    def get_users_with_eager_loading(self):
        """✅ Eager Loading: joinedload"""
        users = User.query.options(joinedload(User.oauth_identities)).all()
        return [{
            "id": user.id,
            "username": user.username,
            "providers": [i.provider for i in user.oauth_identities]
        } for user in users]

    def get_users_with_batch_loading(self):
        """✅ Batch Loading: selectinload"""
        users = User.query.options(selectinload(User.oauth_identities)).all()
        return [{
            "id": user.id,
            "username": user.username,
            "providers": [i.provider for i in user.oauth_identities]
        } for user in users]