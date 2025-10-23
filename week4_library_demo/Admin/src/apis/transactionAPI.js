import axiosInstance from '../config/axiosConfig';

export async function createTransaction(transactionData) {
  try {
    const response = await axiosInstance.post('/api/transactions', transactionData);
    return response.data;
  } catch (error) {
    console.error('Lỗi khi tạo giao dịch:', error);
    throw error.response?.data || { message: 'Không thể thực hiện giao dịch' };
  }
}

/**
 * Lấy danh sách các sách đang được mượn của user hiện tại.
 * @returns {Promise<Array>} Mảng các sách đang mượn.
 */
export async function getMyBorrowedBooks() {
  try {
    // Gọi đến endpoint mới của Gateway
    const response = await axiosInstance.get('/api/me/borrowed-books');
    // '/api/me/borrowed-books'= 'api/users/user_id/borrowed-books'
    return response.data;
  } catch (error) {
    console.error('Lỗi khi lấy sách đang mượn:', error);
    throw error.response?.data || { message: 'Không thể tải danh sách sách đang mượn' };
  }
}

/**
 * Lấy toàn bộ lịch sử giao dịch của người dùng đang đăng nhập.
 * @returns {Promise<Array>} Mảng tất cả giao dịch.
 */
export async function getMyTransactions() {
  try {
    const response = await axiosInstance.get('/api/me/transactions');
    // '/api/me/transactions'= 'api/users/user_id/transactions'
    
    return response.data;
  } catch (error) {
    console.error('Lỗi khi lấy lịch sử giao dịch:', error);
    throw error.response?.data || { message: 'Không thể tải lịch sử giao dịch' };
  }
}

