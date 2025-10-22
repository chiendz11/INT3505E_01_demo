from flask import request
from uuid import uuid4
from authlib.integrations.flask_client import OAuth
from .auth_service import AuthService
from ..models.user_model import User
from ..repositories.user_repository import UserRepository

oauth = OAuth()

def init_oauth(app):
    """Khởi tạo OAuth2 client"""
    oauth.init_app(app)
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"}
    )


class OAuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.auth_service = AuthService()

    def handle_google_user(self, user_info):
        """Tạo hoặc lấy user từ thông tin Google"""
        provider = "google"
        provider_user_id = user_info["sub"]
        email = user_info["email"]
        name = user_info.get("name", f"user_{uuid4().hex[:6]}")

        # ✅ Kiểm tra xem user này đã từng login bằng Google chưa
        oauth_identity = self.user_repo.get_oauth_identity(provider, provider_user_id)
        if oauth_identity:
            user = oauth_identity.user
        else:
            user = self.user_repo.get_user_by_email(email)
            if not user:
                user, _ = self.user_repo.add_user(
                    User(email=email, username=name, hashed_password=f"oauth_{uuid4().hex}")
                )
            # ✅ Liên kết user với tài khoản Google
            self.user_repo.add_oauth_identity(user_id=user.id, provider=provider, provider_user_id=provider_user_id)

        access_token = self.auth_service._generate_access_token(user)
        refresh_token_data = self.auth_service._generate_refresh_token(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token_data["token"],
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
        }
