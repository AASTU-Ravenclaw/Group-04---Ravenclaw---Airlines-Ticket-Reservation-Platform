import React from 'react';

const Notifications = ({ notifications, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Notifications</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {notifications.length > 0 ? (
            notifications.map((notif, index) => (
              <div key={index} className="border-b pb-2">
                <p className="text-sm text-gray-800">{notif.message}</p>
                <p className="text-xs text-gray-500">{new Date(notif.created_at).toLocaleString()}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-500">No notifications</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Notifications;