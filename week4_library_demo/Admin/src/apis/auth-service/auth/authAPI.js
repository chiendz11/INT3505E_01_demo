import axiosInstance from '../../../config/axiosConfig.js';

/**
 * Đăng nhập cho người dùng (USER hoặc ADMIN).
 * Backend sẽ tự động set HttpOnly cookie cho refresh token.
 * @param {object} credentials - { login, password }, trong đó login có thể là username hoặc email.
 * @returns {Promise<object>} Dữ liệu trả về, bao gồm accessToken và thông tin user.
 */
export async function login(credentials) {
  try {
    // Endpoint chuẩn RESTful: POST /api/auth/login
    const response = await axiosInstance.post('/api/auth/login', credentials);

    // Lưu accessToken vào biến trong axios instance để các request sau tự động sử dụng
    if (response.data.access_token) {
      axiosInstance.setAuthToken(response.data.access_token);
    }

    return response.data;
  } catch (error) {
    console.error('Lỗi trong quá trình đăng nhập:', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng nhập' };
  }
}

/**
 * [V2] Đăng nhập: thêm field full_name và avatar_url
 */
export async function loginV2(credentials) {
  try {
    // Endpoint chuẩn: /api/v2/auth/login
    const response = await axiosInstance.post('/api/v2/auth/login', credentials);

    console.log("✅ [Auth V2] Response:", response.data);

    if (response.data.access_token) {
      axiosInstance.setAuthToken(response.data.access_token);
    }

    return response.data;
  } catch (error) {
    console.error('Lỗi (V2):', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng nhập (V2)' };
  }
}

/**
 * [V3] Đăng nhập, trả về id kiểu số
 */
export async function loginV3(credentials) {
  try {
    const response = await axiosInstance.post('/api/v3/auth/login', credentials);
    if (response.data.access_token) {
      axiosInstance.setAuthToken(response.data.access_token);
    }
    console.log("✅ [Auth V3] Response:", response.data);
    return response.data;
  } catch (error) {
    console.error('Lỗi (V3):', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng nhập (V3)' };
  }
}

/**
 * [V4] Đăng nhập, trả về cấu trúc lồng nhau, không set cookie.
 */
export async function loginV4(credentials) {
  try {
    const response = await axiosInstance.post('/api/v4/auth/login', credentials);

    const accessToken = response.data?.data?.tokens?.access;
    const refreshToken = response.data?.data?.tokens?.refresh;

    if (accessToken) {
      axiosInstance.setAuthToken(accessToken);
      localStorage.setItem("v4_refresh_token", refreshToken);
    }
    console.log("✅ [Auth V4] Response:", response.data);
    return response.data;
  } catch (error) {
    console.error('Lỗi (V4):', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng nhập (V4)' };
  }
}

/**
 * [V5] Đăng nhập, bắt buộc gửi thêm 'device_id'.
 */
export async function loginV5(credentials, deviceId) {
  try {
    const bodyV5 = {
      ...credentials,
      device_id: deviceId || "unknown_device"
    };

    const response = await axiosInstance.post('/api/v5/auth/login', bodyV5);
    if (response.data.access_token) {
      axiosInstance.setAuthToken(response.data.access_token);
    }
    console.log("✅ [Auth V5] Response:", response.data);
    return response.data;
  } catch (error) {
    console.error('Lỗi (V5):', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng nhập (V5)' };
  }
}

export async function logout() {
  try {
    // Gọi API logout để xóa refresh token ở server
    await axiosInstance.post('/api/auth/logout');
    // Xóa access token ở client
    axiosInstance.setAuthToken(null);
  } catch (error) {
    console.error('Lỗi khi đăng xuất:', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi đăng xuất' };
  }
}



