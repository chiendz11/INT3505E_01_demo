// File: src/apis/bookAPI.js

import axiosInstance from '../config/axiosConfig';
// Giả sử đường dẫn này đúng: src/apis/ -> ../ -> src/ -> utils/storageCache.js
import { storageCache } from '../utils/storageCache';


// --- HÀM DÀNH CHO CẢ USER VÀ ADMIN ---

// Định nghĩa key tập trung
const listBooksKey = (page, limit, author) => `list_books_${page}|${limit}|${author}`;
const bookKey = (id) => `book_${id}`;


export async function listBooks(page = 1, limit = 10, author_filter = '') {
  try {
    const key = listBooksKey(page, limit, author_filter);

    // 1. KIỂM TRA CACHE "TƯƠI"
    const freshData = storageCache.getFresh(key);
    if (freshData) {
      return freshData; // Trả về ngay, không cần gọi mạng
    }

    // 2. CHUẨN BỊ GỌI MẠNG (CACHE ĐÃ "CŨ" HOẶC KHÔNG CÓ)
    const headers = {};
    const staleCache = storageCache.getStale(key); // Lấy cache cũ
    
    if (staleCache?.etag) {
      console.log("CACHE STALE (Validating/localStorage):", key);
      headers['If-None-Match'] = staleCache.etag;
    } else {
      console.log("CACHE MISS (Fetching/localStorage):", key);
    }

    const params = { page, limit };
    if (author_filter.trim()) params.author_filter = author_filter.trim();

    // 3. GỌI MẠNG
    const response = await axiosInstance.get('/api/books', { params, headers });

    // 4. XỬ LÝ 200 OK (DỮ LIỆU MỚI)
    // (Lưu ý: axios ném lỗi cho status 304, nên nó sẽ nhảy vào catch)
    if (response.status === 200) {
      console.log("NETWORK 200 (Updating localStorage):", key);
      const maxAgeInSeconds = storageCache.parseMaxAge(response.headers['cache-control']);
      storageCache.set(
        key,
        response.data,
        response.headers.etag,
        maxAgeInSeconds
      );
      return response.data;
    }
  } catch (error) {
    // 5. XỬ LÝ 304 NOT MODIFIED
    const key = listBooksKey(page, limit, author_filter);
    
    if (error.response?.status === 304) {
      console.log("NETWORK 304 (Re-validating localStorage):", key);
      const staleCache = storageCache.getStale(key); // Lấy lại cache cũ

      if (staleCache) {
        const maxAgeInSeconds = storageCache.parseMaxAge(error.response.headers['cache-control']);
        // "Làm mới" cache cũ với thời gian hết hạn mới
        storageCache.set(
          key,
          staleCache.data, // Dùng lại data cũ
          staleCache.etag, // Dùng lại etag cũ
          maxAgeInSeconds  // Set TTL mới
        );
        return staleCache.data; // Trả về data cũ
      }
    }
    
    // 6. XỬ LÝ LỖI THỰC SỰ
    console.error('Lỗi khi lấy danh sách sách:', error);
    throw error.response?.data || { message: 'Không thể tải danh sách sách' };
  }
}

export async function listBooksCursor(cursor = null) {
  try {
    const params = cursor ? { cursor } : {};
    // Tương ứng với: GET /api/books/cursor
    // (Cursor-based pagination thường không cache theo kiểu này, nên bỏ qua cache là OK)
    const response = await axiosInstance.get('/api/books/cursor', { params });
    return response.data;
  } catch (error) {
    console.error('Lỗi khi lấy danh sách sách (cursor):', error);
    throw error.response?.data || { message: 'Không thể tải danh sách sách' };
  }
}

/**
 * Lấy thông tin một cuốn sách theo ID (ĐÃ CẬP NHẬT DÙNG storageCache)
 */
