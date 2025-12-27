import React, { useEffect, useState, useContext } from "react";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";

const AdminBookings = () => {
  const { auth } = useContext(AuthContext);
  const [bookings, setBookings] = useState([]);
  const [selectedBooking, setSelectedBooking] = useState(null);
  const [flightDetails, setFlightDetails] = useState(null);

  const fetchBookings = async () => {
    const res = await api.get(`/bookings/`);
    setBookings(res.data);
  };

  const fetchFlightDetails = async (flightId) => {
    try {
      const res = await api.get(`/flights/${flightId}/`);
      setFlightDetails(res.data);
    } catch (err) {
      console.error("Error fetching flight details:", err);
      setFlightDetails(null);
    }
  };

  useEffect(() => {
    if(auth.user && auth.user.role === 'ADMIN') fetchBookings();
  }, [auth.user]);

  const cancelBooking = async (id) => {
    if(!window.confirm("Are you sure?")) return;
    try {
      await api.delete(`/bookings/${id}/`);
      
      alert("Booking cancelled successfully");
      setSelectedBooking(null);
      setFlightDetails(null);
      fetchBookings();
    } catch (err) {
      alert("Error cancelling booking");
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">All Bookings</h1>
        <p className="text-gray-600">View and manage all flight reservations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Booking List</h2>
          <div className="space-y-3">
            {bookings.map(b => (
              <div
                key={b.booking_id || b.id || i}
                onClick={() => {
                  setSelectedBooking(b);
                  fetchFlightDetails(b.flight_id);
                }}
                className={`cursor-pointer p-4 rounded-lg border-2 transition-colors ${
                  selectedBooking?.booking_id === b.booking_id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-medium text-gray-900 text-sm">Booking #{b.booking_id?.slice(-6) || 'N/A'}</p>
                    <p className="text-xs text-gray-500">{new Date(b.booking_date).toLocaleDateString()}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    b.status === 'CONFIRMED' ? 'bg-green-100 text-green-800' :
                    b.status === 'CANCELLED' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {b.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="lg:col-span-2">
          {selectedBooking ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-2xl font-semibold text-gray-900 mb-6">Booking Details</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                  <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Booking Information</h4>
                  <div className="space-y-2">
                    <p className="text-sm"><span className="font-medium">Booking ID:</span> <code className="bg-gray-100 px-2 py-1 rounded text-xs">{selectedBooking.booking_id}</code></p>
                    <p className="text-sm"><span className="font-medium">Status:</span> 
                      <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                        selectedBooking.status === 'CONFIRMED' ? 'bg-green-100 text-green-800' :
                        selectedBooking.status === 'CANCELLED' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {selectedBooking.status}
                      </span>
                    </p>
                    <p className="text-sm"><span className="font-medium">Booked on:</span> {new Date(selectedBooking.booking_date).toLocaleDateString()}</p>
                  </div>
                </div>
                
                {flightDetails && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-2">Flight Information</h4>
                    <div className="space-y-2">
                      <p className="text-sm"><span className="font-medium">Flight:</span> {flightDetails.flight_number}</p>
                      <p className="text-sm"><span className="font-medium">Route:</span> {flightDetails.departure_location.city} ({flightDetails.departure_location.airport_code}) → {flightDetails.arrival_location.city} ({flightDetails.arrival_location.airport_code})</p>
                      <p className="text-sm"><span className="font-medium">Departure:</span> {new Date(flightDetails.departure_time).toLocaleString()}</p>
                      <p className="text-sm"><span className="font-medium">Arrival:</span> {new Date(flightDetails.arrival_time).toLocaleString()}</p>
                      <p className="text-sm"><span className="font-medium">Price:</span> <span className="text-green-600 font-semibold">${flightDetails.price}</span></p>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="border-t border-gray-200 pt-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Passengers</h4>
                <div className="space-y-3">
                  {selectedBooking.passengers_details.map((p, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                      <div>
                        <p className="font-medium text-gray-900">{p.first_name} {p.last_name}</p>
                      </div>
                      <span className="text-sm text-gray-500">Passenger {i + 1}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {selectedBooking.status !== 'CANCELLED' && (
                <div className="border-t border-gray-200 pt-6 mt-6">
                  <button
                    onClick={() => cancelBooking(selectedBooking.booking_id)}
                    className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
                  >
                    Cancel Booking
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <div className="text-gray-400 mb-4">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-gray-500">Select a booking to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminBookings;