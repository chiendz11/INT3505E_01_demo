import React, { useState, useEffect } from "react";
import {
  ArrowLeftIcon,
  MagnifyingGlassIcon,
  TrashIcon,
} from "@heroicons/react/24/outline";
import { getAllUsers, deleteUser } from "../apis/userManage";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {
  faDumbbell,
  faCoins,
  faMedal,
  faTrophy,
  faGem,
  faCrown,
  faSort,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useNavigate } from "react-router-dom"; // Import useNavigate

function UserManage() {
  const [searchValue, setSearchValue] = useState("");
  const [customers, setCustomers] = useState([]);
  const [rankFilter, setRankFilter] = useState("");
  const [sortName, setSortName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const navigate = useNavigate(); // Khởi tạo useNavigate

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const response = await getAllUsers();
        if (response.success) {
          setCustomers(response.data);
        } else {
          setError(response.message);
          toast.error(response.message);
        }
      } catch (err) {
        const message = err.message || "Lỗi khi lấy danh sách người dùng";
        setError(message);
        toast.error(message);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Bạn có chắc muốn xóa người dùng này?")) return;
    try {
      const response = await deleteUser(id);
      if (response.success) {
        setCustomers(customers.filter((customer) => customer._id !== id));
        toast.success("Xóa người dùng thành công");
      } else {
        toast.error(response.message);
      }
    } catch (error) {
      toast.error(error.message || "Lỗi khi xóa người dùng");
    }
  };

  let filteredCustomers = customers.filter((customer, index) => {
    const searchLower = searchValue.toLowerCase();
    const searchNumber = Number(searchValue);

    return (
      (index + 1).toString().includes(searchLower) ||
      customer.name.toLowerCase().includes(searchLower) ||
      customer.level.toLowerCase().includes(searchLower) ||
      (customer.phone_number || "").toLowerCase().includes(searchLower) ||
      customer.email.toLowerCase().includes(searchLower) ||
      (Number.isFinite(searchNumber) && customer.points === searchNumber) ||
      customer.points.toString().includes(searchLower)
    );
  });

  if (rankFilter && rankFilter !== "Tất cả") {
    filteredCustomers = filteredCustomers.filter((cust) => cust.level === rankFilter);
  }

  if (sortName && sortName !== "none") {
    filteredCustomers = [...filteredCustomers].sort((a, b) => {
      if (sortName === "asc") {
        return a.name.localeCompare(b.name);
      } else if (sortName === "desc") {
        return b.name.localeCompare(a.name); // Sửa lại để sắp xếp giảm dần
      }
      return 0;
    });
  }

  const handleRankFilter = (e) => {
    setRankFilter(e.target.value);
  };

  const handleSort = (e) => {
    setSortName(e.target.value);
  };

  const handleBack = () => {
    navigate("/dashboard"); // Điều hướng về /dashboard
  };

  // Hàm lấy biểu tượng phù hợp cho mỗi cấp bậc
  const getLevelIcon = (level) => {
    switch (level) {
      case "Sắt":
        return <FontAwesomeIcon icon={faDumbbell} className="ml-1" />;
      case "Đồng":
        return <FontAwesomeIcon icon={faCoins} className="ml-1" />;
      case "Bạc":
        return <FontAwesomeIcon icon={faMedal} className="ml-1" />;
      case "Vàng":
        return <FontAwesomeIcon icon={faTrophy} className="ml-1" />;
      case "Bạch kim":
        return <FontAwesomeIcon icon={faGem} className="ml-1" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-gray-100 min-h-screen w-full">
      <div className="bg-white w-full shadow-md overflow-hidden">
        <div className="bg-green-700 text-white flex items-center p-3">
          <button onClick={handleBack} className="mr-2">
            <ArrowLeftIcon className="h-6 w-6" />
          </button>
          <h1 className="text-lg font-semibold flex-1 text-center">
            Danh sách khách hàng
          </h1>
        </div>

        <div className="flex items-center p-3 bg-white border-b space-x-2">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-2 top-2.5" />
            <input
              type="text"
              className="pl-9 pr-3 py-2 w-full border rounded-md text-sm focus:outline-none focus:border-green-500"
              placeholder="Tìm kiếm khách hàng..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
            />
          </div>
          <div className="relative">
            <FontAwesomeIcon
              icon={faCrown}
              className="text-gray-400 absolute left-2 top-2.5 text-sm"
            />
            <select
              value={rankFilter}
              onChange={handleRankFilter}
              className="pl-8 pr-3 py-1 border rounded-md text-sm focus:outline-none focus:border-green-500 cursor-pointer"
            >
              <option value="" disabled hidden>
                Chọn cấp bậc
              </option>
              <option value="Tất cả">Tất cả</option>
              <option value="Sắt">Sắt</option>
              <option value="Đồng">Đồng</option>
              <option value="Bạc">Bạc</option>
              <option value="Vàng">Vàng</option>
              <option value="Bạch kim">Bạch kim</option>
            </select>
          </div>
          <div className="relative">
            <FontAwesomeIcon
              icon={faSort}
              className="text-gray-400 absolute left-2 top-2.5 text-sm"
            />
            <select
              value={sortName}
              onChange={handleSort}
              className="pl-8 pr-3 py-1 border rounded-md text-sm focus:outline-none focus:border-green-500 cursor-pointer"
            >
              <option value="" disabled hidden>
                Sắp xếp theo tên
              </option>
              <option value="none">Mặc định</option>
              <option value="asc">A → Z</option>
              <option value="desc">Z → A</option>
            </select>
          </div>
        </div>

        <div className="flex justify-around bg-white px-3 py-2 border-b text-sm text-green-700 font-semibold">
          <div className="flex flex-col items-center">
            <div className="flex items-center">
              <span className="inline-flex items-center bg-green-100 text-green-700 px-2 py-1 rounded-md text-xs">
                Sắt {getLevelIcon("Sắt")}
              </span>
            </div>
            <div>{customers.filter((c) => c.level === "Sắt").length}</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="flex items-center">
              <span className="inline-flex items-center bg-green-100 text-green-700 px-2 py-1 rounded-md text-xs">
                Đồng {getLevelIcon("Đồng")}
              </span>
            </div>
            <div>{customers.filter((c) => c.level === "Đồng").length}</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="flex items-center">
              <span className="inline-flex items-center bg-green-100 text-green-700 px-2 py-1 rounded-md text-xs">
                Bạc {getLevelIcon("Bạc")}
              </span>
            </div>
            <div>{customers.filter((c) => c.level === "Bạc").length}</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="flex items-center">
              <span className="inline-flex items-center bg-green-100 text-green-700 px-2 py-1 rounded-md text-xs">
                Vàng {getLevelIcon("Vàng")}
              </span>
            </div>
            <div>{customers.filter((c) => c.level === "Vàng").length}</div>
          </div>
          <div className="flex flex-col items-center">
            <div className="flex items-center">
              <span className="inline-flex items-center bg-green-100 text-green-700 px-2 py-1 rounded-md text-xs">
                Bạch kim {getLevelIcon("Bạch kim")}
              </span>
            </div>
            <div>{customers.filter((c) => c.level === "Bạch kim").length}</div>
          </div>
        </div>

        <div className="bg-white">
          {loading ? (
            <div className="text-center py-4">Đang tải...</div>
          ) : error ? (
            <div className="text-center py-4 text-red-500">Lỗi: {error}</div>
          ) : (
            <table className="w-full table-auto text-sm">
              <thead className="border-b">
                <tr className="text-left text-gray-700">
                  <th className="py-2 px-3 w-16">STT</th>
                  <th className="py-2 px-3 w-32">Tên</th>
                  <th className="py-2 px-3 w-24">Xếp hạng</th>
                  <th className="py-2 px-3 w-28">Số điện thoại</th>
                  <th className="py-2 px-3 w-40">Email</th>
                  <th className="py-2 px-3 w-16">Điểm</th>
                  <th className="py-2 px-3 text-right w-16">Xóa</th>
                </tr>
              </thead>
              <tbody>
                {filteredCustomers.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="text-center py-3 text-gray-500 italic">
                      Không tìm thấy khách hàng
                    </td>
                  </tr>
                ) : (
                  filteredCustomers.map((item, index) => (
                    <tr key={item._id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="py-2 px-3">{index + 1}</td>
                      <td className="py-2 px-3">{item.name}</td>
                      <td className="py-2 px-3">
                        <span className="inline-flex items-center bg-green-100 text-green-700 px-2 py-1 rounded-md text-xs">
                          {item.level} {getLevelIcon(item.level)}
                        </span>
                      </td>
                      <td className="py-2 px-3">{item.phone_number}</td>
                      <td className="py-2 px-3">{item.email}</td>
                      <td className="py-2 px-3">{item.points}</td>
                      <td className="py-2 px-3 text-right">
                        <button onClick={() => handleDelete(item._id)}>
                          <TrashIcon className="h-5 w-5 text-red-500 hover:text-red-600" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

export default UserManage;