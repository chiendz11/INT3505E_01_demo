// product-service/db/mongoose.js

const mongoose = require('mongoose');

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/bookstore_product_db';

const connectDB = async () => {
  try {
    // 1. Kết nối với MongoDB
    await mongoose.connect(MONGODB_URI, {
      useNewUrlParser: true,       // Khuyến nghị cho Mongoose
      useUnifiedTopology: true,    // Khuyến nghị cho Mongoose
      // useFindAndModify: false,  // Tùy chọn, nếu bạn dùng findByIdAndUpdate
      // useCreateIndex: true,     // Tùy chọn
    });
    
    // 2. Log khi kết nối thành công
    console.log('✅ MongoDB connected successfully to:', MONGODB_URI);
    
    // 3. Xử lý lỗi sau khi kết nối
    mongoose.connection.on('error', err => {
        console.error('❌ MongoDB connection error:', err);
    });

  } catch (error) {
    // Log và thoát nếu kết nối thất bại
    console.error('❌ MongoDB initial connection failed:', error.message);
    process.exit(1);
  }
};

module.exports = connectDB;