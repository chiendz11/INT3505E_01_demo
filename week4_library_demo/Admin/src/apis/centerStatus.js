import axiosInstance from "../config/axiosConfig"; // Đường dẫn tới file định nghĩa axiosInstance

// API lấy toàn bộ danh sách các trung tâm (phiên bản admin)
export const getAllCenters = async () => {
  try {
    const response = await axiosInstance.get("/api/admin/center-status/get-all-centers");
    return response.data.data; // Mảng các trung tâm
  } catch (error) {
    console.error("Error fetching centers:", error.response?.data || error.message);
    throw error;
  }
};

// API lấy dữ liệu trạng thái sân theo trung tâm và ngày
export async function fetchFullMapping(centerId, dateStr) {
  try {
    if (!centerId || !dateStr) {
      throw new Error("Thiếu tham số centerId hoặc date");
    }

    const response = await axiosInstance.get("/api/admin/center-status/full-mapping", {
      params: {
        centerId,
        date: dateStr,
      },
    });

    return response.data;
  } catch (error) {
    console.error("Lỗi khi lấy dữ liệu trạng thái sân:", error);
    throw error.response?.data || { success: false, message: "Lỗi khi lấy dữ liệu trạng thái sân" };
  }
};

// API lấy danh sách sân theo trung tâm (phiên bản admin)
export const getCourtsByCenter = async (centerId) => {
  try {
    const response = await axiosInstance.get("/api/admin/center-status/get-courts", {
      params: { centerId }
    });
    // Giả sử API trả về { success: true, data: [...] }
    return response.data.data; // Trả về mảng sân
  } catch (error) {
    console.error("Lỗi khi lấy danh sách sân:", error.response?.data || error.message);
    throw error;
  }
};