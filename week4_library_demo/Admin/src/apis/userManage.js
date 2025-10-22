import axiosInstance from '../config/axiosConfig'; // Đường dẫn tới file định nghĩa axiosInstance

// Hàm lấy toàn bộ người dùng
export const getAllUsers = async () => {
  try {
    const response = await axiosInstance.get('/api/admin/user-manage/get-all-users');
    return response.data;
  } catch (error) {
    console.error('Error fetching users:', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi lấy danh sách người dùng' };
  }
};


export const deleteUser = async (id) => {
  try {
    const response = await axiosInstance.delete('/api/admin/user-manage/delete-user', {
      params: { id }
    });
    return response.data;
  } catch (error) {
    console.error('Error deleting user:', error);
    throw error.response?.data || { success: false, message: 'Lỗi khi xóa người dùng' };
  }
};

