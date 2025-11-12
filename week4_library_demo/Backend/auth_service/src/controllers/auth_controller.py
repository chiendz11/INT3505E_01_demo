import json
from flask import Blueprint, request, jsonify, current_app, make_response, redirect, session
from ..services.auth_service import AuthService
from ..services.oauth_service import oauth, OAuthService
from urllib.parse import quote

# ✅ BƯỚC 1: Import các exception mới
from ..exceptions import (
    AuthError, InvalidLoginError, UserInactiveError, 
    UserAlreadyExistsError, InvalidTokenError, MissingDataError
)

auth_bp = Blueprint('auth_bp', __name__)

# ====================================================================
# ✅ BƯỚC 2: ĐỊNH NGHĨA CÁC TRÌNH XỬ LÝ LỖI (ERROR HANDLERS)
# ====================================================================

@auth_bp.errorhandler(InvalidLoginError)
@auth_bp.errorhandler(UserInactiveError)
@auth_bp.errorhandler(InvalidTokenError)
def handle_unauthorized(error):
    """
    Xử lý các lỗi 401 (Xác thực thất bại, token sai, user bị khóa).
    """
    return jsonify({"error": str(error)}), 401

@auth_bp.errorhandler(UserAlreadyExistsError)
def handle_conflict(error):
    """
    Xử lý lỗi 409 (Trùng tài nguyên, ví dụ: trùng email/username).
    """
    return jsonify({"error": str(error)}), 409

@auth_bp.errorhandler(MissingDataError)
def handle_bad_request(error):
    """
    Xử lý lỗi 400 (Dữ liệu vào thiếu hoặc sai).
    """
    return jsonify({"error": str(error)}), 400

@auth_bp.errorhandler(AuthError)
@auth_bp.errorhandler(Exception)
def handle_generic_error(error):
    """
    Xử lý các lỗi 500 (Lỗi server chung, không lường trước được).
    """
    # Bạn NÊN log lỗi này ra file hoặc console để debug
    print(f"🔥 Internal Server Error: {error}") 
    return jsonify({"error": "Đã xảy ra lỗi không mong muốn."}), 500

# ====================================================================
# ✅ BƯỚC 3: CÁC ROUTE ĐÃ ĐƯỢC DỌN SẠCH
# ====================================================================

