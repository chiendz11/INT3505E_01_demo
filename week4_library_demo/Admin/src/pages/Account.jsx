import { useState } from "react";
import { updateAdminProfileAPI } from "../apis/accountAPI.js";
import { toast } from "react-toastify";

const Account = ({ token, admin }) => {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [avatar, setAvatar] = useState(admin?.avatar || "");
  const [preview, setPreview] = useState(admin?.avatar || "");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...(oldPassword && newPassword ? { oldPassword, newPassword } : {}),
        ...(avatar ? { avatar } : {}),
      };

      const result = await updateAdminProfileAPI(token, payload);
      toast.success(result.message);
    } catch (error) {
      toast.error(error.response?.data?.error || "Cập nhật thất bại");
    } finally {
      setLoading(false);
    }
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setAvatar(reader.result); // base64
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="max-w-md mx-auto mt-10 bg-white p-6 rounded-2xl shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">Cập nhật tài khoản</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="text-center">
          <img
            src={preview || "/default-avatar.png"}
            alt="avatar"
            className="w-24 h-24 mx-auto rounded-full object-cover border"
          />
          <input
            type="file"
            accept="image/*"
            onChange={handleAvatarChange}
            className="mt-2"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Mật khẩu cũ</label>
          <input
            type="password"
            className="w-full border p-2 rounded"
            value={oldPassword}
            onChange={(e) => setOldPassword(e.target.value)}
            placeholder="Nhập mật khẩu cũ"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Mật khẩu mới</label>
          <input
            type="password"
            className="w-full border p-2 rounded"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Nhập mật khẩu mới"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
          disabled={loading}
        >
          {loading ? "Đang cập nhật..." : "Cập nhật"}
        </button>
      </form>
    </div>
  );
};

export default Account;