export async function getBookById(bookId) {
  try {
    const key = bookKey(bookId);

    // 1. KIỂM TRA CACHE "TƯƠI"
    const freshData = storageCache.getFresh(key);
    if (freshData) {
      return freshData;
    }

    // 2. CHUẨN BỊ GỌI MẠNG
    const headers = {};
    const staleCache = storageCache.getStale(key);
    
    if (staleCache?.etag) {
      console.log("CACHE STALE (Validating/localStorage):", key);
      headers['If-None-Match'] = staleCache.etag;
    } else {
      console.log("CACHE MISS (Fetching/localStorage):", key);
    }

    // 3. GỌI MẠNG
    const response = await axiosInstance.get(`/api/books/${bookId}`, { headers });

    // 4. XỬ LÝ 200 OK
    if (response.status === 200) {
      console.log("NETWORK 200 (Updating localStorage):", key);
      const maxAgeInSeconds = storageCache.parseMaxAge(response.headers['cache-control']);
      storageCache.set(
        key,
        response.data,
        response.headers.etag,
        maxAgeInSeconds
      );
      return response.data;
    }
  } catch (error) {
    // 5. XỬ LÝ 304 NOT MODIFIED
    const key = bookKey(bookId);
    
    if (error.response?.status === 304) {
      console.log("NETWORK 304 (Re-validating localStorage):", key);
      const staleCache = storageCache.getStale(key);

      if (staleCache) {
        const maxAgeInSeconds = storageCache.parseMaxAge(error.response.headers['cache-control']);
        storageCache.set(
          key,
          staleCache.data,
          staleCache.etag,
          maxAgeInSeconds
        );
        return staleCache.data;
      }
    }
    
    // 6. XỬ LÝ LỖI THỰC SỰ
    console.error(`Lỗi khi lấy sách có ID ${bookId}:`, error);
    throw error.response?.data || { message: 'Không thể tìm thấy sách' };
  }
}

// --- HÀM CHỈ DÀNH CHO ADMIN ---

/**
 * Tạo một cuốn sách mới (chỉ dành cho Admin).
 */
export async function createBook(bookData) {
  try {
    // Tương ứng với: POST /api/books
    const response = await axiosInstance.post('/api/books', bookData);
    
    // VÔ HIỆU HÓA CACHE: Xóa tất cả cache của listBooks
    storageCache.clear('list_books_');
    
    return response.data;
  } catch (error) {
    console.error('Lỗi khi tạo sách mới:', error);
    throw error.response?.data || { message: 'Không thể tạo sách' };
  }
}

/**
 * Cập nhật thông tin một cuốn sách (chỉ dành cho Admin).
 */
export async function updateBook(bookId, bookData) {
  try {
    // Tương ứng với: PUT /api/books/<book_id>
    const response = await axiosInstance.put(`/api/books/${bookId}`, bookData);
    
    // VÔ HIỆU HÓA CACHE
    storageCache.clear('list_books_'); // Xóa cache listBooks
    storageCache.delete(bookKey(bookId)); // Xóa cache của chính sách này
    
    return response.data;
  } catch (error) {
    console.error(`Lỗi khi cập nhật sách có ID ${bookId}:`, error);
    throw error.response?.data || { message: 'Không thể cập nhật sách' };
  }
}

/**
 * Xóa một cuốn sách (chỉ dành cho Admin).
 */
export async function deleteBook(bookId) {
  try {
    // Tương ứng với: DELETE /api/books/<book_id>
    const response = await axiosInstance.delete(`/api/books/${bookId}`);
    
    // VÔ HIỆU HÓA CACHE
    storageCache.clear('list_books_'); // Xóa cache listBooks
    storageCache.delete(bookKey(bookId)); // Xóa cache của chính sách này
    
    return response.data;
  } catch (error) {
    console.error(`Lỗi khi xóa sách có ID ${bookId}:`, error);
    throw error.response?.data || { message: 'Không thể xóa sách' };
  }
}