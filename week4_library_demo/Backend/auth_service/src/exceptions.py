# auth_service/src/exceptions.py

class AuthError(Exception):
    """Lỗi cơ sở cho tất cả các lỗi trong service này"""
    pass

class InvalidLoginError(AuthError):
    """Ném ra khi email/password không chính xác."""
    pass

class UserInactiveError(AuthError):
    """Ném ra khi tài khoản người dùng bị khóa (is_active=False)."""
    pass

class UserAlreadyExistsError(AuthError):
    """Ném ra khi đăng ký trùng email hoặc username."""
    pass

class InvalidTokenError(AuthError):
    """Ném ra khi access/refresh token không hợp lệ hoặc hết hạn."""
    pass

class MissingDataError(AuthError):
    """Ném ra khi thiếu dữ liệu đầu vào (ví dụ: thiếu 'login')."""
    pass