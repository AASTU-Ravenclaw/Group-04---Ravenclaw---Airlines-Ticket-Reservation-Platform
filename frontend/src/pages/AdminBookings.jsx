import React, { useEffect, useState, useContext } from "react";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";
import toast from "react-hot-toast";
import { Plane, Calendar, User, Search, RefreshCw, X, Check, AlertCircle, Clock, MapPin, Ticket } from "lucide-react";

const AdminBookings = () => {
  const { auth } = useContext(AuthContext);
  
  // State
  const [flights, setFlights] = useState([]);
  const [selectedFlight, setSelectedFlight] = useState(null);
  
  const [bookings, setBookings] = useState([]);
  const [selectedBooking, setSelectedBooking] = useState(null); // For Modal
  const [isLoadingFlights, setIsLoadingFlights] = useState(false);
  const [isLoadingBookings, setIsLoadingBookings] = useState(false);

  // Fetch all flights on mount
  const fetchFlights = async () => {
    setIsLoadingFlights(true);
    try {
      const res = await api.get('/flights/');
      setFlights(res.data);
    } catch (err) {
      console.error("Error fetching flights:", err);
      toast.error("Failed to load flights");
    } finally {
      setIsLoadingFlights(false);
    }
  };

  const fetchBookingsForFlight = async (flightId) => {
    setIsLoadingBookings(true);
    try {
      setBookings([]); // Clear while loading
      const res = await api.get(`/bookings/?flight_id=${flightId}`);
      setBookings(res.data);
    } catch (err) {
      console.error("Error fetching bookings:", err);
      setBookings([]);
      toast.error("Failed to load bookings");
    } finally {
      setIsLoadingBookings(false);
    }
  };

  useEffect(() => {
    if(auth.user && auth.user.role === 'ADMIN') fetchFlights();
  }, [auth.user]);

  const handleFlightClick = (flight) => {
    if (selectedFlight?.flight_id === flight.flight_id) return;
    setSelectedFlight(flight);
    fetchBookingsForFlight(flight.flight_id);
  };
  
  const handleBookingClick = (booking) => {
    setSelectedBooking(booking);
  };

  const cancelBooking = async (id) => {
    if(!window.confirm("Are you sure you want to cancel this booking? This action cannot be undone.")) return;
    
    const toastId = toast.loading("Cancelling booking...");
    try {
      await api.delete(`/bookings/${id}/`);
      
      toast.success("Booking cancelled successfully", { id: toastId });
      setSelectedBooking(null); // Close modal
      // Refresh current flight bookings
      if (selectedFlight) {
        fetchBookingsForFlight(selectedFlight.flight_id);
      }
    } catch (err) {
      toast.error("Error cancelling booking. Please try again.", { id: toastId });
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
        case 'CONFIRMED': return 'bg-green-100 text-green-800 border-green-200';
        case 'CANCELLED': return 'bg-red-100 text-red-800 border-red-200';
        default: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-8 text-left">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
        <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Booking Management</h1>
            <p className="text-gray-500">Select a flight to view and manage passenger reservations.</p>
        </div>
        <button 
            onClick={fetchFlights}
            className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
        >
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh Data
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-[calc(100vh-220px)] min-h-[600px]">
        
        {/* Column 1: Flights List */}
        <div className="lg:col-span-5 flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900 flex items-center">
                <Plane className="w-5 h-5 mr-2 text-blue-600" />
                Flights Directory
            </h2>
            <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">{flights.length}</span>
          </div>
          
          <div className="overflow-y-auto flex-1 p-3 space-y-3 custom-scrollbar">
            {isLoadingFlights ? (
                <div className="flex justify-center items-center h-32">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
            ) : flights.length === 0 ? (
                <div className="text-center py-10 text-gray-400">
                    <p>No flights available</p>
                </div>
            ) : (flights.map(f => (
              <div
                key={f.flight_id}
                onClick={() => handleFlightClick(f)}
                className={`group cursor-pointer p-4 rounded-xl border transition-all duration-200 hover:shadow-md ${
                  selectedFlight?.flight_id === f.flight_id
                    ? 'border-blue-500 bg-blue-50/50 shadow-sm ring-1 ring-blue-500'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="font-bold text-gray-900 font-mono tracking-tight">{f.flight_number}</span>
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                    f.status === 'scheduled' ? 'bg-green-100 text-green-700' :
                    f.status === 'cancelled' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {f.status}
                  </span>
                </div>
                
                <div className="flex items-center text-sm text-gray-600 mb-2">
                    <div className="flex-1 truncate">
                        <span className="font-medium text-gray-900">{f.departure_location.city}</span>
                        <span className="text-xs text-gray-400 mx-1">({f.departure_location.airport_code})</span>
                    </div>
                    <span className="text-gray-400 mx-2">→</span>
                    <div className="flex-1 truncate text-right">
                        <span className="font-medium text-gray-900">{f.arrival_location.city}</span>
                        <span className="text-xs text-gray-400 mx-1">({f.arrival_location.airport_code})</span>
                    </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500 border-t border-gray-100 pt-3 mt-1">
                    <div className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        <span>{new Date(f.departure_time).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        <span>{new Date(f.departure_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    </div>
                </div>
              </div>
            )))}
          </div>
        </div>
        
        {/* Column 2: Bookings List (Expanded) */}
        <div className="lg:col-span-7 flex flex-col bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
             <div className="flex justify-between items-center mb-1">
                <h2 className="font-semibold text-gray-900 flex items-center">
                    <Ticket className="w-5 h-5 mr-2 text-indigo-600" />
                    Reservations
                </h2>
                {selectedFlight && (
                    <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-medium">
                        {bookings.length} Total
                    </span>
                )}
             </div>
             {selectedFlight ? (
                 <p className="text-xs text-gray-500 truncate flex items-center mt-1">
                    Via <span className="font-medium mx-1">{selectedFlight.flight_number}</span> 
                    to {selectedFlight.arrival_location.city}
                 </p>
             ) : (
                <p className="text-xs text-gray-400 italic mt-1">Select a flight to view bookings</p>
             )}
          </div>

          <div className="overflow-y-auto flex-1 p-4 bg-gray-50/30 custom-scrollbar">
            {!selectedFlight ? (
                <div className="h-full flex flex-col items-center justify-center text-gray-400">
                    <div className="bg-gray-100 p-4 rounded-full mb-3">
                        <Search className="w-8 h-8 text-gray-300" />
                    </div>
                    <p className="font-medium text-gray-500">No flight selected</p>
                    <p className="text-sm">Please choose a flight from the directory</p>
                </div>
            ) : isLoadingBookings ? (
                <div className="flex justify-center items-center h-48">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                </div>
            ) : bookings.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-gray-400">
                    <div className="bg-gray-100 p-4 rounded-full mb-3">
                        <User className="w-8 h-8 text-gray-300" />
                    </div>
                    <p className="font-medium text-gray-500">No bookings yet</p>
                    <p className="text-sm">This flight has no reservations.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {bookings.map(b => (
                    <div
                        key={b.booking_id}
                        onClick={() => handleBookingClick(b)}
                        className="group bg-white cursor-pointer p-4 rounded-xl border border-gray-200 hover:border-indigo-300 hover:shadow-md transition-all duration-200"
                    >
                        <div className="flex justify-between items-start mb-3">
                            <div className="bg-gray-50 px-2 py-1 rounded text-xs font-mono text-gray-600 border border-gray-100">
                                #{b.booking_id?.slice(-6) || 'N/A'}
                            </div>
                            <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase border ${getStatusColor(b.status)}`}>
                                {b.status}
                            </span>
                        </div>
                        
                        <div className="flex items-center mb-3">
                            <div className="bg-indigo-50 p-2 rounded-full mr-3 group-hover:bg-indigo-100 transition-colors">
                                <User className="w-4 h-4 text-indigo-600" />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-gray-900">
                                    {(b.passengers_details && b.passengers_details.length > 0) 
                                        ? `${b.passengers_details[0].first_name} ${b.passengers_details[0].last_name}` + (b.passengers_details.length > 1 ? ` +${b.passengers_details.length - 1}` : '')
                                        : `${b.passengers} Passenger(s)`
                                    }
                                </p>
                                <p className="text-xs text-gray-500">{new Date(b.booking_date).toLocaleDateString()}</p>
                            </div>
                        </div>

                        <div className="flex justify-end mt-2">
                             <span className="text-xs text-indigo-600 font-medium group-hover:translate-x-1 transition-transform inline-flex items-center">
                                View Details →
                             </span>
                        </div>
                    </div>
                    ))}
                </div>
            )}
          </div>
        </div>
      </div>

      {/* Booking Details Modal */}
      {selectedBooking && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-scale-in">
                
                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-gray-100">
                    <h3 className="text-xl font-bold text-gray-900 flex items-center">
                        <Ticket className="w-6 h-6 mr-3 text-indigo-600" />
                        Booking Details
                    </h3>
                    <button 
                        onClick={() => setSelectedBooking(null)}
                        className="text-gray-400 hover:text-gray-600 hover:bg-gray-100 p-2 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto max-h-[70vh]">
                    
                    {/* Status Banner */}
                    <div className={`flex items-center p-4 rounded-xl mb-6 border ${getStatusColor(selectedBooking.status)}`}>
                        {selectedBooking.status === 'CONFIRMED' ? <Check className="w-5 h-5 mr-3" /> : <AlertCircle className="w-5 h-5 mr-3" />}
                        <div>
                            <p className="font-bold text-sm">Booking Status: {selectedBooking.status}</p>
                            <p className="text-xs opacity-80">Ref ID: {selectedBooking.booking_id}</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                         {/* Flight Info */}
                         <div>
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Flight Information</h4>
                            {selectedFlight ? (
                                <div className="space-y-4">
                                     <div>
                                        <p className="text-sm font-semibold text-gray-900 flex items-center">
                                             <Plane className="w-4 h-4 mr-2 text-gray-400" />
                                             {selectedFlight.flight_number}
                                        </p>
                                        <p className="text-xs text-gray-500 pl-6">Flight Number</p>
                                     </div>
                                     <div className="flex items-start">
                                        <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 mr-2"></div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">{selectedFlight.departure_location.city} <span className="text-gray-400">({selectedFlight.departure_location.airport_code})</span></p>
                                            <p className="text-xs text-gray-500">{new Date(selectedFlight.departure_time).toLocaleString()}</p>
                                        </div>
                                     </div>
                                     <div className="flex items-start">
                                        <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 mt-1.5 mr-2"></div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">{selectedFlight.arrival_location.city} <span className="text-gray-400">({selectedFlight.arrival_location.airport_code})</span></p>
                                            <p className="text-xs text-gray-500">{new Date(selectedFlight.arrival_time).toLocaleString()}</p>
                                        </div>
                                     </div>
                                </div>
                            ) : (
                                <p className="text-sm text-red-500">Flight details not available</p>
                            )}
                         </div>

                         {/* Passenger List */}
                         <div>
                            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">Passenger List</h4>
                            <div className="space-y-3">
                                {selectedBooking.passengers_details && selectedBooking.passengers_details.length > 0 ? (
                                    selectedBooking.passengers_details.map((p, i) => (
                                        <div key={i} className="flex items-start p-3 bg-gray-50 rounded-lg border border-gray-100">
                                            <div className="bg-white p-2 rounded-full border border-gray-100 mr-3 shadow-sm">
                                                <User className="w-4 h-4 text-gray-600" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-gray-900">{p.first_name} {p.last_name}</p>
                                                <p className="text-xs text-gray-500">{p.email}</p>
                                                {p.passport_number && <p className="text-[10px] text-gray-400 mt-1 font-mono">Passport: {p.passport_number}</p>}
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <div className="p-4 bg-gray-50 rounded-lg text-center border border-dashed border-gray-200">
                                        <p className="text-sm text-gray-500 italic">No detailed passenger info</p>
                                        <p className="text-xs text-gray-400 mt-1">{selectedBooking.passengers} Seats Booked</p>
                                    </div>
                                )}
                            </div>
                         </div>
                    </div>
                </div>

                {/* Footer Actions */}
                <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-end gap-3">
                    <button 
                        onClick={() => setSelectedBooking(null)}
                        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium transition-colors"
                    >
                        Close
                    </button>
                    {selectedBooking.status !== 'CANCELLED' && (
                        <button 
                            onClick={() => cancelBooking(selectedBooking.booking_id)}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 shadow-sm hover:shadow font-medium transition-all"
                        >
                            Cancel Booking
                        </button>
                    )}
                </div>
            </div>
        </div>
      )}
    </div>
  );
};

export default AdminBookings;
