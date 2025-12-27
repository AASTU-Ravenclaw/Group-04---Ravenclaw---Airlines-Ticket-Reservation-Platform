import React, { useEffect, useState, useContext } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";

const FlightDetails = () => {
  const { id } = useParams();
  const { auth } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const [flight, setFlight] = useState(null);
  const [isBooking, setIsBooking] = useState(false);
  const [passengers, setPassengers] = useState([]);

  useEffect(() => {
    api.get(`/flights/${id}/`).then(res => setFlight(res.data));
  }, [id]);

  const startBooking = () => {
    if (!auth.user) {
      // Redirect to login then back here
      navigate("/login", { state: { from: location } });
    } else {
      setIsBooking(true);
      // Initialize first passenger as logged in user (Auto-fill)
      setPassengers([{ 
        firstName: auth.user.first_name, 
        lastName: auth.user.last_name, 
        email: auth.user.email 
      }]);
    }
  };

  const handlePassengerChange = (index, field, value) => {
    const newPassengers = [...passengers];
    newPassengers[index][field] = value;
    setPassengers(newPassengers);
  };

  const addPassenger = () => {
    setPassengers([...passengers, { firstName: "", lastName: "", email: "" }]);
  };

  const submitBooking = async () => {
    try {
      const bookingData = {
        flight_id: flight.flight_id,
        passengers: passengers.length
      };

      await api.post("/bookings/", bookingData);
      
      alert("Booking Confirmed!");
      navigate("/history");
    } catch (err) {
      console.error(err);
      alert("Booking Failed: " + JSON.stringify(err.response?.data || err.message));
    }
  };

  if (!flight) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Flight {flight.flight_number}</h1>
          <div className="text-lg text-gray-600">
            {flight.departure_location.city} ({flight.departure_location.airport_code}) → {flight.arrival_location.city} ({flight.arrival_location.airport_code})
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="font-medium text-gray-900 mb-2">Departure</h3>
            <p className="text-gray-700">{new Date(flight.departure_time).toLocaleString()}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-md">
            <h3 className="font-medium text-gray-900 mb-2">Arrival</h3>
            <p className="text-gray-700">{new Date(flight.arrival_time).toLocaleString()}</p>
          </div>
        </div>

        <div className="flex justify-between items-center mb-6">
          <div className="text-2xl font-bold text-green-600">${flight.price}</div>
          <div className="text-gray-600">Available Seats: {flight.available_seats}</div>
        </div>

        {!isBooking ? (
          <div className="text-center">
            <button
              onClick={startBooking}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-8 rounded-md transition-colors text-lg"
            >
              Book This Flight
            </button>
          </div>
        ) : (
          <div className="border-t pt-6">
            <h3 className="text-2xl font-semibold mb-4">Passenger Details</h3>
            <div className="space-y-6">
              {passengers.map((p, idx) => (
                <div key={idx} className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold mb-3">Passenger {idx + 1}</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input
                      className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="First Name"
                      value={p.firstName}
                      onChange={e => handlePassengerChange(idx, 'firstName', e.target.value)}
                    />
                    <input
                      className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Last Name"
                      value={p.lastName}
                      onChange={e => handlePassengerChange(idx, 'lastName', e.target.value)}
                    />
                    <input
                      className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Email"
                      value={p.email}
                      onChange={e => handlePassengerChange(idx, 'email', e.target.value)}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center mt-6">
              <button
                onClick={addPassenger}
                className="bg-gray-500 hover:bg-gray-600 text-white font-semibold py-2 px-4 rounded-lg transition duration-300"
              >
                + Add Another Passenger
              </button>
              <button
                onClick={submitBooking}
                className="bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-300"
              >
                Confirm Booking
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlightDetails;
