import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createBook } from '../apis/bookAPI'; // Giả sử file này tồn tại
import { ArrowLeft } from 'lucide-react';

const AddBookPage = () => {
    const [formData, setFormData] = useState({ title: '', author: '', available_copies: '' });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setSuccess('');
        try {
            const copies = parseInt(formData.available_copies, 10);
            if (isNaN(copies) || copies < 0) {
                throw new Error("Số lượng phải là một số không âm.");
            }
            const dataToSubmit = { ...formData, available_copies: copies };
            await createBook(dataToSubmit);
            setSuccess(`Đã thêm thành công sách "${formData.title}"!`);
            // Reset form
            setFormData({ title: '', author: '', available_copies: '' });
            // Tùy chọn: Chuyển hướng sau một khoảng thời gian
            setTimeout(() => navigate('/admin/manage-books'), 2000);
        } catch (err) {
            setError(err.response?.data?.message || err.message || 'Thêm sách thất bại.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
            <div className="w-full max-w-2xl">
                <Link to="/dashboard" className="inline-flex items-center text-green-700 hover:underline mb-6">
                    <ArrowLeft size={20} className="mr-2" />
                    Quay lại Bảng điều khiển
                </Link>
                <div className="bg-white p-8 rounded-xl shadow-lg">
                    <h1 className="text-3xl font-bold text-gray-800 mb-6">Thêm Sách Mới</h1>
                    <form onSubmit={handleSubmit}>
                        <div className="mb-4">
                            <label htmlFor="title" className="block text-gray-700 font-medium mb-2">Tên sách</label>
                            <input
                                id="title"
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                                required
                            />
                        </div>
                        <div className="mb-4">
                            <label htmlFor="author" className="block text-gray-700 font-medium mb-2">Tác giả</label>
                            <input
                                id="author"
                                name="author"
                                value={formData.author}
                                onChange={handleChange}
                                className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                                required
                            />
                        </div>
                        <div className="mb-6">
                            <label htmlFor="available_copies" className="block text-gray-700 font-medium mb-2">Số lượng bản có sẵn</label>
                            <input
                                id="available_copies"
                                type="number"
                                name="available_copies"
                                value={formData.available_copies}
                                onChange={handleChange}
                                className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                                required
                                min="0"
                            />
                        </div>
                        
                        {error && <p className="text-red-500 mb-4 text-center">{error}</p>}
                        {success && <p className="text-green-600 mb-4 text-center">{success}</p>}

                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full bg-green-600 text-white py-3 rounded-md font-semibold hover:bg-green-700 transition-colors disabled:opacity-50"
                        >
                            {isLoading ? 'Đang lưu...' : 'Thêm Sách'}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default AddBookPage;
