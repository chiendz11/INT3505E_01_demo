# auth_service/src/services/oauth_service.py

from flask import request
from uuid import uuid4
from authlib.integrations.flask_client import OAuth
from .auth_service import AuthService
from ..models.user_model import User
from ..repositories.user_repository import UserRepository

# ✅ BƯỚC 1: Import các exception
from ..exceptions import AuthError, UserAlreadyExistsError

oauth = OAuth()

def init_oauth(app):
    """Khởi tạo OAuth2 client"""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={
            "scope": "openid email profile",
            "code_challenge_method": "S256"
        }
    )


class OAuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.auth_service = AuthService()

    def handle_google_user(self, user_info):
        """
        Tạo hoặc lấy user từ thông tin Google.
        Ném ra Exception nếu thất bại.
        """
        provider = "google"
        provider_user_id = user_info["sub"]
        email = user_info["email"]
        name = user_info.get("name", f"user_{uuid4().hex[:6]}")

        oauth_identity = self.user_repo.get_oauth_identity(provider, provider_user_id)
        
        if oauth_identity:
            # Happy Path 1: User đã từng login = Google
            user = oauth_identity.user
        else:
            # Lần đầu login = Google
            user = self.user_repo.get_user_by_email(email)
            
            if not user:
                # Happy Path 2: User này hoàn toàn mới
                new_user_obj = User(
                    email=email, 
                    username=name, 
                    hashed_password=f"oauth_{uuid4().hex}"
                )
                
                # ✅ BƯỚC 2: Sửa lại, kiểm tra `error`
                user, error = self.user_repo.add_user(new_user_obj)
                
                # ✅ BƯỚC 3: XỬ LÝ SAD PATH
                if error:
                    # Dù logic get_user_by_email đã check,
                    # vẫn nên phòng thủ trường hợp trùng email (race condition)
                    if 'users_email_key' in error:
                         raise UserAlreadyExistsError("Email đã tồn tại (lỗi hiếm)")
                    # Lỗi DB không mong muốn
                    raise AuthError(f"Lỗi khi tạo user OAuth: {error}")
            
            # Nếu user đã tồn tại (qua email) hoặc vừa được tạo,
            # chúng ta liên kết tài khoản Google với họ.
            self.user_repo.add_oauth_identity(
                user_id=user.id, 
                provider=provider, 
                provider_user_id=provider_user_id
            )

        # Tạo tokens
        access_token = self.auth_service._generate_access_token(user)
        refresh_token_data = self.auth_service._generate_refresh_token(user)

        # Trả về cả 2 token
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_data['token'], # Trả token raw
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role
            }
        }