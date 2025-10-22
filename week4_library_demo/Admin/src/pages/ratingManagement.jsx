import React, { useState, useEffect } from 'react';
import { fetchRatings, deleteRating } from '../apis/ratingAPI.js';

const centers = [
  { id: '67ca6e3cfc964efa218ab7d8', name: 'Nhà thi đấu quận Thanh Xuân' },
  { id: '67ca6e3cfc964efa218ab7d9', name: 'Nhà thi đấu quận Cầu Giấy' },
  { id: '67ca6e3cfc964efa218ab7d7', name: 'Nhà thi đấu quận Tây Hồ' },
  { id: '67ca6e3cfc964efa218ab7da', name: 'Nhà thi đấu quận Bắc Từ Liêm' }
];

export default function RatingManagement() {
  const [selectedCenter, setSelectedCenter] = useState(centers[0].id);
  const [ratings, setRatings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRatings(selectedCenter);
  }, [selectedCenter]);

  const loadRatings = async (centerId) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchRatings(centerId);
      setRatings(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      setError(err.message || 'Failed to load ratings');
      setRatings([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Bạn có chắc muốn xóa đánh giá này?')) return;
    try {
      await deleteRating(id);
      setRatings((prev) => prev.filter((r) => r._id !== id));
    } catch (err) {
      alert(err.message || 'Xóa thất bại');
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">Quản lý đánh giá</h2>
      <div className="mb-4">
        <label htmlFor="center-select" className="mr-2">Chọn trung tâm:</label>
        <select
          id="center-select"
          value={selectedCenter}
          onChange={(e) => setSelectedCenter(e.target.value)}
          className="border rounded p-1"
        >
          {centers.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {loading && <p>Đang tải đánh giá...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && (
        <table className="min-w-full bg-white">
          <thead>
            <tr>
              <th className="py-2">Người dùng</th>
              <th className="py-2">Sao</th>
              <th className="py-2">Bình luận</th>
              <th className="py-2">Ngày tạo</th>
              <th className="py-2">Hành động</th>
            </tr>
          </thead>
          <tbody>
            {ratings.map((r) => (
              <tr key={r._id} className="text-center border-t">
                <td className="py-2">{r.user.username || r.user.email}</td>
                <td className="py-2">{r.stars} ★</td>
                <td className="py-2">{r.comment}</td>
                <td className="py-2">{new Date(r.createdAt).toLocaleDateString('vi-VN')}</td>
                <td className="py-2">
                  <button
                    onClick={() => handleDelete(r._id)}
                    className="px-2 py-1 bg-red-500 text-white rounded"
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))}
            {ratings.length === 0 && (
              <tr>
                <td colSpan="5" className="py-4">Chưa có đánh giá cho trung tâm này.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}