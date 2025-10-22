export function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString(); // Sử dụng định dạng ngày mặc định của trình duyệt
  }
  