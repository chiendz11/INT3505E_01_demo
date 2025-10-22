// src/pages/Users.jsx
import React, { useEffect, useState } from 'react';
import {
  getAllUsers,
  createUser,
  updateUser,
  deleteUser
} from '../apis/usersAPI.js';
import {
  FiEdit,
  FiTrash2,
  FiPlus,
  FiUser,
  FiPhone,
  FiMapPin,
  FiStar,
  FiX,
  FiMail,
  FiChevronDown,
  FiXCircle,
  FiSave
} from 'react-icons/fi';
import Modal from '../components/Modal';
import AdminLayout from '../components/AdminLayout.jsx';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [notification, setNotification] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone_number: '',
    address: '',
    role: 'member'
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const data = await getAllUsers();
      setUsers(data);
      setLoading(false);
    } catch (error) {
      showNotification('error', 'Lỗi khi tải danh sách người dùng');
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (selectedUser) {
        await updateUser(selectedUser._id, formData);
        showNotification('success', 'Cập nhật người dùng thành công');
      } else {
        await createUser(formData);
        showNotification('success', 'Thêm người dùng mới thành công');
      }
      fetchUsers();
      closeModal();
    } catch (error) {
      const message = error.response?.data?.message || 'Có lỗi xảy ra';
      showNotification('error', message);
    }
  };

  const openEditModal = (user) => {
    setSelectedUser(user);
    setFormData({
      name: user.name,
      email: user.email,
      phone_number: user.phone_number,
      address: user.address,
      role: user.role
    });
    setIsModalOpen(true);
  };

  const openCreateModal = () => {
    setSelectedUser(null);
    setFormData({
      name: '',
      email: '',
      phone_number: '',
      address: '',
      role: 'member'
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (userId) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa người dùng này?')) {
      try {
        await deleteUser(userId);
        showNotification('success', 'Xóa người dùng thành công');
        fetchUsers();
      } catch (error) {
        showNotification('error', 'Xóa người dùng thất bại');
      }
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedUser(null);
  };

  const showNotification = (type, message) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  if (loading) {
    return <div className="flex items-center justify-center py-8 text-xl">Đang tải...</div>;
  }

  return (
    <AdminLayout>
      <div className="container mx-auto p-4">
        <div className="flex flex-col md:flex-row md:justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-4 md:mb-0 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Quản lý Người dùng
          </h1>
          <button
            onClick={openCreateModal}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg hover:bg-blue-700 transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
          >
            <FiPlus size={20} />
            <span>Thêm mới</span>
          </button>
        </div>

        {notification && (
          <div className={`mb-6 p-4 rounded ${notification.type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
            {notification.message}
          </div>
        )}

        <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-lg">
          <table className="min-w-full bg-white divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-blue-50 to-purple-50">
              <tr>
                {['Tên', 'Email', 'Số điện thoại', 'Địa chỉ', 'Vai trò', 'Hành động'].map((header) => (
                  <th 
                    key={header}
                    className="px-6 py-4 text-left text-sm font-semibold text-gray-700 uppercase tracking-wider"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map(user => (
                <tr 
                  key={user._id} 
                  className="hover:bg-gray-50 transition-colors duration-200 group"
                >
                  <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 flex items-center justify-center bg-blue-100 rounded-full">
                        <FiUser className="text-blue-600" />
                      </div>
                      {user.name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">{user.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                    <div className="flex items-center gap-2">
                      <FiPhone className="text-gray-400" />
                      {user.phone_number}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                    <div className="flex items-center gap-2">
                      <FiMapPin className="text-gray-400" />
                      {user.address}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      user.role === 'member'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}>
                      {user.role === 'member' ? (
                        <>
                          <FiStar className="mr-1.5" />
                          Thành viên
                        </>
                      ) : (
                        <>
                          <FiUser className="mr-1.5" />
                          Khách
                        </>
                      )}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap flex items-center gap-3">
                    <button
                      onClick={() => openEditModal(user)}
                      className="p-2 rounded-lg hover:bg-blue-50 text-blue-600 hover:text-blue-700 transition-colors tooltip"
                      data-tip="Chỉnh sửa"
                    >
                      <FiEdit size={20} />
                    </button>
                    <button
                      onClick={() => handleDelete(user._id)}
                      className="p-2 rounded-lg hover:bg-red-50 text-red-600 hover:text-red-700 transition-colors tooltip"
                      data-tip="Xóa"
                    >
                      <FiTrash2 size={20} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <Modal isOpen={isModalOpen} onClose={closeModal}>
          <div className="p-6 bg-white rounded-xl">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">
                {selectedUser ? '🖊️ Cập nhật' : '✨ Thêm mới'} Người dùng
              </h2>
              <button
                onClick={closeModal}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <FiX size={24} className="text-gray-500" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-5">
              {['name', 'email', 'phone_number', 'address'].map((field) => (
                <div key={field}>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {{
                      name: 'Tên',
                      email: 'Email',
                      phone_number: 'Số điện thoại',
                      address: 'Địa chỉ'
                    }[field]}
                  </label>
                  <div className="relative">
                    <input
                      name={field}
                      value={formData[field]}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      required
                      pattern={field === 'phone_number' ? '\\d{10,15}' : undefined}
                    />
                    <div className="absolute inset-y-0 right-3 flex items-center">
                      {{
                        name: <FiUser className="text-gray-400" />,
                        email: <FiMail className="text-gray-400" />,
                        phone_number: <FiPhone className="text-gray-400" />,
                        address: <FiMapPin className="text-gray-400" />
                      }[field]}
                    </div>
                  </div>
                </div>
              ))}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Vai trò
                </label>
                <div className="relative">
                  <select
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg appearance-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  >
                    <option value="member">Thành viên</option>
                    <option value="guest">Khách</option>
                  </select>
                  <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
                    <FiChevronDown className="text-gray-400" />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-6">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-6 py-2.5 border rounded-lg hover:bg-gray-50 text-gray-600 transition-colors flex items-center gap-2"
                >
                  <FiXCircle size={18} />
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-lg hover:shadow-blue-200"
                >
                  {selectedUser ? <FiSave size={18} /> : <FiPlus size={18} />}
                  {selectedUser ? 'Cập nhật' : 'Thêm mới'}
                </button>
              </div>
            </form>
          </div>
        </Modal>
      </div>
    </AdminLayout>
  );
};

export default Users;
