import React, { useState, useEffect, useCallback } from 'react';
import { listBooks } from '../apis/bookAPI';
import { createTransaction } from '../apis/transactionAPI';
import { Link } from 'react-router-dom';

// --- Component Modal để xác nhận mượn sách ---
const BorrowModal = ({ book, onClose, onSuccess }) => {
    const [quantity, setQuantity] = useState(1);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleBorrow = async () => {
        const numQuantity = parseInt(quantity, 10);
        if (isNaN(numQuantity) || numQuantity <= 0) {
            setError("Số lượng phải là một số lớn hơn 0.");
            return;
        }
        if (numQuantity > book.available_copies) {
            setError("Số lượng mượn không được vượt quá số sách hiện có.");
            return;
        }
        
        setIsLoading(true);
        setError(null);
        try {
            await createTransaction({
                book_id: book.id,
                quantity: numQuantity,
                type: 'borrow'
            });
            onSuccess(`Mượn thành công ${numQuantity} cuốn "${book.title}"!`);
        } catch (err) {
            setError(err.message || "Mượn sách thất bại. Vui lòng thử lại.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 transition-opacity">
            <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl animate-fade-in-down">
                <h3 className="text-xl font-bold mb-4 text-gray-800">Xác nhận mượn sách</h3>
                <div className="space-y-2 mb-4">
                    <p><strong>Sách:</strong> {book.title}</p>
                    <p><strong>Tác giả:</strong> {book.author}</p>
                    <p><strong>Hiện có:</strong> {book.available_copies} cuốn</p>
                </div>
                <div className="mb-4">
                    <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">Số lượng cần mượn</label>
                    <input
                        type="number"
                        id="quantity"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                        min="1"
                        max={book.available_copies}
                        autoFocus
                    />
                </div>
                {error && <p className="text-red-600 text-sm mb-4 text-center">{error}</p>}
                <div className="flex justify-end space-x-4">
                    <button onClick={onClose} className="px-5 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors">Hủy</button>
                    <button onClick={handleBorrow} disabled={isLoading} className="px-5 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-wait">
                        {isLoading ? 'Đang xử lý...' : 'Xác nhận'}
                    </button>
                </div>
            </div>
        </div>
    );
};

// --- Component chính của trang ---
const BorrowBooksPage = () => {
  const [booksData, setBooksData] = useState(null);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedBook, setSelectedBook] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  const fetchBooks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listBooks(page, 9); // Lấy 9 sách mỗi trang cho layout 3 cột
      setBooksData(data);
    } catch (err) {
      setError("Không thể tải danh sách sách. Vui lòng thử lại sau.");
    } finally {
      setIsLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  const handleSuccess = (message) => {
    setSuccessMessage(message);
    setSelectedBook(null); // Đóng modal
    fetchBooks(); // Tải lại danh sách sách để cập nhật số lượng
    // Tự động ẩn thông báo thành công sau 5 giây
    setTimeout(() => setSuccessMessage(''), 5000);
  };

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center mt-20 text-xl">Đang tải danh sách sách...</div>;
    }
    if (error) {
      return <div className="text-center mt-20 text-xl text-red-500">{error}</div>;
    }
    if (!booksData || booksData.data.length === 0) {
      return <div className="text-center mt-20 text-xl text-gray-500">Không có sách nào để hiển thị.</div>;
    }
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {booksData.data.map((book) => (
          <div key={book.id} className="border p-5 rounded-xl shadow-lg flex flex-col justify-between bg-white hover:shadow-2xl transition-shadow duration-300">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 truncate">{book.title}</h2>
              <p className="text-gray-600 my-2">Tác giả: {book.author}</p>
              <p className="text-sm font-medium text-blue-600">Số lượng còn lại: {book.available_copies}</p>
            </div>
            <button
              onClick={() => setSelectedBook(book)}
              disabled={book.available_copies === 0}
              className="mt-4 w-full bg-green-600 text-white py-2 rounded-md font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {book.available_copies > 0 ? 'Mượn sách' : 'Đã hết sách'}
            </button>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="container mx-auto p-6 md:p-10 bg-gray-50 min-h-screen">
      <Link to="/dashboard" className="text-green-700 hover:underline mb-8 inline-block font-semibold">&larr; Quay lại Bảng điều khiển</Link>
      <h1 className="text-4xl font-extrabold mb-8 text-center text-gray-800">Thư viện sách</h1>
      
      {successMessage && (
        <div className="bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded-md shadow-md mb-6" role="alert">
            <p className="font-bold">Thành công!</p>
            <p>{successMessage}</p>
        </div>
      )}

      {renderContent()}

      {/* Phân trang */}
      {booksData && booksData.metadata.total_pages > 1 && (
        <div className="flex justify-center items-center mt-12 space-x-4">
          <button onClick={() => setPage(p => p - 1)} disabled={page === 1} className="px-5 py-2 font-semibold bg-white border-2 border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100">
            Trang trước
          </button>
          <span className="font-bold text-gray-700">
            Trang {booksData.metadata.page} / {booksData.metadata.total_pages}
          </span>
          <button onClick={() => setPage(p => p + 1)} disabled={page === booksData.metadata.total_pages} className="px-5 py-2 font-semibold bg-white border-2 border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100">
            Trang sau
          </button>
        </div>
      )}

      {selectedBook && (
        <BorrowModal 
          book={selectedBook} 
          onClose={() => setSelectedBook(null)}
          onSuccess={handleSuccess}
        />
      )}
    </div>
  );
};

export default BorrowBooksPage;

