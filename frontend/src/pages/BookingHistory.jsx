import React, { useEffect, useState, useContext } from "react";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";
import toast from "react-hot-toast";
import { 
    Clock, Calendar, Plane, User, X, Check, AlertCircle, Info, ChevronRight, Ticket 
} from "lucide-react";

const BookingHistory = () => {
  const { auth } = useContext(AuthContext);
  const [bookings, setBookings] = useState([]);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [flightDetails, setFlightDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchBookings = async () => {
    setIsLoading(true);
    try {
        const res = await api.get(`/bookings/`);
        setBookings(res.data);
    } catch (error) {
        console.error("Error fetching bookings", error);
        toast.error("Failed to load your bookings");
    } finally {
        setIsLoading(false);
    }
  };

  const fetchFlightDetails = async (flightId) => {
    try {
      setFlightDetails(null); // Clear previous
      const res = await api.get(`/flights/${flightId}/`);
      setFlightDetails(res.data);
    } catch (err) {
      console.error("Error fetching flight details:", err);
      toast.error("Could not load flight details");
    }
  };

  useEffect(() => {
    if(auth.user) fetchBookings();
  }, [auth.user]);

  const cancelBooking = async (id) => {
    if(!window.confirm("Are you sure you want to cancel this booking? This action cannot be undone.")) return;
    
    const toastId = toast.loading("Processing cancellation...");
    try {
      await api.delete(`/bookings/${id}/`);
      
      toast.success("Booking cancelled successfully", { id: toastId });
      setSelectedBooking(null);
      setFlightDetails(null);
      fetchBookings();
    } catch (err) {
      toast.error("Error cancelling booking", { id: toastId });
    }
  };

  const handleBookingClick = (b) => {
    setSelectedBooking(b);
    fetchFlightDetails(b.flight_id);
    // Smooth scroll to details on mobile
    if (window.innerWidth < 1024) {
        setTimeout(() => {
            document.getElementById('booking-details-panel')?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
        case 'CONFIRMED': return 'text-green-700 bg-green-50 border-green-200';
        case 'CANCELLED': return 'text-red-700 bg-red-50 border-red-200';
        default: return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    }
  };

  const getFlightStatusColor = (status) => {
      switch(status) {
          case 'scheduled': return 'text-green-600 bg-green-100';
          case 'delayed': return 'text-orange-600 bg-orange-100';
          case 'cancelled': return 'text-red-600 bg-red-100';
          case 'landed': return 'text-blue-600 bg-blue-100';
          default: return 'text-gray-600 bg-gray-100';
      }
  };

  return (
    <div className="max-w-7xl mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Journeys</h1>
        <p className="text-gray-500">Manage your past and upcoming flights</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Column: List */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
             <div className="p-4 bg-gray-50 border-b border-gray-200">
                <h2 className="font-semibold text-gray-900">Recent Bookings</h2>
             </div>
             
             <div className="max-h-[600px] overflow-y-auto p-4 space-y-3 custom-scrollbar">
                {isLoading ? (
                    <div className="flex justify-center p-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                ) : bookings.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        <Ticket className="w-12 h-12 mx-auto text-gray-300 mb-3" />
                        <p>No bookings found.</p>
                        <a href="/" className="text-blue-600 text-sm hover:underline mt-2 inline-block">Book a flight</a>
                    </div>
                ) : (bookings.map(b => (
                    <div
                        key={b.booking_id}
                        onClick={() => handleBookingClick(b)}
                        className={`cursor-pointer p-4 rounded-xl border transition-all duration-200 group relative ${
                        selectedBooking?.booking_id === b.booking_id
                            ? 'border-blue-500 bg-blue-50/50 shadow-md ring-1 ring-blue-500'
                            : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50 hover:shadow-sm'
                        }`}
                    >
                        <div className="flex justify-between items-start mb-2">
                            <div>
                                <span className="text-xs font-mono text-gray-500">#{b.booking_id.slice(-6).toUpperCase()}</span>
                                <p className="text-sm font-semibold text-gray-900 mt-1">
                                    {new Date(b.booking_date).toLocaleDateString()}
                                </p>
                            </div>
                            <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider border ${getStatusColor(b.status)}`}>
                                {b.status}
                            </span>
                        </div>
                        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
                             <div className="flex items-center">
                                 <User className="w-3 h-3 mr-1" />
                                 {b.passengers_details?.length || b.passengers}
                             </div>
                             <ChevronRight className={`w-4 h-4 transition-transform ${selectedBooking?.booking_id === b.booking_id ? 'text-blue-600 translate-x-1' : 'text-gray-300'}`} />
                        </div>
                    </div>
                )))}
             </div>
          </div>
        </div>
        
        {/* Right Column: Details */}
        <div className="lg:col-span-8" id="booking-details-panel">
          {selectedBooking ? (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden animate-fade-in-up">
              
              {/* Header */}
              <div className="p-6 md:p-8 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${getStatusColor(selectedBooking.status)}`}>
                                {selectedBooking.status}
                            </span>
                            <span className="text-gray-400 text-sm font-mono">#{selectedBooking.booking_id}</span>
                        </div>
                        <h2 className="text-2xl font-bold text-gray-900">Trip Details</h2>
                    </div>
                    {flightDetails && (
                        <div className={`px-4 py-2 rounded-lg ${getFlightStatusColor(flightDetails.status)} flex items-center`}>
                             <Info className="w-4 h-4 mr-2" />
                             <span className="font-bold text-sm uppercase">Flight {flightDetails.status}</span>
                        </div>
                    )}
                </div>
              </div>

              <div className="p-6 md:p-8">
                {/* Flight Route Visual */}
                {flightDetails ? (
                    <div className="bg-gray-50 rounded-2xl p-6 mb-8 border border-gray-100">
                         <div className="flex flex-col md:flex-row items-center justify-between gap-6 relative">
                             {/* Line connector for desktop */}
                             <div className="hidden md:block absolute top-[26px] left-[15%] right-[15%] h-0.5 bg-gray-300 z-0"></div>
                             {/* Plane icon for desktop */}
                             <div className="hidden md:flex absolute top-[14px] left-1/2 -translate-x-1/2 bg-gray-50 px-2 z-10 text-blue-500">
                                <Plane className="w-6 h-6 rotate-90" />
                             </div>

                             <div className="text-center md:text-left z-10 w-full md:w-auto">
                                 <p className="text-3xl font-bold text-gray-900">{flightDetails.departure_location.city}</p>
                                 <p className="text-lg font-mono text-blue-600 font-semibold">{flightDetails.departure_location.airport_code}</p>
                                 <div className="mt-2 flex items-center justify-center md:justify-start text-gray-500 text-sm">
                                     <Calendar className="w-4 h-4 mr-1" />
                                     {new Date(flightDetails.departure_time).toLocaleDateString()}
                                 </div>
                                 <div className="mt-1 flex items-center justify-center md:justify-start text-gray-500 text-sm">
                                     <Clock className="w-4 h-4 mr-1" />
                                     {new Date(flightDetails.departure_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                 </div>
                             </div>

                             {/* Mobile arrow */}
                             <div className="md:hidden transform rotate-90 text-gray-300">
                                 <Plane className="w-6 h-6" />
                             </div>

                             <div className="text-center md:text-right z-10 w-full md:w-auto">
                                 <p className="text-3xl font-bold text-gray-900">{flightDetails.arrival_location.city}</p>
                                 <p className="text-lg font-mono text-blue-600 font-semibold">{flightDetails.arrival_location.airport_code}</p>
                                 <div className="mt-2 flex items-center justify-center md:justify-end text-gray-500 text-sm">
                                     <Calendar className="w-4 h-4 mr-1" />
                                     {new Date(flightDetails.arrival_time).toLocaleDateString()}
                                 </div>
                                 <div className="mt-1 flex items-center justify-center md:justify-end text-gray-500 text-sm">
                                     <Clock className="w-4 h-4 mr-1" />
                                     {new Date(flightDetails.arrival_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                                 </div>
                             </div>
                         </div>
                         
                         <div className="mt-6 pt-6 border-t border-gray-200 flex justify-between items-center text-sm">
                             <div className="text-gray-500">
                                 <span className="font-semibold text-gray-700">Flight No:</span> {flightDetails.flight_number}
                             </div>
                             <div className="text-gray-500">
                                 <span className="font-semibold text-gray-700">Total Price:</span> <span className="text-green-600 font-bold text-base">${flightDetails.price}</span>
                             </div>
                         </div>
                    </div>
                ) : (
                    <div className="h-32 flex items-center justify-center text-gray-400">
                        Loading flight information...
                    </div>
                )}
                
                {/* Passengers */}
                <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <User className="w-5 h-5 mr-2 text-blue-600" />
                        Passenger Information
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {selectedBooking.passengers_details && selectedBooking.passengers_details.length > 0 ? (
                            selectedBooking.passengers_details.map((p, i) => (
                                <div key={i} className="flex items-start p-4 bg-white border border-gray-200 rounded-xl hover:border-blue-300 transition-colors shadow-sm">
                                    <div className="bg-blue-50 p-2 rounded-full mr-3 text-blue-600 text-sm font-bold w-8 h-8 flex items-center justify-center">
                                        {i + 1}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-bold text-gray-900 truncate">{p.first_name} {p.last_name}</p>
                                        <p className="text-sm text-gray-500 truncate">{p.email}</p>
                                        {p.passport_number && (
                                            <p className="text-xs text-gray-400 font-mono mt-1 pt-1 border-t border-gray-50">
                                                ID: {p.passport_number}
                                            </p>
                                        )}
                                    </div>
                                </div>
                            ))
                        ) : (
                            // Fallback if passenger details are missing (e.g. legacy data)
                             <div className="bg-orange-50 text-orange-800 p-4 rounded-xl border border-orange-100 col-span-2">
                                <p className="font-medium">Summary Only</p>
                                <p className="text-sm opacity-80">{selectedBooking.passengers} Passenger(s) confirmed.</p>
                             </div>
                        )}
                    </div>
                </div>

              </div>
              
              {/* Footer Actions */}
              {selectedBooking.status !== 'CANCELLED' && (
                <div className="bg-gray-50 p-6 border-t border-gray-100">
                  <button
                    onClick={() => cancelBooking(selectedBooking.booking_id)}
                    className="w-full md:w-auto ml-auto block bg-white text-red-600 border border-red-200 hover:bg-red-50 hover:border-red-300 font-medium py-3 px-6 rounded-xl transition-all shadow-sm hover:shadow"
                  >
                    Cancel Booking
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center h-[500px] flex flex-col justify-center items-center">
              <div className="bg-blue-50 p-6 rounded-full mb-6 animate-bounce-slow">
                <Plane className="h-12 w-12 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Select a Trip</h3>
              <p className="text-gray-500 max-w-sm mx-auto">Click on a booking from the list on the left to view detailed flight information and manage your reservation.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookingHistory;
