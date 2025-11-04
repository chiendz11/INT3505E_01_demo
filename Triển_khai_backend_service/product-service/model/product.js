const mongoose = require('mongoose');

const ProductSchema = new mongoose.Schema({
  // Thuộc tính cần thiết (từ ProductCreate)
  name: { type: String, required: true },
  category: { type: String, required: true },
  type: { 
    type: String, 
    enum: ['book', 'toy', 'office_supply'], // Từ enum trong OpenAPI
    required: true 
  },
  price: { type: Number, required: true, min: 0 },
  
  // Thuộc tính tùy chọn
  stock: { type: Number, default: 0, min: 0 }, // Tồn kho
  discount: { type: Number, default: 0, min: 0, max: 100 }, // Giảm giá (ví dụ: %)
  description: String,
  images: [String],
  
  // Thuộc tính bổ sung
  author: String,
  publisher: String,
  language: String,
  brand: String,
  material: String,
  size: String,
  weight: String,
  age_range: String,
  
  // Mongoose tự động tạo _id
}, { 
  timestamps: true // Tự động thêm createdAt và updatedAt
});

// Chuyển 'id' của Mongoose thành 'id' trong JSON trả về (như OpenAPI)
ProductSchema.set('toJSON', {
  virtuals: true,
  transform: (doc, ret) => {
    ret.id = ret._id;
    delete ret._id;
    delete ret.__v;
  }
});

module.exports = mongoose.model('Product', ProductSchema);