import React, { useState, useEffect } from 'react';
import { Link, useNavigate, Navigate } from 'react-router-dom';
import { BookPlus, Wrench } from 'lucide-react';

// Giao diện cho người dùng thông thường (USER)
const UserDashboard = ({ username, onLogout }) => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
    <div className="w-full max-w-2xl p-8 space-y-8 bg-white rounded-xl shadow-lg text-center">
      <h1 className="text-3xl font-bold text-gray-800">
        Chào mừng trở lại, <span className="text-green-600">{username}</span>!
      </h1>
      <p className="text-gray-600">Chọn một chức năng để bắt đầu.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
        <Link 
          to="/borrow-books" 
          className="px-6 py-4 font-semibold text-white bg-green-600 rounded-lg hover:bg-green-700 transition-all duration-300 transform hover:scale-105 shadow-md"
        >
          Mượn Sách
        </Link>
        <Link 
          to="/return-books"
          className="px-6 py-4 font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 shadow-md"
        >
          Trả Sách
        </Link>
      </div>

      <div className="pt-8 border-t mt-8">
        <button 
          onClick={onLogout}
          className="w-full md:w-auto px-8 py-3 font-semibold text-red-600 bg-transparent border border-red-600 rounded-lg hover:bg-red-600 hover:text-white transition-colors duration-300"
        >
          Đăng xuất
        </button>
      </div>
    </div>
  </div>
);

// Giao diện cho Quản trị viên (ADMIN)
const AdminDashboardMenu = ({ username, onLogout }) => (
  <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
    <div className="w-full max-w-4xl p-10 space-y-8 bg-gray-800 rounded-xl shadow-2xl text-center">
      <h1 className="text-4xl font-bold">Admin Control Panel</h1>
      <p className="text-gray-400">Xin chào, Quản trị viên <span className="text-yellow-400">{username}</span>.</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
        <Link to="/admin/add-book" className="flex flex-col items-center justify-center p-6 bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors font-semibold">
            <BookPlus size={40} className="mb-2" />
            Thêm Sách Mới
        </Link>
        <Link to="/admin/manage-books" className="flex flex-col items-center justify-center p-6 bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors font-semibold">
            <Wrench size={40} className="mb-2" />
            Sửa & Xóa Sách
        </Link>
      </div>
      
      <div className="pt-8 border-t border-gray-700 mt-8">
        <button onClick={onLogout} className="px-8 py-3 font-semibold text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors">
          Đăng xuất
        </button>
      </div>
    </div>
  </div>
);

// Component chính - ĐÃ SỬA LẠI
const Dashboard = () => {
    const navigate = useNavigate();
    // [FIX] Dùng state để lưu thông tin user, thay vì đọc trực tiếp
    const [user, setUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // [FIX] Ưu tiên đọc object 'user' từ localStorage
        const userStr = localStorage.getItem('user');
        
        if (userStr) {
            try {
                // Nếu có, giải mã và set vào state
                const parsedUser = JSON.parse(userStr);
                setUser(parsedUser);
            } catch (error) {
                console.error("Lỗi giải mã thông tin người dùng từ localStorage:", error);
                // Nếu lỗi, xóa dữ liệu hỏng và coi như chưa đăng nhập
                localStorage.clear();
            }
        }
        
        // Đánh dấu đã kiểm tra xong
        setIsLoading(false);
    }, []);

    const handleLogout = () => {
        // [FIX] Xóa tất cả các key liên quan để đảm bảo sạch sẽ
        localStorage.removeItem('user');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('username'); // Xóa key cũ nếu có
        localStorage.removeItem('role'); // Xóa key cũ nếu có
        navigate('/login');
    };

    // Trong lúc đang kiểm tra localStorage, có thể hiện loading
    if (isLoading) {
        return <div className="flex items-center justify-center min-h-screen">Đang tải...</div>;
    }

    // Nếu không có user sau khi kiểm tra, điều hướng về trang đăng nhập
    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // Render dashboard tương ứng với vai trò
    return user.role === 'ADMIN' 
        ? <AdminDashboardMenu username={user.username} onLogout={handleLogout} /> 
        : <UserDashboard username={user.username} onLogout={handleLogout} />;
};

export default Dashboard;
