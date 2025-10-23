import axiosInstance from '../config/axiosConfig'; // Đường dẫn tới file cấu hình axios

/**
 * Đăng nhập cho người dùng (USER hoặc ADMIN).
 * Backend sẽ tự động set HttpOnly cookie cho refresh token.
 * @param {object} credentials - { login, password }, trong đó login có thể là username hoặc email.
 * @returns {Promise<object>} Dữ liệu trả về, bao gồm accessToken và thông tin user.
 */
export async function login(credentials) {
  try {
    // Endpoint chung cho cả user và admin, backend sẽ trả về role tương ứng
    const response = await axiosInstance.post('/api/auth/tokens', credentials);
    
    // Lưu accessToken vào biến trong axios instance để các request sau tự động sử dụng
    if (response.data.access_token) {
      axiosInstance.setAuthToken(response.data.access_token);
    }

    return response.data;
  } catch (error) {
    console.error('Lỗi trong quá trình đăng nhập:', error);
    // Ném lỗi ra ngoài để component có thể xử lý
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng nhập' };
  }
}
// version 2: Thêm field full_name và avatar_url
export async function loginV2(credentials) {
  try {
    // Endpoint V2 (trỏ đến /api/v2/auth/tokens của Gateway)
    const response = await axiosInstance.post('/api/v2/auth/tokens', credentials);
    
    // [ĐỂ DEMO] Log data nhận được ra console
    console.log("✅ [Auth V2] Đã nhận được response:", response.data);

    // Lưu accessToken (giống V1)
    if (response.data.access_token) {
      axiosInstance.setAuthToken(response.data.access_token);
    }

    return response.data;
  } catch (error) {
    console.error('Lỗi trong quá trình đăng nhập (V2):', error);
    // Ném lỗi ra ngoài để component có thể xử lý
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng nhập' };
  }
}

/**
 * Đăng ký một người dùng mới.
 * @param {object} userData - { email, username, password }
 * @returns {Promise<object>} Dữ liệu trả về từ server.
 */
export async function register(userData) {
  try {
    const response = await axiosInstance.post('/api/users', userData);
    return response.data;
  } catch (error) {
    console.error('Lỗi trong quá trình đăng ký:', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng ký' };
  }
}

/**
 * Bắt đầu luồng đăng nhập với Google.
 * Hàm này không trả về gì, nó sẽ chuyển hướng trình duyệt của người dùng.
 */
export function loginWithGoogle() {
  // Lấy baseURL từ axios instance để đảm bảo luôn đúng
  const googleLoginUrl = `${axiosInstance.defaults.baseURL}/api/auth/google/login`;
  // Chuyển hướng trang hiện tại đến endpoint của backend để bắt đầu OAuth flow
  window.location.href = googleLoginUrl;
}

