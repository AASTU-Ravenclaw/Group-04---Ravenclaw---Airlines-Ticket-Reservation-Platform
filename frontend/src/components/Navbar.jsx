import React, { useContext, useEffect, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "../context/AuthContext";
import api from "../api/axios";
import { User, LogOut, Settings, Bell, ChevronDown, Check } from "lucide-react";

const Navbar = () => {
  const { auth, logout, loading } = useContext(AuthContext);
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  
  const [ws, setWs] = useState(null);
  const notificationRef = useRef(null);
  const profileRef = useRef(null);

  // WebSocket connection for real-time notifications
  useEffect(() => {
    if (auth.user?.role === "CLIENT" && auth.user?.id) {
      const token = localStorage.getItem('accessToken');
      const wsHost = window.location.host;
      const wsUrl = `ws://${wsHost}/ws/notifications/${auth.user.id}/${token}/`;
      
      let websocket;
      try {
          websocket = new WebSocket(wsUrl);

          websocket.onopen = () => {
            console.log('WebSocket connected');
          };

          websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received notification:', data.message);
            setNotifications(prev => {
                // data.message is the full notification object from backend (including id, message text, etc)
                const newNotif = { 
                    ...data.message, 
                    is_read: false 
                };
                return [newNotif, ...prev.slice(0, 9)];
            }); 
            setUnreadCount(prev => prev + 1);
          };

          websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
          };

          setWs(websocket);
      } catch (e) {
          console.error("WebSocket connection failed", e);
      }

      return () => {
        if (websocket) websocket.close();
      };
    }
  }, [auth.user]);

  // Fetch initial notifications
  useEffect(() => {
    if (auth.user?.role === "CLIENT" && auth.user?.id) {
      const fetchNotifications = async () => {
        try {
          const [notifsRes, countRes] = await Promise.all([
            api.get(`/notifications/${auth.user.id}/`),
            api.get(`/notifications/${auth.user.id}/unread-count/`)
          ]);
          setNotifications(notifsRes.data.results || []);
          setUnreadCount(countRes.data.unread_count || 0);
        } catch (err) {
          console.error("Error fetching notifications:", err);
        }
      };
      fetchNotifications();
    }
  }, [auth.user]);

  const handleNotificationClick = async () => {
    setShowNotifications(!showNotifications);
    setShowProfileMenu(false); // Close other menu
    
    if (!showNotifications && unreadCount > 0) {
      try {
        const unreadNotifications = notifications.filter(n => !n.is_read);
        if (unreadNotifications.length > 0) {
            await Promise.all(
            unreadNotifications.map(notif => 
                api.patch(`/notifications/${notif.id}/read/`)
            )
            );
            setUnreadCount(0);
            setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        }
      } catch (err) {
        console.error("Error marking notifications as read:", err);
      }
    }
  };

  const toggleProfileMenu = () => {
    setShowProfileMenu(!showProfileMenu);
    setShowNotifications(false);
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setShowProfileMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleLogoutClick = () => {
    setShowProfileMenu(false);
    setShowLogoutConfirm(true);
  };

  const confirmLogout = () => {
    logout();
    setShowLogoutConfirm(false);
  };

  return (
    <>
      <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            
            {/* Logo & Main Nav */}
            <div className="flex items-center">
                <Link to="/" className="flex items-center gap-2 text-blue-600 font-bold text-xl hover:text-blue-700 transition-colors">
                    {/* Simple Plane Icon SVG */}
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h20"/><path d="M13 2a9 9 0 0 1 9 9v11"/><path d="M13 2v9"/><path d="M13 2H4"/></svg>
                    FlightBooking
                </Link>

                <div className="hidden md:flex items-center space-x-6 ml-10">
                    {auth.user?.role === "CLIENT" && (
                        <Link to="/history" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                        My Bookings
                        </Link>
                    )}
                    {auth.user?.role === "ADMIN" && (
                        <>
                        <Link to="/admin" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                            Dashboard
                        </Link>
                        <Link to="/admin/flights" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                            Flights
                        </Link>
                        <Link to="/admin/bookings" className="text-gray-600 hover:text-gray-900 font-medium transition-colors">
                            Bookings
                        </Link>
                        </>
                    )}
                </div>
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-3">
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
              ) : auth.user ? (
                <>
                  <span className="hidden md:block text-gray-700 text-sm font-medium mr-2">
                      Hi, {auth.user.first_name}
                  </span>

                  {/* Notifications */}
                  {auth.user.role === "CLIENT" && (
                    <div className="relative" ref={notificationRef}>
                      <button
                        onClick={handleNotificationClick}
                        className="relative text-gray-500 hover:text-gray-700 p-2 rounded-full hover:bg-gray-100 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        title="Notifications"
                      >
                        <Bell className="w-5 h-5" />
                        {unreadCount > 0 && (
                          <span className="absolute top-1 right-1 bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[16px] flex items-center justify-center">
                            {unreadCount > 99 ? '99+' : unreadCount}
                          </span>
                        )}
                      </button>
                      
                      {showNotifications && (
                        <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-100 ring-1 ring-black ring-opacity-5 overflow-hidden z-50 animate-fade-in-down">
                          <div className="p-3 border-b border-gray-100 bg-gray-50">
                            <h3 className="text-sm font-semibold text-gray-900">Notifications</h3>
                          </div>
                          <div className="max-h-96 overflow-y-auto">
                            {notifications.length > 0 ? (
                              notifications.map((notif, index) => (
                                <div 
                                  key={notif.id || index} 
                                  className={`p-3 border-b border-gray-50 hover:bg-gray-50 transition-colors ${
                                    !notif.is_read ? 'bg-blue-50/50' : ''
                                  }`}
                                >
                                  <p className="text-sm text-gray-800 leading-snug">{notif.message}</p>
                                  <p className="text-xs text-gray-400 mt-1">
                                    {notif.timestamp ? new Date(notif.timestamp).toLocaleString() : 'Just now'}
                                  </p>
                                </div>
                              ))
                            ) : (
                              <div className="p-8 text-center text-gray-400 text-sm">
                                <Bell className="w-8 h-8 mx-auto mb-2 opacity-20" />
                                No new notifications
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Profile Dropdown */}
                  <div className="relative" ref={profileRef}>
                    <button
                        onClick={toggleProfileMenu}
                        className="flex items-center gap-2 text-gray-700 hover:text-gray-900 px-2 py-1.5 rounded-lg hover:bg-gray-100 transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                        <div className="bg-blue-100 text-blue-600 rounded-full p-1.5">
                            <User className="w-5 h-5" />
                        </div>
                        <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${showProfileMenu ? 'rotate-180' : ''}`} />
                    </button>

                    {showProfileMenu && (
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-xl border border-gray-100 ring-1 ring-black ring-opacity-5 overflow-hidden z-50 animate-fade-in-down">
                            <div className="px-4 py-3 border-b border-gray-50 bg-gray-50/50">
                                <p className="text-sm font-medium text-gray-900 truncate">{auth.user.email}</p>
                                <p className="text-xs text-gray-500 capitalize">{auth.user.role.toLowerCase()}</p>
                            </div>
                            <div className="py-1">
                                <button
                                    onClick={() => {
                                        navigate('/profile');
                                        setShowProfileMenu(false);
                                    }}
                                    className="flex w-full items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-blue-600"
                                >
                                    <Settings className="w-4 h-4 mr-3" />
                                    Profile Settings
                                </button>
                                <button
                                    onClick={handleLogoutClick}
                                    className="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                >
                                    <LogOut className="w-4 h-4 mr-3" />
                                    Sign out
                                </button>
                            </div>
                        </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="flex items-center gap-2">
                  <Link to="/login" className="text-gray-600 hover:text-gray-900 font-medium px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors">
                    Login
                  </Link>
                  <Link to="/register" className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg shadow-sm hover:shadow-md transition-all">
                    Register
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
            <div className="bg-white rounded-xl shadow-2xl max-w-sm w-full overflow-hidden transform transition-all animate-scale-in">
                <div className="p-6 text-center">
                    <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
                        <LogOut className="h-6 w-6 text-red-600" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Sign out?</h3>
                    <p className="text-sm text-gray-500">Are you sure you want to sign out of your account?</p>
                </div>
                <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-2">
                    <button
                        type="button"
                        onClick={confirmLogout}
                        className="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:w-auto sm:text-sm transition-colors"
                    >
                        Sign out
                    </button>
                    <button
                        type="button"
                        onClick={() => setShowLogoutConfirm(false)}
                        className="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:w-auto sm:text-sm transition-colors"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
