import React from "react";

const BillImage = ({ bill, onImageClick }) => {
  if (!bill || !bill.paymentImage) {
    return <div>Không có ảnh</div>;
  }

  // Kiểm tra xem paymentImage đã là data URL hay chỉ là chuỗi base64
  let dataUrl = bill.paymentImage;
  if (!dataUrl.startsWith("data:image/")) {
    // Giả sử là chuỗi base64, thêm tiền tố mặc định (image/jpeg)
    dataUrl = `data:image/jpeg;base64,${bill.paymentImage}`;
  }

  // Kiểm tra xem dataUrl có hợp lệ không (cơ bản)
  const isValidDataUrl = dataUrl.match(/^data:image\/(png|jpeg|gif);base64,[A-Za-z0-9+/=]+$/);
  if (!isValidDataUrl) {
    console.error("Invalid data URL:", dataUrl);
    return <div>Ảnh không hợp lệ</div>;
  }

  return (
    <div>
      <img
        src={dataUrl}
        alt="Payment confirmation"
        style={{
          maxWidth: "200px",
          height: "auto",
          cursor: "pointer",
          borderRadius: "8px",
          boxShadow: "0 2px 4px rgba(0, 0, 0, 0.1)",
        }}
        onClick={() => onImageClick(dataUrl)}
        onError={() => console.error("Lỗi khi tải ảnh:", dataUrl)} // Ghi log nếu ảnh không tải được
      />
    </div>
  );
};

export default BillImage;