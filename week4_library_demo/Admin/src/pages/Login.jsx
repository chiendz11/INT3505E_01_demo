import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { login, register, loginWithGoogle } from '../apis/authAPI.js';
import axiosInstance from '../config/axiosConfig.js';
import { Eye, EyeOff, X } from 'lucide-react';

// --- Component Modal Đăng ký ---
const RegisterModal = ({ isOpen, onClose, onRegisterSuccess }) => {
    const [formData, setFormData] = useState({ email: '', username: '', password: '' });
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    if (!isOpen) return null;

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.email || !formData.username || !formData.password) {
            setError('Vui lòng điền đầy đủ thông tin.');
            return;
        }
        setError(null);
        setIsLoading(true);
        try {
            await register(formData);
            onRegisterSuccess();
        } catch (err) {
            setError(err.response?.data?.error || err.message || 'Đăng ký thất bại. Vui lòng thử lại.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 transition-opacity">
            <div className="bg-white rounded-lg shadow-xl p-8 w-full max-w-md relative animate-fade-in-down">
                <button onClick={onClose} className="absolute top-4 right-4 text-gray-500 hover:text-gray-800 transition-colors">
                    <X size={24} />
                </button>
                <h2 className="text-2xl font-bold text-green-800 mb-4">Đăng ký tài khoản</h2>
                {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">Email</label>
                        <input id="email" name="email" type="email" placeholder="Nhập email của bạn" className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" value={formData.email} onChange={handleInputChange} required />
                    </div>
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username_reg">Tên đăng nhập</label>
                        <input id="username_reg" name="username" type="text" placeholder="Tên đăng nhập" className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" value={formData.username} onChange={handleInputChange} required />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password_reg">Mật khẩu</label>
                        <input id="password_reg" name="password" type="password" placeholder="Nhập mật khẩu" className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500" value={formData.password} onChange={handleInputChange} required />
                    </div>
                    <button type="submit" disabled={isLoading} className="w-full bg-green-600 text-white py-3 rounded-md hover:bg-green-700 transition-colors disabled:opacity-70 disabled:cursor-not-allowed font-semibold">
                        {isLoading ? 'Đang xử lý...' : 'ĐĂNG KÝ'}
                    </button>
                </form>
            </div>
        </div>
    );
};

// --- Component Đăng nhập chính ---
const Login = () => {
    const [showPassword, setShowPassword] = useState(false);
    const [loginData, setLoginData] = useState({ login: '', password: '' });
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
    const [registerSuccessMessage, setRegisterSuccessMessage] = useState('');

    const navigate = useNavigate();
    const location = useLocation();

    // Xử lý callback từ Google sau khi đăng nhập thành công
    useEffect(() => {
        const hash = location.hash;
        if (hash.includes('accessToken') && hash.includes('user')) {
            const params = new URLSearchParams(hash.substring(1));
            const accessTokenFromGoogle = params.get('accessToken');
            const userStrEncoded = params.get('user');

            if (accessTokenFromGoogle && userStrEncoded) {
                try {
                    console.log(accessTokenFromGoogle, "\n", userStrEncoded)
                    const user = JSON.parse(decodeURIComponent(userStrEncoded));
                    axiosInstance.setAuthToken(accessTokenFromGoogle);
                    localStorage.setItem('user', JSON.stringify(user));
                    
                    // [FIX] Chuyển hướng đến /dashboard cho BẤT KỲ vai trò nào
                    navigate('/dashboard'); 
                } catch (e) {
                    console.error("Lỗi xử lý callback từ Google:", e);
                    setError("Lỗi xử lý thông tin đăng nhập từ Google.");
                }
            } else if (hash.includes('error')) {
                 setError("Đăng nhập bằng Google thất bại. Vui lòng thử lại.");
            }
            // Xóa hash khỏi URL để tránh xử lý lại
            window.history.replaceState(null, "", window.location.pathname + window.location.search);
        }
    }, [location, navigate]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setLoginData({ ...loginData, [name]: value });
    };

    const handleLogin = async () => {
        if (!loginData.login || !loginData.password) {
            setError('Vui lòng điền đầy đủ thông tin');
            return;
        }
        try {
            setError(null);
            setRegisterSuccessMessage('');
            setIsLoading(true);

            const response = await login(loginData);
            const { access_token: accessToken, user } = response;

            if (!accessToken || !user) {
                throw new Error("Dữ liệu trả về từ server không hợp lệ");
            }

            axiosInstance.setAuthToken(accessToken);
            localStorage.setItem("user", JSON.stringify(user));

            // [FIX] Chuyển hướng đến /dashboard cho BẤT KỲ vai trò nào
            navigate("/dashboard");

        } catch (err) {
            const errorMessage = err.response?.data?.error || err.message || 'Đăng nhập thất bại';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    const handleRegisterSuccess = () => {
        setIsRegisterModalOpen(false);
        setRegisterSuccessMessage('Đăng ký thành công! Vui lòng đăng nhập.');
    };

    return (
        <>
            <RegisterModal 
                isOpen={isRegisterModalOpen} 
                onClose={() => setIsRegisterModalOpen(false)}
                onRegisterSuccess={handleRegisterSuccess}
            />
            <div className="flex min-h-screen bg-gray-50">
                <div className="hidden md:block md:w-1/3 lg:w-1/2">
                    <img src="https://placehold.co/800x1200/a3e635/14532d?text=BadMan" alt="Background" className="object-cover w-full h-full" />
                </div>
                <div className="flex items-center justify-center w-full md:w-2/3 lg:w-1/2">
                    <div className="w-full max-w-md px-10 py-12 bg-white rounded-xl shadow-lg m-4">
                        <h2 className="text-3xl font-bold text-gray-800 mb-2 text-center">Chào mừng trở lại</h2>
                        <p className="text-sm text-gray-600 mb-8 text-center">Đăng nhập để tiếp tục với BadMan</p>

                        {error && <p className="text-center text-red-500 mb-4 font-medium">{error}</p>}
                        {registerSuccessMessage && <p className="text-center text-green-600 mb-4 font-medium">{registerSuccessMessage}</p>}

                        <div className="relative mb-4">
                            <input name="login" type="text" placeholder="Tên đăng nhập hoặc Email" className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors" value={loginData.login} onChange={handleInputChange} />
                        </div>
                        <div className="relative mb-6">
                            <input name="password" type={showPassword ? 'text' : 'password'} placeholder="Nhập mật khẩu" className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 transition-colors" value={loginData.password} onChange={handleInputChange} />
                            <span className="absolute right-3 top-3.5 text-gray-500 cursor-pointer" onClick={() => setShowPassword(!showPassword)}>
                                {showPassword ? <EyeOff size={20} title="Ẩn mật khẩu" /> : <Eye size={20} title="Hiện mật khẩu" />}
                            </span>
                        </div>
                        <button onClick={handleLogin} disabled={isLoading} className="w-full bg-green-600 text-white py-3 rounded-md mb-4 font-semibold hover:bg-green-700 transition-transform transform hover:scale-105 disabled:opacity-70 disabled:cursor-not-allowed">
                            {isLoading ? 'Đang đăng nhập...' : 'ĐĂNG NHẬP'}
                        </button>
                        <div className="flex items-center my-6">
                            <div className="flex-grow border-t border-gray-300"></div><span className="flex-shrink mx-4 text-gray-500 text-sm">HOẶC</span><div className="flex-grow border-t border-gray-300"></div>
                        </div>
                        <button onClick={loginWithGoogle} className="w-full flex items-center justify-center bg-white border border-gray-300 text-gray-700 py-3 rounded-md mb-6 hover:bg-gray-100 transition-colors">
                            <img src="https://fonts.gstatic.com/s/i/productlogos/googleg/v6/24px.svg" alt="Google icon" className="w-5 h-5 mr-3"/>
                            <span className="font-semibold">Đăng nhập với Google</span>
                        </button>
                        <p className="text-center text-sm text-gray-600">
                            Chưa có tài khoản?{' '}
                            <button onClick={() => setIsRegisterModalOpen(true)} className="font-semibold text-green-600 hover:underline">Đăng ký ngay</button>
                        </p>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Login;

