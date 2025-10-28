
import axiosInstance from '../../../../config/axiosConfig.js';

/**
 * Đăng ký người dùng mới.
 */
export async function register(userData) {
    try {
      const response = await axiosInstance.post('/api/users', userData);
      return response.data;
    } catch (error) {
      console.error('Lỗi khi đăng ký:', error);
      throw error.response?.data || { success: false, message: 'Lỗi khi đăng ký' };
    }
  }