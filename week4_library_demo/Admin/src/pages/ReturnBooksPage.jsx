import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
// Sửa import: Dùng hàm API mới, bỏ hàm cũ
import { getMyBorrowedBooks, createTransaction } from '../apis/transactionAPI';

// --- Component Modal để xác nhận trả sách (Giữ nguyên không đổi) ---
const ReturnModal = ({ book, onClose, onSuccess }) => {
    const [quantity, setQuantity] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleReturn = async () => {
        const numQuantity = parseInt(quantity, 10);
        if (isNaN(numQuantity) || numQuantity <= 0) {
            setError("Số lượng phải là một số lớn hơn 0.");
            return;
        }
        if (numQuantity > book.borrowed_count) {
            setError("Số lượng trả không được vượt quá số sách đã mượn.");
            return;
        }
        
        setIsLoading(true);
        setError(null);
        try {
            await createTransaction({
                book_id: book.book_id,
                quantity: numQuantity,
                type: 'return'
            });
            onSuccess(`Trả thành công ${numQuantity} cuốn "${book.book_title}"!`);
        } catch (err) {
            setError(err.message || "Trả sách thất bại. Vui lòng thử lại.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
                <h3 className="text-xl font-bold mb-4">Xác nhận trả sách</h3>
                <p className="mb-2"><strong>Sách:</strong> {book.book_title}</p>
                <p className="mb-4"><strong>Số lượng đang mượn:</strong> {book.borrowed_count}</p>
                <div className="mb-4">
                    <label htmlFor="return_quantity" className="block text-sm font-medium text-gray-700">Số lượng muốn trả</label>
                    <input type="number" id="return_quantity" value={quantity}
                           onChange={(e) => setQuantity(e.target.value)}
                           className="mt-1 w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                           min="1" max={book.borrowed_count} autoFocus />
                </div>
                {error && <p className="text-red-600 text-sm mb-4 text-center">{error}</p>}
                <div className="flex justify-end space-x-4">
                    <button onClick={onClose} className="px-5 py-2 bg-gray-200 rounded-md hover:bg-gray-300">Hủy</button>
                    <button onClick={handleReturn} disabled={isLoading} className="px-5 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
                        {isLoading ? 'Đang xử lý...' : 'Xác nhận'}
                    </button>
                </div>
            </div>
        </div>
    );
};

// --- Component chính của trang (Đã được đơn giản hóa) ---
const ReturnBooksPage = () => {
    const [borrowedBooks, setBorrowedBooks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedBook, setSelectedBook] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');

    const fetchBorrowedBooks = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getMyBorrowedBooks(); // <-- GỌI HÀM API MỚI
            setBorrowedBooks(data); // <-- Dữ liệu đã sạch, chỉ cần set state
        } catch (err) {
            setError("Không thể tải danh sách sách đang mượn.");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchBorrowedBooks();
    }, []);
    
    // ===== BỎ HOÀN TOÀN LOGIC TÍNH TOÁN BẰNG useMemo =====

    const handleSuccess = (message) => {
        setSuccessMessage(message);
        setSelectedBook(null);
        fetchBorrowedBooks(); // Tải lại danh sách để cập nhật
        setTimeout(() => setSuccessMessage(''), 5000);
    };

    const renderContent = () => {
        if (isLoading) return <p className="text-center mt-8">Đang tải dữ liệu...</p>;
        if (error) return <p className="text-center mt-8 text-red-500">{error}</p>;
        if (borrowedBooks.length === 0) {
            return <p className="text-center mt-8 text-gray-500">Bạn chưa mượn cuốn sách nào.</p>;
        }
        return (
            <div className="space-y-4">
                {borrowedBooks.map(book => (
                    <div key={book.book_id} className="flex items-center justify-between bg-white p-4 rounded-lg shadow">
                        <div>
                            <h2 className="font-bold text-lg">{book.book_title}</h2>
                            <p className="text-sm text-gray-600">Số lượng đang mượn: {book.borrowed_count}</p>
                        </div>
                        <button onClick={() => setSelectedBook(book)}
                                className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 transition-colors">
                            Trả sách
                        </button>
                    </div>
                ))}
            </div>
        );
    };

    return (
        <div className="container mx-auto p-6 md:p-10 bg-gray-50 min-h-screen">
            <Link to="/dashboard" className="text-green-700 hover:underline mb-8 inline-block">&larr; Quay lại Bảng điều khiển</Link>
            <h1 className="text-3xl font-bold mb-6 text-center">Sách đang mượn</h1>
            
            {successMessage && (
                <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-6 rounded-md shadow" role="alert">
                    {successMessage}
                </div>
            )}
            
            {renderContent()}

            {selectedBook && (
                <ReturnModal 
                    book={selectedBook} 
                    onClose={() => setSelectedBook(null)}
                    onSuccess={handleSuccess}
                />
            )}
        </div>
    );
};

export default ReturnBooksPage;

