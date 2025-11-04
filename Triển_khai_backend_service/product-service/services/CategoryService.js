/* eslint-disable no-unused-vars */
const Service = require('./Service');

/**
* Lấy danh sách danh mục sản phẩm
*
* returns List
* */
const categoriesGET = () => new Promise(
  async (resolve, reject) => {
    try {
      // 1. Tạo dữ liệu tĩnh (mock data)
      // Dữ liệu này tuân thủ schema Category trong openAPI.yaml (id: string, name: string)
      const categories = [
        { id: 'c01', name: 'Sách Văn học' },
        { id: 'c02', name: 'Sách Kỹ năng & Tâm lý' },
        { id: 'c03', name: 'Đồ chơi' },
        { id: 'c04', name: 'Văn phòng phẩm' },
      ];

      // 2. Trả về response thành công (Status 200 OK)
      resolve(Service.successResponse(categories));

    } catch (e) {
      // 3. Xử lý lỗi hệ thống (500)
      reject(Service.rejectResponse(
        e.message || 'Lỗi hệ thống khi lấy danh mục',
        500,
      ));
    }
  },
);

module.exports = {
  categoriesGET,
};