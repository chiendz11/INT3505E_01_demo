import axiosInstance from '../../../config/axiosConfig.js';
/**
 * Đăng nhập bằng Google (OAuth 2.0 Authorization Code)
 */
export function loginWithGoogle() {
    const googleLoginUrl = `${axiosInstance.defaults.baseURL}/api/auth/google/login`;
    window.location.href = googleLoginUrl;
  }