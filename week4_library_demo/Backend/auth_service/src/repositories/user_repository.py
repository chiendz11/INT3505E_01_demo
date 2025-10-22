from ..database import db
from ..models.user_model import User, OAuthIdentity, RefreshToken
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_

class UserRepository:
    def add_user(self, user):
        try:
            db.session.add(user)
            db.session.commit()
            return user, None
        except IntegrityError as e:
            db.session.rollback()
            return None, str(e)
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    def get_user_by_login(self, login_identifier):
        # Tìm bằng email hoặc username
        return User.query.filter(
            or_(User.email == login_identifier, User.username == login_identifier)
        ).first()

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)
    def get_user_by_email(self, email):
        """Tìm user bằng email."""
        return User.query.filter_by(email=email.lower()).first()

    def add_oauth_identity(self, user_id, provider, provider_user_id):
        """Thêm một liên kết OAuth mới."""
        identity = OAuthIdentity(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id
        )
        db.session.add(identity)
        db.session.commit()
        return identity

    def get_oauth_identity(self, provider, provider_user_id):
        """Tìm một liên kết OAuth."""
        return OAuthIdentity.query.filter_by(
            provider=provider,
            provider_user_id=provider_user_id
        ).first()

    def add_refresh_token(self, token):
        try:
            db.session.add(token)
            db.session.commit()
            return token
        except Exception as e:
            db.session.rollback()
            return None

    def get_refresh_token(self, jti):
        return RefreshToken.query.filter_by(jti=jti, is_revoked=False).first()

    def revoke_refresh_token(self, jti):
        token = self.get_refresh_token(jti)
        if token and not token.is_revoked:
            token.is_revoked = True
            db.session.commit()
            return True
        return False