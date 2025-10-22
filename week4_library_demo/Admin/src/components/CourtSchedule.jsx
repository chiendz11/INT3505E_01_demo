const CourtSchedule = ({ center }) => {
    return (
      <div className="mt-4">
        <h4 className="font-medium mb-2 flex items-center gap-2">
          <FiDollarSign className="text-green-500" />
          Bảng giá
        </h4>
        
        <div className="space-y-2">
          {center.pricing.map((price, index) => (
            <div key={index} className="flex justify-between text-sm">
              <span>{price.startTime} - {price.endTime}</span>
              <span>{price.price.toLocaleString()} VND</span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  export default CourtSchedule;