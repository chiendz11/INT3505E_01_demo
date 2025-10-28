import axiosInstance from '../../../config/axiosConfig';

export async function createTransaction(transactionData) {
  try {
    const response = await axiosInstance.post('/api/transactions', transactionData);
    return response.data;
  } catch (error) {
    console.error('Lỗi khi tạo giao dịch:', error);
    throw error.response?.data || { message: 'Không thể thực hiện giao dịch' };
  }
}

