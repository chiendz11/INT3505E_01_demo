# auth_service/src/controllers/auth_controller.py

import time
import logging
import json
import traceback
from urllib.parse import quote
from flask import Blueprint, request, jsonify, current_app, make_response, redirect, session
from ..services.auth_service import AuthService
from ..services.oauth_service import oauth, OAuthService

# Import các exception
from ..exceptions import (
    AuthError, InvalidLoginError, UserInactiveError, 
    UserAlreadyExistsError, InvalidTokenError, MissingDataError
)

auth_bp = Blueprint('auth_bp', __name__)

# ====================================================================
# [LESSON 10] SETUP LOGGING & HELPER
# ====================================================================

# 1. Cấu hình Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuthServiceMonitor")

# 2. Helper: Audit Log (Quan trọng nhất của Auth Service)
def log_audit(action, target_id, details=None):
    """
    Ghi lại các sự kiện bảo mật quan trọng: Login, Register, Logout.
    """
    audit_record = {
        "event_type": "SECURITY_AUDIT_LOG", # Đánh dấu riêng cho Security
        "timestamp": time.time(),
        "actor": target_id or "Anonymous",  # Với Auth, actor thường là chính user đó
        "action": action,
        "target_resource": "user_account",
        "ip_address": request.remote_addr,
        "details": details or {}
    }
    logger.info(json.dumps(audit_record))

# ====================================================================
# [LESSON 10] MIDDLEWARE: OBSERVABILITY
# ====================================================================

@auth_bp.before_request
def start_timer():
    request.start_time = time.time()

@auth_bp.after_request
def log_access_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        
        log_data = {
            "event_type": "ACCESS_LOG",
            "method": request.method,
            "path": request.path,
            "ip": request.remote_addr,
            "status": response.status_code,
            "duration_seconds": round(duration, 4),
            "user_agent": request.headers.get('User-Agent')
        }
        
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
            
    return response

# ====================================================================
# ERROR HANDLERS
# ====================================================================

@auth_bp.errorhandler(InvalidLoginError)
@auth_bp.errorhandler(UserInactiveError)
@auth_bp.errorhandler(InvalidTokenError)
def handle_unauthorized(error):
    # Log warning để phát hiện tấn công dò mật khẩu
    logger.warning(f"[SECURITY] Auth Failed: {str(error)} | IP: {request.remote_addr}")
    return jsonify({"error": str(error)}), 401

@auth_bp.errorhandler(UserAlreadyExistsError)
def handle_conflict(error):
    return jsonify({"error": str(error)}), 409

@auth_bp.errorhandler(MissingDataError)
def handle_bad_request(error):
    return jsonify({"error": str(error)}), 400

@auth_bp.errorhandler(AuthError)
@auth_bp.errorhandler(Exception)
def handle_generic_error(error):
    # [DEBUGGING] In traceback chi tiết cho lỗi 500
    error_traceback = traceback.format_exc()
    logger.error(f"INTERNAL SERVER ERROR:\n{error_traceback}")
    return jsonify({"error": "An internal server error occurred."}), 500

# ====================================================================
# ROUTES
# ====================================================================

