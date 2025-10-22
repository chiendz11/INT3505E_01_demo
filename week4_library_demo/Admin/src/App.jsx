import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import BorrowBooksPage from './pages/BorrowBooksPage';
import ReturnBooksPage from './pages/ReturnBooksPage';
import AddBookPage from './pages/AddBooksPage';
import ManageBooksPage from './pages/ManageBooksPage';

// [FIX] Cập nhật logic để đọc object 'user' từ localStorage
const ProtectedRoute = () => {
  const userStr = localStorage.getItem('user');
  // Nếu có thông tin user, cho phép truy cập, ngược lại điều hướng về trang login
  return userStr ? <Outlet /> : <Navigate to="/login" replace />;
};

// [FIX] Cập nhật logic để đọc và kiểm tra vai trò từ object 'user'
const AdminRoute = () => {
    const userStr = localStorage.getItem('user');
    
    // Nếu không có thông tin user, không thể là admin -> về trang login
    if (!userStr) {
        return <Navigate to="/login" replace />;
    }

    try {
        const user = JSON.parse(userStr);
        // Kiểm tra xem user có tồn tại và có vai trò 'ADMIN' không
        return user && user.role === 'ADMIN' 
            ? <Outlet /> 
            : <Navigate to="/dashboard" replace />; // Nếu đăng nhập nhưng không phải admin, về dashboard
    } catch (e) {
        console.error("Lỗi parse user data:", e);
        // Nếu dữ liệu trong localStorage bị lỗi, coi như chưa đăng nhập
        return <Navigate to="/login" replace />;
    }
}

function App() {
  return (
    <Router>
      <Routes>
        {/* Route mặc định sẽ chuyển về login */}
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />

        {/* --- Các route yêu cầu phải đăng nhập (cho cả USER và ADMIN) --- */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/borrow-books" element={<BorrowBooksPage />} />
          <Route path="/return-books" element={<ReturnBooksPage />} />
        </Route>

        {/* --- Các route chỉ dành cho ADMIN --- */}
        <Route element={<AdminRoute />}>
            <Route path="/admin/add-book" element={<AddBookPage />} />
            <Route path="/admin/manage-books" element={<ManageBooksPage />} />
        </Route>

      </Routes>
    </Router>
  );
}

export default App;
