/* eslint-disable no-unused-vars */
const Service = require('./Service');
// 1. IMPORT MODEL VÀ CÁC THƯ VIỆN CẦN THIẾT
const mongoose = require('mongoose');
// Giả định Model được tạo tại ../models/product.js
const Product = require('../model/product'); 

// Hàm tiện ích để xử lý lỗi Validation
const handleMongooseError = (e) => {
    return Service.rejectResponse(
        e.message || 'Dữ liệu không hợp lệ hoặc lỗi hệ thống',
        e.name === 'ValidationError' ? 400 : 500, // 400 cho lỗi Validation
    );
};


/**
* Tạo mới sản phẩm (POST /products)
* (Nhiệm vụ của Đức)
* */
const productsPOST = ({ body }) => new Promise(
  async (resolve, reject) => {
    try {
      // 1. Tạo mới sản phẩm bằng Mongoose
      const newProduct = await Product.create(body);

      // 2. Trả về sản phẩm đã tạo với status 201 (Created)
      resolve(Service.successResponse(newProduct.toJSON(), 201)); // Sử dụng toJSON() để format ID

    } catch (e) {
      reject(handleMongooseError(e));
    }
  },
);

/**
* Lấy danh sách tất cả sản phẩm (có phân trang & lọc)
* (Nhiệm vụ của Đức)
* */
const productsGET = ({ category, type, page, limit }) => new Promise(
  async (resolve, reject) => {
    try {
      const pageNum = parseInt(page) || 1;
      const limitNum = parseInt(limit) || 20;
      const skip = (pageNum - 1) * limitNum;
      
      const query = {};
      if (category) {
        query.category = category;
      }
      if (type) {
        query.type = type;
      }

      // 1. Đếm tổng số sản phẩm cho phân trang
      const total = await Product.countDocuments(query);

      // 2. Truy vấn dữ liệu: Lọc, Phân trang và Sắp xếp
      const data = await Product.find(query)
        .skip(skip)
        .limit(limitNum)
        .sort({ createdAt: -1 })
        .exec();

      // 3. Trả về response theo format OpenAPI
      resolve(Service.successResponse({
        total,
        page: pageNum,
        limit: limitNum,
        data: data.map(item => item.toJSON()), // Dùng toJSON để format ID
      }));

    } catch (e) {
      reject(Service.rejectResponse('Lỗi hệ thống khi truy vấn sản phẩm', 500));
    }
  },
);

/**
* Lấy chi tiết một sản phẩm (GET /products/{id})
* (Nhiệm vụ của Đức)
* */
const productsIdGET = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        return reject(Service.rejectResponse('ID sản phẩm không hợp lệ.', 400));
      }

      // 1. Tìm sản phẩm theo ID
      const product = await Product.findById(id).exec();

      // 2. Xử lý không tìm thấy (404)
      if (!product) {
        return reject(Service.rejectResponse('Không tìm thấy sản phẩm.', 404));
      }

      // 3. Trả về chi tiết sản phẩm
      resolve(Service.successResponse(product.toJSON()));

    } catch (e) {
      reject(Service.rejectResponse('Lỗi hệ thống', 500));
    }
  },
);

/**
* Cập nhật thông tin sản phẩm (PUT /products/{id})
* (Nhiệm vụ của Chiến - UD)
* */
const productsIdPUT = ({ id, productUpdate }) => new Promise(
  async (resolve, reject) => {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        return reject(Service.rejectResponse('ID sản phẩm không hợp lệ.', 400));
      }

      // 1. Dùng Mongoose để tìm và cập nhật
      const updatedProduct = await Product.findByIdAndUpdate(
        id, 
        productUpdate, 
        { 
          new: true,          // Trả về bản ghi đã cập nhật
          runValidators: true, // Kiểm tra các quy tắc validate trong schema
          context: 'query'     // Cho phép validator chạy cho update
        }
      ).exec();

      // 2. Xử lý trường hợp không tìm thấy (404)
      if (!updatedProduct) {
        return reject(Service.rejectResponse('Không tìm thấy sản phẩm cần cập nhật.', 404));
      }

      // 3. Trả về sản phẩm đã cập nhật (200)
      resolve(Service.successResponse(updatedProduct.toJSON()));

    } catch (e) {
      reject(handleMongooseError(e));
    }
  },
);

/**
* Xóa sản phẩm (DELETE /products/{id})
* (Nhiệm vụ của Chiến - UD)
* */
const productsIdDELETE = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      if (!mongoose.Types.ObjectId.isValid(id)) {
        return reject(Service.rejectResponse('ID sản phẩm không hợp lệ.', 400));
      }
      
      // 1. Dùng Mongoose để tìm và xóa
      const result = await Product.findByIdAndDelete(id).exec();

      // 2. Xử lý trường hợp không tìm thấy (404)
      if (!result) {
        return reject(Service.rejectResponse('Không tìm thấy sản phẩm cần xóa.', 404));
      }

      // 3. Xóa thành công, trả về 204 (No Content)
      resolve(Service.successResponse(null, 204)); 

    } catch (e) {
      reject(Service.rejectResponse('Lỗi hệ thống khi xóa sản phẩm', 500));
    }
  },
);

module.exports = {
  productsGET,
  productsIdDELETE,
  productsIdGET,
  productsIdPUT,
  productsPOST,
};