@auth_bp.route('/users', methods=['POST'])
def register():
    # [SECURITY] Rate Limit: Chặn spam đăng ký (5 lần/phút)
    limiter = current_app.extensions['limiter']
    with limiter.limit("5 per minute"):
        
        data = request.json
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        if not all([email, username, password]):
            raise MissingDataError("Email, username, và password là bắt buộc")

        service = AuthService()
        user = service.register_user(email, username, password)
        
        # [AUDIT LOG] Ghi nhận đăng ký mới
        log_audit("REGISTER", user.id, {"username": username, "email": email})
            
        return jsonify({"message": "Đăng ký thành công", "user_id": user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    # [SECURITY] Rate Limit: Chống Brute Force (10 lần/phút)
    limiter = current_app.extensions['limiter']
    with limiter.limit("10 per minute"):
    
        data = request.json
        login_identifier = data.get('login')
        password = data.get('password')

        if not all([login_identifier, password]):
            raise MissingDataError("Login và password là bắt buộc")

        service = AuthService()
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
        
        # [AUDIT LOG] Ghi nhận đăng nhập thành công
        log_audit("LOGIN", user.id, {"username": user.username})

        # Set cookie secure
        is_production = current_app.config.get('ENV') == 'production'
        response.set_cookie(
            "refresh_token", refresh_token_data['token'],
            httponly=True, 
            secure=is_production,     
            samesite='None' if is_production else 'Lax',
            path='/api/auth'
        )
        return response

# --- Các phiên bản Login V2 (Áp dụng tương tự) ---

@auth_bp.route('/v2/login', methods=['POST'])
def login_v2():
    # Vẫn áp dụng Rate Limit cho V2
    limiter = current_app.extensions['limiter']
    with limiter.limit("10 per minute"):
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
        
        log_audit("LOGIN_V2", user.id) # Audit Log
        
        response = make_response(jsonify({"access_token": access_token, "user": user_profile_v2}))
        
        is_production = current_app.config.get('ENV') == 'production'
        response.set_cookie("refresh_token", refresh_token_data['token'],
            httponly=True, secure=is_production, samesite='None' if is_production else 'Lax', path='/api/auth')
        return response

# --- Token Management ---

@auth_bp.route('/refresh-token', methods=['PUT'])
def refresh():
    # Rate Limit cho refresh (tránh spam token mới)
    limiter = current_app.extensions['limiter']
    with limiter.limit("20 per minute"):
        
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            raise InvalidTokenError("Thiếu refresh token trong cookie")

        service = AuthService()
        access_token = service.refresh_access_token(refresh_token)
        
        # Access log sẽ tự ghi lại việc này
        return jsonify({"access_token": access_token}), 200

@auth_bp.route('/logout', methods=['DELETE'])
def logout():
    refresh_token = request.cookies.get('refresh_token')
    
    if refresh_token:
        service = AuthService()
        try:
            # Audit Log Logout (cần decode token để biết ai logout, nhưng ở đây log token hash tạm)
            log_audit("LOGOUT", "Unknown_User", {"token_preview": refresh_token[:10] + "..."})
            service.logout_user(refresh_token) 
        except InvalidTokenError:
            pass
    
    response = make_response(jsonify({"message": "Đăng xuất thành công"}), 200)
    
    is_production = current_app.config.get('ENV') == 'production'
    response.delete_cookie(
        "refresh_token", 
        path='/api/auth', 
        secure=is_production, 
        httponly=True, 
        samesite='None' if is_production else 'Lax'
    )
    return response

@auth_bp.route('/validate', methods=['POST'])
def validate_token():
    """
    Endpoint NỘI BỘ: Không cần Rate Limit quá gắt vì chỉ Gateway gọi.
    """
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        raise InvalidTokenError("Missing or invalid token")
    
    access_token = token.split(" ")[1]

    service = AuthService()
    user_data = service.validate_access_token(access_token)
    
    return jsonify({"valid": True, "user": user_data}), 200

# --- OAuth Endpoints (Giữ nguyên logic redirect) ---

@auth_bp.route("/google/login")
def google_login():
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    response = oauth.google.authorize_redirect(redirect_uri, code_challenge_method='S256')
    current_app.session_interface.save_session(current_app, session, response)
    return response

@auth_bp.route("/google/callback")
def google_callback():
    frontend_url = "http://localhost:5174/login" # Nên lấy từ Config
    try:
        token = oauth.google.authorize_access_token() 
        user_info = token.get('userinfo') 
        service = OAuthService() 
        result = service.handle_google_user(user_info) 
        
        log_audit("LOGIN_GOOGLE", result.get('user_id', 'unknown')) # Audit
        
        redirect_url = f"{frontend_url}?login=success" 
        response = make_response(redirect(redirect_url)) 
        
        is_production = current_app.config.get('ENV') == 'production'
        response.set_cookie(
            "refresh_token", result["refresh_token"], 
            httponly=True, secure=is_production, samesite="None" if is_production else 'Lax', path="/api/auth"
        )
        return response

    except Exception as e:
        logger.error(f"Google OAuth Error: {str(e)}")
        return redirect(f"{frontend_url}#error=google_login_failed")

# --- Debug Routes (Giữ nguyên) ---

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