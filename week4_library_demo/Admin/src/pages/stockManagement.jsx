// src/pages/StockManagement.jsx
import React, { useEffect, useState } from "react";
import {
  importStock,
  getStockHistory,
  getInventoryList,
} from "../apis/inventoriesAPI.js";

const centers = [
  { id: "67ca6e3cfc964efa218ab7d8", name: "Nhà thi đấu quận Thanh Xuân" },
  { id: "67ca6e3cfc964efa218ab7d9", name: "Nhà thi đấu quận Cầu Giấy" },
  { id: "67ca6e3cfc964efa218ab7d7", name: "Nhà thi đấu quận Tây Hồ" },
  { id: "67ca6e3cfc964efa218ab7da", name: "Nhà thi đấu quận Bắc Từ Liêm" },
];

export default function StockManagement() {
  const [selectedCenter, setSelectedCenter] = useState(centers[0].id);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState("all");
  const [inventoryList, setInventoryList] = useState([]);
  const [importHistory, setImportHistory] = useState([]);
  const [form, setForm] = useState({
    inventoryId: "",
    centerId: centers[0].id,
    supplier: "",
    quantityImport: 0,
    importPrice: 0,
  });

  useEffect(() => {
    fetchInventory();
    fetchImportHistory();
  }, [selectedCenter, selectedYear, selectedMonth]);

  const fetchInventory = async () => {
    const res = await getInventoryList({ centerId: selectedCenter });
    setInventoryList(res.data?.data || []);
  };

  const fetchImportHistory = async () => {
    const res = await getStockHistory({
      centerId: selectedCenter,
      year: selectedYear,
      month: selectedMonth === "all" ? undefined : selectedMonth,
    });
    setImportHistory(res.data?.data || []);
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await importStock(form);
      alert("Nhập kho thành công!");
      setForm({
        inventoryId: "",
        centerId: selectedCenter,
        supplier: "",
        quantityImport: 0,
        importPrice: 0,
      });
      fetchInventory();
      fetchImportHistory();
    } catch (err) {
      console.error(err);
      alert("Lỗi khi nhập kho.");
    }
  };

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  return (
    <div className="p-6 space-y-8 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-center">Quản lý kho</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block font-medium mb-1">Chọn trung tâm:</label>
          <select
            className="border rounded px-3 py-2 w-full"
            value={selectedCenter}
            onChange={(e) => {
              setSelectedCenter(e.target.value);
              setForm({ ...form, centerId: e.target.value });
            }}
          >
            {centers.map((center) => (
              <option key={center.id} value={center.id}>
                {center.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block font-medium mb-1">Năm:</label>
          <select
            className="border rounded px-3 py-2 w-full"
            value={selectedYear}
            onChange={(e) => setSelectedYear(e.target.value)}
          >
            {years.map((year) => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block font-medium mb-1">Tháng:</label>
          <select
            className="border rounded px-3 py-2 w-full"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
          >
            <option value="all">Tất cả</option>
            {[...Array(12)].map((_, i) => (
              <option key={i + 1} value={i + 1}>{`Tháng ${i + 1}`}</option>
            ))}
          </select>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 border p-4 rounded shadow bg-white">
        <h2 className="text-xl font-semibold">Nhập kho</h2>

        <div>
          <label className="block mb-1">Mặt hàng</label>
          <select
            className="w-full border rounded px-3 py-2"
            name="inventoryId"
            value={form.inventoryId}
            onChange={handleChange}
            required
          >
            <option value="">-- Chọn --</option>
            {inventoryList.map((inv) => (
              <option key={inv._id} value={inv._id}>
                {inv.name} ({inv.unitSell}) - Tồn: {inv.quantity}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block mb-1">Nhà cung cấp</label>
          <input
            type="text"
            name="supplier"
            className="w-full border rounded px-3 py-2"
            value={form.supplier}
            onChange={handleChange}
            required
          />
        </div>

        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <label className="block mb-1">Số lượng nhập (đơn vị bán lẻ)</label>
            <input
              type="number"
              name="quantityImport"
              className="w-full border rounded px-3 py-2"
              value={form.quantityImport}
              onChange={handleChange}
              required
              min={1}
            />
          </div>
          <div className="flex-1">
            <label className="block mb-1">Giá nhập (1 thùng)</label>
            <input
              type="number"
              name="importPrice"
              className="w-full border rounded px-3 py-2"
              value={form.importPrice}
              onChange={handleChange}
              required
              min={0}
            />
          </div>
        </div>

        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Nhập hàng
        </button>
      </form>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-xl font-semibold mb-2">Kho hiện tại</h2>
        <div className="overflow-x-auto">
          <table className="w-full border text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border p-2">Tên hàng</th>
                <th className="border p-2">Danh mục</th>
                <th className="border p-2">Tồn kho</th>
                <th className="border p-2">Đơn vị bán</th>
                <th className="border p-2">Giá bán</th>
              </tr>
            </thead>
            <tbody>
              {inventoryList.map((inv) => (
                <tr key={inv._id}>
                  <td className="border p-2">{inv.name}</td>
                  <td className="border p-2">{inv.category}</td>
                  <td className="border p-2">{inv.quantity}</td>
                  <td className="border p-2">{inv.unitSell}</td>
                  <td className="border p-2">{inv.price.toLocaleString()} đ</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="text-xl font-semibold mb-2">Lịch sử nhập hàng</h2>
        <div className="overflow-x-auto">
          <table className="w-full border text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="border p-2">Mặt hàng</th>
                <th className="border p-2">Số lượng</th>
                <th className="border p-2">Giá nhập</th>
                <th className="border p-2">Nhà cung cấp</th>
                <th className="border p-2">Ngày nhập</th>
              </tr>
            </thead>
            <tbody>
              {importHistory.map((entry) => (
                <tr key={entry._id}>
                  <td className="border p-2">{entry.inventoryId.name || "N/A"}</td>
                  <td className="border p-2">{entry.quantityImport}</td>
                  <td className="border p-2">{entry.importPrice.toLocaleString()} đ</td>
                  <td className="border p-2">{entry.supplier}</td>
                  <td className="border p-2">{new Date(entry.createdAt).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}