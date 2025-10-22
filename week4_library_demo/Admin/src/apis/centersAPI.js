import axiosInstance from './axiosInstance'; // Import axiosInstance

// Lấy danh sách các nhà thi đấu
export const getCentersAPI = async () => {
  try {
    const response = await axiosInstance.get('/api/centers');
    return response.data;
  } catch (error) {
    console.error('Error fetching centers:', error);
    throw error; // Re-throw the error to be handled by the caller
  }
};

// Lấy thông tin 1 nhà thi đấu theo id
export const getCenterByIdAPI = async (id) => {
  try {
    const response = await axiosInstance.get(`/api/centers/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching center with id ${id}:`, error);
    throw error;
  }
};

// Tạo mới 1 nhà thi đấu
export const createCenterAPI = async (centerData) => {
  try {
    const response = await axiosInstance.post('/api/centers', centerData);
    return response.data;
  } catch (error) {
    console.error('Error creating center:', error);
    throw error;
  }
};

// Cập nhật thông tin 1 nhà thi đấu theo id
export const updateCenterAPI = async (id, centerData) => {
  try {
    const response = await axiosInstance.put(`/api/centers/${id}`, centerData);
    return response.data;
  } catch (error) {
    console.error(`Error updating center with id ${id}:`, error);
    throw error;
  }
};

// Xóa 1 nhà thi đấu theo id
export const deleteCenterAPI = async (id) => {
  try {
    const response = await axiosInstance.delete(`/api/centers/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting center with id ${id}:`, error);
    throw error;
  }
};
