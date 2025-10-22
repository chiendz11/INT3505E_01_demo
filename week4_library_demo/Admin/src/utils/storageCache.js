// A simple localStorage cache wrapper
export const storageCache = {
    // Thêm prefix để tránh đè key của các ứng dụng khác
    prefix: 'api_cache_',
  
    /**
     * Lưu cache vào localStorage
     * @param {string} key - Key (đã bao gồm prefix)
     * @param {object} cacheEntry - { data, etag, expiresAt }
     */
    _set: (fullKey, cacheEntry) => {
      try {
        localStorage.setItem(fullKey, JSON.stringify(cacheEntry));
      } catch (e) {
        // Lỗi này thường xảy ra khi localStorage bị đầy
        console.warn("localStorage quota exceeded. Clearing cache.", e);
        // Chính sách đơn giản: xóa bớt cache cũ (hoặc xóa hết)
        storageCache.clear('list_books_'); 
      }
    },
  
    /**
     * Lấy cache từ localStorage
     * @param {string} key - Key (đã bao gồm prefix)
     * @returns {null | {data: any, etag: string, expiresAt: number}}
     */
    _get: (fullKey) => {
      const item = localStorage.getItem(fullKey);
      if (!item) {
        return null;
      }
      try {
        // Parse dữ liệu từ chuỗi JSON
        return JSON.parse(item);
      } catch (e) {
        // Nếu dữ liệu lưu bị hỏng, xóa nó đi
        console.warn("Failed to parse cache entry. Removing.", e);
        localStorage.removeItem(fullKey);
        return null;
      }
    },
  
    // --- Các hàm public ---
  
    /**
     * Lấy cache, đồng thời kiểm tra xem nó còn "tươi" (fresh) không
     * @param {string} key - Key (chưa có prefix)
     * @returns {null | object} Chỉ trả về data nếu cache còn hạn
     */
    getFresh: (key) => {
      const entry = storageCache._get(storageCache.prefix + key);
      const now = Date.now();
      
      // Nếu cache tồn tại VÀ chưa hết hạn
      if (entry && entry.expiresAt > now) {
        console.log("CACHE HIT (Fresh/localStorage):", key);
        return entry.data; // Chỉ trả về data
      }
      // Nếu hết hạn hoặc không có, trả null
      return null;
    },
  
    /**
     * Lấy cache "cũ" (stale), chủ yếu để lấy ETag
     * @param {string} key - Key (chưa có prefix)
     */
    getStale: (key) => {
       const entry = storageCache._get(storageCache.prefix + key);
       return entry; // Trả về cả { data, etag, expiresAt }
    },
    
    /**
     * Set cache mới
     * @param {string} key - Key (chưa có prefix)
     * @param {object} data - Dữ liệu JSON từ response
     * @param {string} etag - ETag từ header
     * @param {number} maxAgeInSeconds - max-age từ header
     */
    set: (key, data, etag, maxAgeInSeconds) => {
      const fullKey = storageCache.prefix + key;
      const expiresAt = Date.now() + (maxAgeInSeconds * 1000);
      const cacheEntry = {
        data: data,
        etag: etag,
        expiresAt: expiresAt
      };
      storageCache._set(fullKey, cacheEntry);
    },
  
    /**
     * Xóa một key cụ thể
     */
    delete: (key) => {
      localStorage.removeItem(storageCache.prefix + key);
    },
  
    /**
     * Xóa tất cả cache có prefix (ví dụ: 'list_books_')
     */
    clear: (prefix = '') => {
      const fullPrefix = storageCache.prefix + prefix;
      Object.keys(localStorage)
        .filter(k => k.startsWith(fullPrefix))
        .forEach(k => localStorage.removeItem(k));
    }
  };
  
  // Hàm helper parse max-age (giữ nguyên)
  function parseMaxAge(cacheControlHeader) {
    if (!cacheControlHeader) return 0;
    const match = cacheControlHeader.match(/max-age=(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }