import axios from "axios";

const API_URL = import.meta.env.API_GATEWAY_URL || "http://localhost:8080";

// 🔑 BIẾN LƯU TRỮ TRONG BỘ NHỚ (IN-MEMORY)
let accessToken = null; 

let isRefreshing = false;
let refreshSubscribers = [];

// Hàm cập nhật token trong bộ nhớ
function setAccessToken(token) {
  accessToken = token;
}

// Hàm đăng ký subscriber khi có nhiều request cùng chờ refresh
function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb);
}

function onRefreshed(newToken) {
  refreshSubscribers.forEach(cb => cb(newToken));
  refreshSubscribers = [];
}

const axiosInstance = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Gửi cookie (Refresh Token)
});

// ----------------------
// Request Interceptor
// ----------------------
axiosInstance.interceptors.request.use(
  (config) => {
    // ⚠️ LẤY TOKEN TRỰC TIẾP TỪ BIẾN BỘ NHỚ
    if (accessToken) { 
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ----------------------
// Response Interceptor (ĐÃ ĐIỀU CHỈNH)
// ----------------------
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    // 💡 PHẦN 1: XỬ LÝ 401 VÀ LÀM MỚI TOKEN
    if (status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Nếu đang refresh thì chờ token mới
        return new Promise((resolve) => {
          subscribeTokenRefresh((newToken) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(axiosInstance(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Gọi API refresh token
        const res = await axios.put(
          `${API_URL}/api/auth/tokens`, 
          {},
          { withCredentials: true }
        );

        const newToken = res.data.access_token;
        setAccessToken(newToken); 
        onRefreshed(newToken);  
        // Retry lại request gốc
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return axiosInstance(originalRequest);

      } catch (err) {
        console.error("Refresh token failed", err);
        // ⚠️ Không chuyển hướng ở đây! Chỉ cần xóa token cục bộ
        setAccessToken(null); 
        // Vẫn reject để request gốc thất bại. AuthContext sẽ xử lý việc chuyển hướng
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ----------------------
// HÀM PUBLIC ĐỂ QUẢN LÝ TOKEN TỪ BÊN NGOÀI (Giữ nguyên)
// ----------------------
axiosInstance.setAuthToken = (token) => {
    setAccessToken(token);
};

axiosInstance.clearAuthToken = () => {
    setAccessToken(null);
    // Trong thực tế, bạn cũng sẽ cần gọi API để xóa cookie/refresh token
};

export default axiosInstance;
