import jwt
import uuid
from datetime import datetime, timedelta
from flask import current_app
from flask_bcrypt import Bcrypt
from ..models.user_model import User, RefreshToken
from ..repositories.user_repository import UserRepository

bcrypt = Bcrypt()

class AuthService:
    def __init__(self):
        self.repo = UserRepository()

    def register_user(self, email, username, password):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(
            email=email.lower(),
            username=username.lower(),
            hashed_password=hashed_password,
            role='user' # Mặc định là user
        )
        user, error = self.repo.add_user(new_user)
        if error:
            if 'users_email_key' in error:
                return None, "Email đã tồn tại"
            if 'users_username_key' in error:
                return None, "Username đã tồn tại"
            return None, "Lỗi server"
        return user, None

    def login_user(self, login_identifier, password):
        """
        Xác thực người dùng, tạo token và trả về thông tin người dùng.
        [FIX] Luôn trả về 4 giá trị: (user, access_token, refresh_token_data, error)
        """
        user = self.repo.get_user_by_login(login_identifier.lower())
        
        # 1. Lỗi xác thực
        if not user or not user.hashed_password or not bcrypt.check_password_hash(user.hashed_password, password):
            # Trả về 4 giá trị None cho user, access_token, refresh_token và thông báo lỗi
            return None, None, None, "Email/Username hoặc mật khẩu không chính xác" 
        
        # 2. Lỗi tài khoản bị khóa
        if not user.is_active:
            # Trả về 4 giá trị
            return None, None, None, "Tài khoản đã bị khóa"
            
        # 3. Thành công
        access_token = self._generate_access_token(user)
        refresh_token_data = self._generate_refresh_token(user)
        
        # [FIX] Trả về user object cùng với tokens
        return user, access_token, refresh_token_data, None

    def _generate_access_token(self, user):
        payload = {
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=15), # Sống 15 phút
            'sub': user.id,
            'role': user.role,
            'username': user.username
        }
        return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

    def _generate_refresh_token(self, user):
        jti = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=7) # Sống 7 ngày
        payload = {
            'iat': datetime.utcnow(),
            'exp': expires_at,
            'sub': user.id,
            'jti': jti # JWT ID, dùng để thu hồi
        }
        token = jwt.encode(payload, current_app.config['JWT_REFRESH_SECRET_KEY'], algorithm='HS256')
        
        # Lưu vào DB
        new_token_db = RefreshToken(
            user_id=user.id,
            jti=jti,
            expires_at=expires_at
        )
        self.repo.add_refresh_token(new_token_db)
        return {'token': token, 'jti': jti, 'expires_at': expires_at}

    def refresh_access_token(self, refresh_token):
        try:
            payload = jwt.decode(
                refresh_token,
                current_app.config['JWT_REFRESH_SECRET_KEY'],
                algorithms=['HS256']
            )
            jti = payload['jti']
            user_id = payload['sub']

            # Kiểm tra trong DB xem token đã bị thu hồi chưa
            db_token = self.repo.get_refresh_token(jti)
            if not db_token or db_token.expires_at < datetime.utcnow():
                return None, "Refresh token không hợp lệ hoặc đã hết hạn"
            
            user = self.repo.get_user_by_id(user_id)
            if not user:
                return None, "Không tìm thấy người dùng"
            
            # Tạo access token mới
            access_token = self._generate_access_token(user)
            return access_token, None

        except jwt.ExpiredSignatureError:
            return None, "Refresh token đã hết hạn"
        except jwt.InvalidTokenError:
            return None, "Refresh token không hợp lệ"

    def logout_user(self, refresh_token):
        try:
            payload = jwt.decode(
                refresh_token,
                current_app.config['JWT_REFRESH_SECRET_KEY'],
                algorithms=['HS256']
            )
            jti = payload['jti']
            # Thu hồi token trong DB
            if self.repo.revoke_refresh_token(jti):
                return True, None
            else:
                return False, "Token không tìm thấy"
        except jwt.InvalidTokenError:
            return False, "Token không hợp lệ"

    def validate_access_token(self, access_token):
        try:
            payload = jwt.decode(
                access_token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            # Trả về thông tin user để Gateway sử dụng
            return {'user_id': payload['sub'], 'role': payload['role']}, None
        except jwt.ExpiredSignatureError:
            return None, "Token đã hết hạn"
        except jwt.InvalidTokenError:
            return None, "Token không hợp lệ"
        
        