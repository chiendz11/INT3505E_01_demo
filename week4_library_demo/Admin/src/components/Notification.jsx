// src/components/Notification.jsx
const Notification = ({ type, message }) => {
    const colors = {
      success: 'bg-green-100 border-green-400 text-green-700',
      error: 'bg-red-100 border-red-400 text-red-700',
      info: 'bg-blue-100 border-blue-400 text-blue-700'
    };
  
    return (
      <div className={`fixed top-4 right-4 p-4 rounded border ${colors[type]} animate-slide-in`}>
        {message}
      </div>
    );
  };
  
  export default Notification;