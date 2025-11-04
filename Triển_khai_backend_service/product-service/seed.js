// seed.js

const mongoose = require('mongoose');
const { faker } = require('@faker-js/faker'); 
const Product = require('./model/product'); // Giả định bạn có model Product
const connectDB = require('./db/mongoose'); // Hàm kết nối DB của bạn

// Dữ liệu mẫu (theo openAPI.yaml)
const categories = ['Văn học', 'Tâm lý kỹ năng', 'Đồ chơi', 'Văn phòng phẩm'];
const types = ['book', 'toy', 'office_supply'];

const createRandomProduct = () => {
  const categoryName = faker.helpers.arrayElement(categories);
  let productType;

  // Gán type phù hợp với category (ví dụ đơn giản)
  if (categoryName === 'Văn học' || categoryName === 'Tâm lý kỹ năng') {
    productType = 'book';
  } else if (categoryName === 'Đồ chơi') {
    productType = 'toy';
  } else {
    productType = 'office_supply';
  }

  return {
    name: productType === 'book' ? faker.commerce.productName() + ' - ' + faker.person.lastName() : faker.commerce.productName(),
    category: categoryName,
    type: productType,
    price: faker.number.float({ min: 50000, max: 500000, precision: 1000 }), // Giá từ 50k đến 500k
    stock: faker.number.int({ min: 1, max: 300 }), // Tồn kho từ 1 đến 300
    discount: faker.number.int({ min: 0, max: 50 }), // Giảm giá từ 0% đến 50%
    description: faker.lorem.paragraph(),
    images: Array.from({ length: 2 }, () => faker.image.urlLoremFlickr({ category: productType })),
    
    // Thuộc tính bổ sung
    author: productType === 'book' ? faker.person.fullName() : undefined,
    publisher: productType === 'book' ? faker.company.name() : undefined,
  };
};

const seedDB = async (count) => {
  await connectDB(); // Kết nối DB
  try {
    console.log('Bắt đầu xóa dữ liệu cũ...');
    await Product.deleteMany({}); // Xóa tất cả bản ghi cũ

    console.log(`Bắt đầu tạo ${count} bản ghi mới...`);
    const productData = Array.from({ length: count }, createRandomProduct);
    
    // Tạo và lưu vào DB
    await Product.insertMany(productData); 

    console.log(`✅ Đã tạo thành công ${count} bản ghi sản phẩm.`);
  } catch (error) {
    console.error('❌ Lỗi khi thực hiện Seeding:', error);
  } finally {
    mongoose.connection.close(); // Đóng kết nối
    console.log('Đã đóng kết nối DB.');
  }
};

// Chạy hàm tạo 100 bản ghi
seedDB(100);