@auth_bp.route('/users', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not all([email, username, password]):
        # Ném lỗi 400, @errorhandler sẽ bắt
        raise MissingDataError("Email, username, và password là bắt buộc")

    service = AuthService()
    # Chỉ gọi. Nếu lỗi, @errorhandler sẽ bắt.
    user = service.register_user(email, username, password)
        
    return jsonify({"message": "Đăng ký thành công", "user_id": user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    login_identifier = data.get('login')
    password = data.get('password')

    if not all([login_identifier, password]):
        raise MissingDataError("Login và password là bắt buộc")

    service = AuthService()
    # Service sẽ ném lỗi 401 nếu thất bại
    user, access_token, refresh_token_data = service.login_user(login_identifier, password)

    # Happy Path: Tạo response
    user_profile = {
        "id": user.id, "email": user.email,
        "username": user.username, "role": user.role
    }
    
    response = make_response(jsonify({
        "access_token": access_token,
        "user": user_profile
    }))
    
    # Set cookie cho refresh token
    response.set_cookie(
        "refresh_token", refresh_token_data['token'],
        httponly=True, 
        secure=True,     # (True nếu production dùng HTTPS)
        samesite='None', # (Nếu frontend và backend khác domain)
        path='/api/auth' # Chỉ gửi cookie khi gọi các API trong /api/auth/
    )
    return response

# --- Các phiên bản Login V2, V3, V4, V5 ---
# (Các route này sẽ tự động được hưởng lợi từ @errorhandler
# vì chúng đều gọi service.login_user)

@auth_bp.route('/v2/login', methods=['POST'])
def login_v2():
    data = request.json
    login_identifier = data.get('login')
    password = data.get('password')
    if not all([login_identifier, password]):
        raise MissingDataError("Login và password là bắt buộc")

    service = AuthService()
    user, access_token, refresh_token_data = service.login_user(login_identifier, password)
    
    user_profile_v2 = {
        "id": user.id, "email": user.email, "username": user.username, "role": user.role,
        "full_name": getattr(user, 'full_name', None),
        "avatar_url": getattr(user, 'avatar_url', None)
    }
    response = make_response(jsonify({"access_token": access_token, "user": user_profile_v2}))
    response.set_cookie("refresh_token", refresh_token_data['token'],
        httponly=True, secure=True, samesite='None', path='/api/auth/tokens') # Giả sử path khác
    return response

# (Các route V3, V4, V5... tương tự)

# --- Các route Token ---

@auth_bp.route('/refresh-token', methods=['PUT'])
def refresh():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise InvalidTokenError("Thiếu refresh token trong cookie")

    service = AuthService()
    # Service sẽ ném lỗi 401 nếu token sai/hết hạn
    access_token = service.refresh_access_token(refresh_token)

    return jsonify({"access_token": access_token}), 200

@auth_bp.route('/logout', methods=['DELETE'])
def logout():
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        # Dù không có token, vẫn nên trả về 200 (đã đăng xuất)
        # và cố gắng xóa cookie (nếu có)
        pass 

    if refresh_token:
        service = AuthService()
        # Chúng ta không cần quan tâm lỗi ở đây
        # Dù token hợp lệ hay không, client cũng muốn đăng xuất
        try:
            service.logout_user(refresh_token) 
        except InvalidTokenError:
            # Bỏ qua lỗi, vì đằng nào cũng xóa cookie
            pass
    
    response = make_response(jsonify({"message": "Đăng xuất thành công"}), 200)
    
    # Gửi lệnh cho trình duyệt xóa cookie
    response.delete_cookie(
        "refresh_token", 
        path='/api/auth', # Path phải khớp với lúc set
        secure=True, 
        httponly=True, 
        samesite='None'
    )
    return response

@auth_bp.route('/validate', methods=['POST'])
def validate_token():
    """
    Endpoint NỘI BỘ, chỉ API Gateway được gọi.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        raise InvalidTokenError("Missing or invalid token")
    
    access_token = token.split(" ")[1]

    service = AuthService()
    # Service sẽ ném lỗi 401 nếu token sai/hết hạn
    user_data = service.validate_access_token(access_token)
    
    # Trả về thông tin user cho Gateway
    return jsonify({"valid": True, "user": user_data}), 200

# --- Các route OAuth ---
# (Các route này đã xử lý lỗi bằng try/except riêng 
# vì logic redirect của chúng phức tạp, giữ nguyên là TỐT)

@auth_bp.route("/google/login")
def google_login():
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    # (Giữ nguyên logic authorize_redirect của bạn)
    response = oauth.google.authorize_redirect(
        redirect_uri, 
        code_challenge_method='S256' 
    )
    current_app.session_interface.save_session(current_app, session, response)
    return response

@auth_bp.route("/google/callback")
def google_callback():
    frontend_url = "http://localhost:5174/login" 
    try:
        token = oauth.google.authorize_access_token() 
        user_info = token.get('userinfo') 
        service = OAuthService() 
        result = service.handle_google_user(user_info) 
        redirect_url = f"{frontend_url}?login=success" # (Nên gửi token theo cách khác)
        response = make_response(redirect(redirect_url)) 
        
        response.set_cookie(
            "refresh_token", result["refresh_token"], 
            httponly=True, secure=True, samesite="None", path="/api/auth"
        )
        return response

    except Exception as e:
        print(f"🔥 Google OAuth callback error: {e}")
        return redirect(f"{frontend_url}#error=google_login_failed")

# --- Các route Debug N+1 ---
# (Các route này chỉ là Happy Path, không cần sửa)

@auth_bp.route('/users/nplus1', methods=['GET'])
def debug_users_nplus1():
    service = AuthService()
    result = service.get_users_with_nplus1()
    return jsonify(result), 200

@auth_bp.route('/users/eager', methods=['GET'])
def debug_users_eager():
    service = AuthService()
    result = service.get_users_with_eager_loading()
    return jsonify(result), 200