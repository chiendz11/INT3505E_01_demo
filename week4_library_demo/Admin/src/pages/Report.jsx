import React, { useEffect, useState } from "react";
import { getReportSummary, getMonthlyReport } from "@/apis/reportAPI.js";

const centers = [
  { id: "67ca6e3cfc964efa218ab7d8", name: "Nhà thi đấu quận Thanh Xuân" },
  { id: "67ca6e3cfc964efa218ab7d9", name: "Nhà thi đấu quận Cầu Giấy" },
  { id: "67ca6e3cfc964efa218ab7d7", name: "Nhà thi đấu quận Tây Hồ" },
  { id: "67ca6e3cfc964efa218ab7da", name: "Nhà thi đấu quận Bắc Từ Liêm" }
];

// Sinh danh sách năm từ 2022 đến năm hiện tại
const currentYear = new Date().getFullYear();
const years = Array.from({ length: currentYear - 2021 }, (_, i) => 2022 + i);

export default function Report() {
  const [selectedCenter, setSelectedCenter] = useState("");
  const [summary, setSummary] = useState(null);
  const [year, setYear] = useState(currentYear);
  const [monthlyData, setMonthlyData] = useState([]);

  // Lấy summary khi chọn trung tâm
  useEffect(() => {
    if (!selectedCenter) {
      setSummary(null);
      return;
    }
    (async () => {
      try {
        console.log("Fetching summary for centerId:", selectedCenter);
        const res = await getReportSummary({ centerId: selectedCenter });
        setSummary(res.data.data);
      } catch (err) {
        console.error(err);
      }
    })();
  }, [selectedCenter]);

  // Lấy báo cáo hàng tháng khi thay đổi center hoặc year
  useEffect(() => {
    if (!selectedCenter) {
      setMonthlyData([]);
      return;
    }
    (async () => {
      try {
        console.log("Fetching monthly data for", selectedCenter, "year", year);
        const res = await getMonthlyReport({ centerId: selectedCenter, year });
        setMonthlyData(res.data.data || []);
      } catch (err) {
        console.error(err);
        setMonthlyData([]);
      }
    })();
  }, [selectedCenter, year]);

  return (
    <div className="p-4">
      <h1 className="text-xl font-semibold mb-4">Báo cáo doanh thu & chi phí</h1>

      <div className="flex items-center space-x-4">
        {/* Chọn trung tâm */}
        <select
          className="border px-3 py-1 rounded"
          value={selectedCenter}
          onChange={(e) => setSelectedCenter(e.target.value)}
        >
          <option value="">-- Chọn trung tâm --</option>
          {centers.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>

        {/* Chọn năm */}
        {selectedCenter && (
          <select
            className="border px-3 py-1 rounded"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <div className="mt-4 bg-white shadow p-4 rounded-lg">
          <p>💵 Doanh thu: {summary.totalRevenue.toLocaleString()} VND</p>
          <p>📦 Chi phí nhập hàng: {summary.totalCost.toLocaleString()} VND</p>
          <p>📈 Lợi nhuận: {summary.profit.toLocaleString()} VND</p>
          <p>🧾 Số hóa đơn: {summary.totalInvoices}</p>
          <p>📥 Số lần nhập hàng: {summary.totalImports}</p>
        </div>
      )}

      {/* Báo cáo theo tháng */}
      {monthlyData.length > 0 && (
        <div className="mt-6 bg-white shadow p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">
            Báo cáo tháng trong năm {year}
          </h2>
          <table className="w-full table-auto text-left border-collapse">
            <thead>
              <tr>
                <th className="border px-2 py-1">Tháng</th>
                <th className="border px-2 py-1">Doanh thu</th>
                <th className="border px-2 py-1">Chi phí</th>
                <th className="border px-2 py-1">Lợi nhuận</th>
              </tr>
            </thead>
            <tbody>
              {monthlyData.map((item) => (
                <tr key={item.month}>
                  <td className="border px-2 py-1">{item.month}</td>
                  <td className="border px-2 py-1">
                    {item.totalRevenue.toLocaleString()}
                  </td>
                  <td className="border px-2 py-1">
                    {item.totalCost.toLocaleString()}
                  </td>
                  <td className="border px-2 py-1">
                    {(item.totalRevenue - item.totalCost).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Không có dữ liệu monthly */}
      {selectedCenter && monthlyData.length === 0 && (
        <p className="mt-4 text-gray-500">Không có dữ liệu cho năm {year}</p>
      )}
    </div>
  );
}
