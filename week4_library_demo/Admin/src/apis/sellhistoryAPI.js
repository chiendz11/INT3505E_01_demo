import axiosInstance from '../config/axiosConfig';

const SELL_HISTORY_ENDPOINT = '/api/admin/sell-histories';

/** Lấy danh sách hóa đơn */
export async function getSellHistories() {
  try {
    const response = await axiosInstance.get(SELL_HISTORY_ENDPOINT);
    return response;
  } catch (error) {
    console.error('Error fetching sell histories:', error);
    throw error;
  }
}

/** Tạo hóa đơn mới
 * @param {Object} payload - { invoiceNumber, centerId, items, totalAmount, paymentMethod, customer }
 */
export async function createSellHistory(payload) {
  try {
    const response = await axiosInstance.post(SELL_HISTORY_ENDPOINT, payload);
    return response;
  } catch (error) {
    console.error('Error creating sell history:', error);
    throw error;
  }
}
