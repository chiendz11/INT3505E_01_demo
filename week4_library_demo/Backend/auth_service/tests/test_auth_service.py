import pytest
import jwt # Cần import để mock các lỗi của nó
from unittest.mock import MagicMock, call

# Import các lớp cần test và mock
from src.services.auth_service import AuthService
from src.repositories.user_repository import UserRepository
from src.models.user_model import User
from src.exceptions import (
    AuthError, InvalidLoginError, UserInactiveError, 
    UserAlreadyExistsError, InvalidTokenError
)

# ====================================================================
# PHẦN SETUP (FIXTURES)
# ====================================================================

@pytest.fixture
def mock_repo(mocker):
    """Giả mạo (mock) UserRepository"""
    return mocker.Mock(spec=UserRepository)

@pytest.fixture
def mock_bcrypt(mocker):
    """Giả mạo (mock) thư viện bcrypt"""
    bcrypt = mocker.Mock()
    # Giả lập hàm băm, trả về một chuỗi text đơn giản
    bcrypt.generate_password_hash.return_value.decode.return_value = 'hashed_password_string'
    # Mặc định là check pass thành công
    bcrypt.check_password_hash.return_value = True
    return bcrypt

@pytest.fixture
def mock_current_app(mocker):
    """Giả mạo (mock) 'current_app' của Flask"""
    mock_app = mocker.Mock()
    # Cung cấp các config giả mà service cần
    mock_app.config = {
        'JWT_SECRET_KEY': 'test_secret_key',
        'JWT_REFRESH_SECRET_KEY': 'test_refresh_key'
    }
    return mock_app

@pytest.fixture
def mock_jwt(mocker):
    """Giả mạo (mock) thư viện jwt"""
    # Chúng ta chỉ cần mock hàm 'decode'
    return mocker.patch('src.services.auth_service.jwt.decode')

@pytest.fixture
def mock_user():
    """Tạo một đối tượng User giả"""
    user = MagicMock(spec=User)
    user.id = 'user-uuid-123'
    user.email = 'test@example.com'
    user.username = 'testuser'
    user.role = 'user'
    user.is_active = True
    user.hashed_password = 'real_hashed_password' # Giả sử đây là hash thật
    return user

@pytest.fixture
def auth_service(mocker, mock_repo, mock_bcrypt, mock_current_app):
    """
    Fixture chính: Tạo AuthService và "tiêm" (inject) các mock.
    Đây là phần phức tạp nhất.
    """
    # 1. Patch các thư viện mà 'auth_service.py' import vào
    mocker.patch('src.services.auth_service.current_app', mock_current_app)
    mocker.patch('src.services.auth_service.bcrypt', mock_bcrypt)
    
    # 2. Khởi tạo service
    service = AuthService()
    
    # 3. Tiêm repo giả mạo vào service
    service.repo = mock_repo
    
    return service

# ====================================================================
# TEST HÀM: register_user
# ====================================================================

def test_register_user_success(auth_service, mock_repo, mock_bcrypt, mock_user):
    """Test Happy Path: Đăng ký thành công"""
    # Setup: Repo giả lập việc add user thành công
    mock_repo.add_user.return_value = (mock_user, None)
    
    # Action
    email = "test@example.com"
    username = "testuser"
    password = "123456"
    result = auth_service.register_user(email, username, password)
    
    # Assert
    # 1. Kiểm tra bcrypt được gọi để băm mật khẩu
    mock_bcrypt.generate_password_hash.assert_called_with(password)
    
    # 2. Kiểm tra repo được gọi (chúng ta không cần check object User
    #    chính xác, chỉ cần biết nó được gọi 1 lần)
    mock_repo.add_user.assert_called_once()
    
    # 3. Kết quả trả về đúng là user
    assert result == mock_user

def test_register_user_email_exists(auth_service, mock_repo):
    """Test Sad Path: Đăng ký trùng email"""
    # Setup: Repo trả về lỗi trùng email (lỗi từ DB)
    mock_repo.add_user.return_value = (None, "Lỗi... users_email_key ...")
    
    # Action & Assert: Kỳ vọng service ném ra exception
    with pytest.raises(UserAlreadyExistsError, match="Email đã tồn tại"):
        auth_service.register_user("test@example.com", "user", "123")

