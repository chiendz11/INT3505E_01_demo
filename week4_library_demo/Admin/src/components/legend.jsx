import React from "react";

const Legend = () => (
  <div className="flex gap-4 text-sm">
    <div className="flex items-center">
      <div className="w-4 h-4 bg-white mr-1"></div>
      <span>Trống</span>
    </div>
    <div className="flex items-center">
      <div className="w-4 h-4 bg-red-500 mr-1"></div>
      <span>Đã đặt</span>
    </div>
    <div className="flex items-center">
      <div className="w-4 h-4 bg-yellow-500 mr-1"></div>
      <span>Pending</span>
    </div>
    <div className="flex items-center">
      <div className="w-4 h-4 bg-[#0288D1] mr-1"></div>
      <span>Chờ xử lý</span>
    </div>
    <div className="flex items-center">
      <div className="w-4 h-4 bg-gray-300 mr-1"></div>
      <span>Locked</span>
    </div>
  </div>
);

export default Legend;