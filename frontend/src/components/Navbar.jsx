import React, { useContext, useEffect, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "../context/AuthContext";
import api from "../api/axios";

const Navbar = () => {
  const { auth, logout, loading } = useContext(AuthContext);
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [ws, setWs] = useState(null);
  const notificationRef = useRef(null);

  // WebSocket connection for real-time notifications
  useEffect(() => {
    if (auth.user?.role === "CLIENT" && auth.user?.id) {
      const token = localStorage.getItem('accessToken');
      const wsUrl = `ws://localhost:801/ws/notifications/${auth.user.id}/${token}/`;
      const websocket = new WebSocket(wsUrl);

      websocket.onopen = () => {
        console.log('WebSocket connected');
      };

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Received notification:', data.message);
        
        // Add new notification to the list
        setNotifications(prev => [data.message, ...prev.slice(0, 9)]); // Keep only 10 most recent
        setUnreadCount(prev => prev + 1);
      };

      websocket.onclose = () => {
        console.log('WebSocket disconnected');
      };

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      setWs(websocket);

      return () => {
        websocket.close();
      };
    }
  }, [auth.user]);

  // Fetch initial notifications and unread count
  useEffect(() => {
    if (auth.user?.role === "CLIENT" && auth.user?.id) {
      const fetchNotifications = async () => {
        try {
          const [notifsRes, countRes] = await Promise.all([
            api.get(`/notifications/${auth.user.id}/`),
            api.get(`/notifications/${auth.user.id}/unread-count/`)
          ]);
          
          // Get the first page results
          setNotifications(notifsRes.data.results || []);
          setUnreadCount(countRes.data.unread_count || 0);
        } catch (err) {
          console.error("Error fetching notifications:", err);
          setNotifications([]);
          setUnreadCount(0);
        }
      };

      fetchNotifications();
    }
  }, [auth.user]);

  // Mark notifications as read when opening the dropdown
  const handleNotificationClick = async () => {
    setShowNotifications(!showNotifications);
    
    if (!showNotifications && unreadCount > 0) {
      // Mark all unread notifications as read
      try {
        const unreadNotifications = notifications.filter(n => !n.is_read);
        await Promise.all(
          unreadNotifications.map(notif => 
            api.patch(`/notifications/${notif.id}/read/`)
          )
        );
        setUnreadCount(0);
        // Update local state
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      } catch (err) {
        console.error("Error marking notifications as read:", err);
      }
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <>
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link to="/" className="text-gray-900 font-semibold text-lg hover:text-gray-600 transition-colors">
                Flight Booking
              </Link>
              {auth.user?.role === "CLIENT" && (
                <Link to="/history" className="text-gray-700 hover:text-gray-900 transition-colors">
                  My Bookings
                </Link>
              )}
              {auth.user?.role === "ADMIN" && (
                <>
                  <Link to="/admin" className="text-gray-700 hover:text-gray-900 transition-colors">
                    Dashboard
                  </Link>
                  <Link to="/admin/flights" className="text-gray-700 hover:text-gray-900 transition-colors">
                    Manage Flights
                  </Link>
                  <Link to="/admin/bookings" className="text-gray-700 hover:text-gray-900 transition-colors">
                    Manage Bookings
                  </Link>
                </>
              )}
            </div>

            <div className="flex items-center space-x-4">
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900"></div>
              ) : auth.user ? (
                <>
                  <span className="text-gray-700">Welcome, {auth.user.first_name}</span>
                  <button
                    onClick={() => navigate('/profile')}
                    className="text-gray-600 hover:text-gray-800 transition-colors p-2 rounded-full hover:bg-gray-100"
                    title="Edit Profile"
                  >
                    👤
                  </button>
                  {auth.user.role === "CLIENT" && (
                    <div className="relative" ref={notificationRef}>
                      <button
                        onClick={handleNotificationClick}
                        className="relative text-gray-600 hover:text-gray-800 transition-colors p-2 rounded-full hover:bg-gray-100"
                        title="Notifications"
                      >
                        🔔
                        {unreadCount > 0 && (
                          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center min-w-[20px]">
                            {unreadCount > 99 ? '99+' : unreadCount}
                          </span>
                        )}
                      </button>
                      
                      {showNotifications && (
                        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                          <div className="p-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
                          </div>
                          <div className="max-h-96 overflow-y-auto">
                            {notifications.length > 0 ? (
                              notifications.map((notif, index) => (
                                <div 
                                  key={notif.id || index} 
                                  className={`p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${
                                    !notif.is_read ? 'bg-blue-50' : ''
                                  }`}
                                >
                                  <p className="text-sm text-gray-800">{notif.message}</p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    {new Date(notif.timestamp).toLocaleString()}
                                  </p>
                                  {!notif.is_read && (
                                    <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-2"></span>
                                  )}
                                </div>
                              ))
                            ) : (
                              <div className="p-4 text-center text-gray-500">
                                No notifications
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                  <button
                    onClick={logout}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md transition-colors"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="text-gray-700 hover:text-gray-900 transition-colors">
                    Login
                  </Link>
                  <Link to="/register" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>
    </>
  );
};

export default Navbar;