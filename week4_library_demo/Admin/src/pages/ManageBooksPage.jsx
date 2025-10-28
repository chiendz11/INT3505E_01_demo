import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { deleteBook, listBooks, updateBook } from '../apis/book-service/rest/books.js';
import { Trash2, Edit, X, ArrowLeft, Search } from 'lucide-react';

const BookFormModal = ({ isOpen, onClose, onSuccess, book }) => {
    const [formData, setFormData] = useState({ title: '', author: '', available_copies: '' });
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (book) {
            setFormData({
                title: book.title,
                author: book.author,
                available_copies: book.available_copies
            });
        }
    }, [book]);

    if (!isOpen) return null;

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        try {
            const copies = parseInt(formData.available_copies, 10);
            if (isNaN(copies) || copies < 0) throw new Error("Số lượng không hợp lệ.");
            
            await updateBook(book.id, { ...formData, available_copies: copies });
            onSuccess(`Cập nhật sách "${formData.title}" thành công!`);
        } catch (err) {
            setError(err.response?.data?.message || err.message || 'Cập nhật thất bại.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-lg relative animate-fade-in-down">
                <button onClick={onClose} className="absolute top-4 right-4 text-gray-500 hover:text-gray-800"><X /></button>
                <h2 className="text-2xl font-bold mb-6">Chỉnh sửa sách</h2>
                <form onSubmit={handleSubmit}>
                    <div className="mb-4"><label className="block mb-1 font-medium">Tên sách</label><input name="title" value={formData.title} onChange={handleChange} className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required /></div>
                    <div className="mb-4"><label className="block mb-1 font-medium">Tác giả</label><input name="author" value={formData.author} onChange={handleChange} className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required /></div>
                    <div className="mb-4"><label className="block mb-1 font-medium">Số lượng</label><input type="number" name="available_copies" value={formData.available_copies} onChange={handleChange} className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500" required min="0" /></div>
                    {error && <p className="text-red-500 mb-4">{error}</p>}
                    <div className="flex justify-end space-x-4"><button type="button" onClick={onClose} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">Hủy</button><button type="submit" disabled={isLoading} className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-blue-300">{isLoading ? 'Đang lưu...' : 'Lưu thay đổi'}</button></div>
                </form>
            </div>
        </div>
    );
};

// --- Component: Modal Xác nhận Xóa ---
const DeleteConfirmModal = ({ isOpen, onClose, onConfirm, bookName, isLoading }) => {
    if (!isOpen) return null;
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md animate-fade-in-down">
                <h2 className="text-xl font-bold mb-4">Xác nhận xóa</h2>
                <p>Bạn có chắc chắn muốn xóa cuốn sách "{bookName}" không?</p>
                <div className="flex justify-end space-x-4 mt-6"><button onClick={onClose} disabled={isLoading} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">Hủy</button><button onClick={onConfirm} disabled={isLoading} className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">{isLoading ? 'Đang xóa...' : 'Xóa'}</button></div>
            </div>
        </div>
    );
};