def test_register_user_username_exists(auth_service, mock_repo):
    """Test Sad Path: Đăng ký trùng username"""
    # Setup: Repo trả về lỗi trùng username
    mock_repo.add_user.return_value = (None, "Lỗi... users_username_key ...")
    
    with pytest.raises(UserAlreadyExistsError, match="Username đã tồn tại"):
        auth_service.register_user("test@example.com", "user", "123")

# ====================================================================
# TEST HÀM: login_user
# ====================================================================

def test_login_user_success(auth_service, mock_repo, mock_bcrypt, mock_user):
    """Test Happy Path: Đăng nhập thành công"""
    # Setup
    mock_repo.get_user_by_login.return_value = mock_user
    mock_bcrypt.check_password_hash.return_value = True
    
    # Action
    result_user, result_access, result_refresh = auth_service.login_user("test@example.com", "123")
    
    # Assert
    # 1. Kiểm tra đã tìm user
    mock_repo.get_user_by_login.assert_called_with("test@example.com")
    # 2. Kiểm tra đã check hash
    mock_bcrypt.check_password_hash.assert_called_with(mock_user.hashed_password, "123")
    # 3. Trả về đúng user
    assert result_user == mock_user
    # 4. Đã tạo token (kiểm tra không rỗng)
    assert result_access is not None
    assert result_refresh is not None

def test_login_user_not_found(auth_service, mock_repo):
    """Test Sad Path: User không tồn tại"""
    # Setup: Repo không tìm thấy user
    mock_repo.get_user_by_login.return_value = None
    
    with pytest.raises(InvalidLoginError, match="không chính xác"):
        auth_service.login_user("wrong@example.com", "123")

def test_login_user_wrong_password(auth_service, mock_repo, mock_bcrypt, mock_user):
    """Test Sad Path: Sai mật khẩu"""
    # Setup
    mock_repo.get_user_by_login.return_value = mock_user
    # GIẢ LẬP SAI MẬT KHẨU
    mock_bcrypt.check_password_hash.return_value = False
    
    with pytest.raises(InvalidLoginError, match="không chính xác"):
        auth_service.login_user("test@example.com", "wrong_pass")

def test_login_user_inactive(auth_service, mock_repo, mock_user):
    """Test Sad Path: User bị khóa"""
    # Setup: User bị inactive
    mock_user.is_active = False
    mock_repo.get_user_by_login.return_value = mock_user
    
    with pytest.raises(UserInactiveError, match="Tài khoản đã bị khóa"):
        auth_service.login_user("test@example.com", "123")

def test_login_user_oauth_account(auth_service, mock_repo, mock_user):
    """Test Sad Path: User đăng ký bằng Google (không có hash)"""
    # Setup: User không có password hash (lỗi 'Invalid salt' của bạn)
    mock_user.hashed_password = None
    mock_repo.get_user_by_login.return_value = mock_user
    
    with pytest.raises(InvalidLoginError):
        auth_service.login_user("test@example.com", "123")
    
    # Quan trọng: Đảm bảo KHÔNG GỌI check_password_hash
    assert auth_service.repo.check_password_hash.called is False

# ====================================================================
# TEST HÀM: validate_access_token
# ====================================================================

def test_validate_access_token_success(auth_service, mock_jwt, mock_current_app):
    """Test Happy Path: Token hợp lệ"""
    # Setup: Mock jwt.decode trả về payload
    expected_payload = {'sub': 'user-id-123', 'role': 'admin'}
    mock_jwt.return_value = expected_payload
    
    # Action
    result = auth_service.validate_access_token("valid_token_string")
    
    # Assert
    # 1. Đã gọi jwt.decode với đúng key
    mock_jwt.assert_called_with(
        "valid_token_string",
        'test_secret_key', # Key từ mock_current_app
        algorithms=['HS256']
    )
    # 2. Trả về đúng payload
    assert result == expected_payload

def test_validate_access_token_expired(auth_service, mock_jwt):
    """Test Sad Path: Token hết hạn"""
    # Setup: Mock jwt.decode ném ra lỗi
    mock_jwt.side_effect = jwt.ExpiredSignatureError
    
    with pytest.raises(InvalidTokenError, match="Token đã hết hạn"):
        auth_service.validate_access_token("expired_token")

def test_validate_access_token_invalid(auth_service, mock_jwt):
    """Test Sad Path: Token sai (chữ ký, định dạng...)"""
    mock_jwt.side_effect = jwt.InvalidTokenError
    
    with pytest.raises(InvalidTokenError, match="Token không hợp lệ"):
        auth_service.validate_access_token("invalid_token")