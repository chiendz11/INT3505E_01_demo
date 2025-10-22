import axiosInstance from '../config/axiosConfig'; // Import the axiosInstance

/**
 * Nhập hàng
 * @param {{ inventoryId: string, centerId: string, supplier: string, quantityImport: number, importPrice: number }} data
 */
export async function importStock(data) {
  try {
    const response = await axiosInstance.post('/api/admin/inventories/import', data);
    return response; // Return the full response
  } catch (error) {
    console.error('Error importing stock:', error);
    throw error;
  }
}

/**
 * Lấy lịch sử nhập hàng
 * @param {{ inventoryId?: string, centerId?: string }} params
 */
export async function getStockHistory(params = {}) {
  try {
    const response = await axiosInstance.get('/api/admin/inventories/import-history', { params });
    return response; // Return the full response
  } catch (error) {
    console.error('Error fetching stock history:', error);
    throw error;
  }
}

/**
 * Bán hàng (trừ kho)
 * @param {{ inventoryId: string, centerId: string, quantityExport: number, exportPrice: number }} data
 */
export async function sellStock(data) {
  try {
    const response = await axiosInstance.post('/api/admin/inventories/export', data);
    return response; // Return the full response
  } catch (error) {
    console.error('Error selling stock:', error);
    throw error;
  }
}

export async function getInventoryList(params = {}) {
  try {
    const response = await axiosInstance.get('/api/admin/inventories/list', { params });
    return response; // Return the full response
  } catch (error) {
    console.error('Error fetching inventory list:', error);
    throw error;
  }
}