// --- Component chính: ManageBooksPage ---
const ManageBooksPage = () => {
    const [booksData, setBooksData] = useState(null);
    const [page, setPage] = useState(1);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');
    const [modalState, setModalState] = useState({ isOpen: false, book: null });
    const [deleteState, setDeleteState] = useState({ isOpen: false, book: null, isLoading: false });

    // 🔍 Thêm state để lọc theo tác giả
    const [authorFilter, setAuthorFilter] = useState('');
    const [searchInput, setSearchInput] = useState('');

    const fetchBooks = useCallback(async () => {
        setIsLoading(true);
        setError('');
        try {
            const data = await listBooks(page, 10, authorFilter);
            setBooksData(data);
        } catch (err) {
            setError('Không thể tải danh sách sách.');
        } finally {
            setIsLoading(false);
        }
    }, [page, authorFilter]);

    useEffect(() => { fetchBooks(); }, [fetchBooks]);
    
    const handleSuccess = (message) => {
        setSuccessMessage(message);
        setModalState({ isOpen: false, book: null });
        fetchBooks();
        setTimeout(() => setSuccessMessage(''), 4000);
    };

    const handleDelete = async () => {
        if (!deleteState.book) return;
        setDeleteState(prev => ({ ...prev, isLoading: true }));
        try {
            await deleteBook(deleteState.book.id);
            setDeleteState({ isOpen: false, book: null, isLoading: false });
            handleSuccess(`Đã xóa sách "${deleteState.book.title}"!`);
        } catch (err) {
            setError('Xóa sách thất bại.');
            setDeleteState({ isOpen: false, book: null, isLoading: false });
        }
    };

    const handleSearch = () => {
        setPage(1);
        setAuthorFilter(searchInput.trim());
    };

    const handleClearFilter = () => {
        setSearchInput('');
        setAuthorFilter('');
        setPage(1);
    };

    return (
        <div className="container mx-auto p-6 md:p-10 bg-gray-50 min-h-screen">
            <Link to="/dashboard" className="inline-flex items-center text-green-700 hover:underline mb-8">
                <ArrowLeft size={20} className="mr-2" />
                Quay lại Bảng điều khiển
            </Link>
            <h1 className="text-3xl font-bold text-gray-800 mb-8">Sửa & Xóa Sách</h1>
            
            {/* ✅ Thanh tìm kiếm tác giả */}
            <div className="flex flex-wrap items-center gap-3 mb-6">
                <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Nhập tên tác giả..."
                    className="flex-grow md:w-1/3 border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500"
                />
                <button
                    onClick={handleSearch}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-2"
                >
                    <Search size={18} /> Tìm kiếm
                </button>
                {authorFilter && (
                    <button
                        onClick={handleClearFilter}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                    >
                        Xóa lọc
                    </button>
                )}
            </div>

            {successMessage && <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded-md mb-6 shadow">{successMessage}</div>}
            {error && <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md mb-6 shadow">{error}</div>}

            {isLoading ? <p className="text-center text-gray-600">Đang tải danh sách sách...</p> : (
                <>
                    <div className="bg-white shadow-md rounded-lg overflow-x-auto">
                        <table className="min-w-full leading-normal">
                            <thead>
                                <tr>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase">Tên sách</th>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase">Tác giả</th>
                                    <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-center text-xs font-semibold text-gray-600 uppercase">Hành động</th>
                                </tr>
                            </thead>
                            <tbody>
                                {booksData?.data.length > 0 ? (
                                    booksData.data.map(book => (
                                        <tr key={book.id}>
                                            <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm font-medium text-gray-900">{book.title}</td>
                                            <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm text-gray-700">{book.author}</td>
                                            <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm text-center">
                                                <button onClick={() => setModalState({ isOpen: true, book })} className="text-indigo-600 hover:text-indigo-900 mr-4" title="Sửa"><Edit size={20} /></button>
                                                <button onClick={() => setDeleteState({ isOpen: true, book, isLoading: false })} className="text-red-600 hover:text-red-900" title="Xóa"><Trash2 size={20} /></button>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr><td colSpan="3" className="text-center py-6 text-gray-500">Không có sách nào.</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                    
                    {booksData && booksData.metadata.total_pages > 1 && (
                        <div className="flex justify-center items-center mt-8 space-x-4">
                            <button onClick={() => setPage(p => p - 1)} disabled={page === 1} className="px-4 py-2 border rounded disabled:opacity-50">Trước</button>
                            <span className="font-medium text-gray-700">Trang {page} / {booksData.metadata.total_pages}</span>
                            <button onClick={() => setPage(p => p + 1)} disabled={page === booksData.metadata.total_pages} className="px-4 py-2 border rounded disabled:opacity-50">Sau</button>
                        </div>
                    )}
                </>
            )}

            <BookFormModal isOpen={modalState.isOpen} onClose={() => setModalState({ isOpen: false, book: null })} onSuccess={handleSuccess} book={modalState.book} />
            <DeleteConfirmModal isOpen={deleteState.isOpen} onClose={() => setDeleteState({ isOpen: false, book: null, isLoading: false })} onConfirm={handleDelete} bookName={deleteState.book?.title} isLoading={deleteState.isLoading} />
        </div>
    );
};

export default ManageBooksPage;