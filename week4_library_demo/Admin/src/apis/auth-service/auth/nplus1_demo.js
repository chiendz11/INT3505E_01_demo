import axiosInstance from '../../../config/axiosConfig.js';

/**
 * ❌ Gọi endpoint mô phỏng N+1 Query Problem.
 * FE gọi: GET /api/users/nplus1
 */
export async function debugGetUsersNPlus1() {
  try {
    const response = await axiosInstance.get('/api/users/nplus1');
    return response.data;
  } catch (error) {
    console.error('Lỗi khi debug N+1 query:', error);
    throw error.response?.data || { message: 'Lỗi không xác định khi gọi API N+1' };
  }
}

/**
 * ✅ Gọi endpoint đã giải quyết N+1 bằng Eager Loading.
 * FE gọi: GET /api/users/eager
 */
export async function debugGetUsersEager() {
  try {
    const response = await axiosInstance.get('/api/users/eager');
    return response.data;
  } catch (error) {
    console.error('Lỗi khi debug Eager Loading:', error);
    throw error.response?.data || { message: 'Lỗi không xác định khi gọi API Eager' };
  }
}

/**
 * ✅ Gọi endpoint đã giải quyết N+1 bằng Batch Loading (ví dụ: DataLoader).
 * FE gọi: GET /api/users/batch
 */
export async function debugGetUsersBatch() {
  try {
    const response = await axiosInstance.get('/api/users/batch');
    return response.data;
  } catch (error) {
    console.error('Lỗi khi debug Batch Loading:', error);
    throw error.response?.data || { message: 'Lỗi không xác định khi gọi API Batch' };
  }
}