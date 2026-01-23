import React, { useEffect, useState, useContext } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";
import toast from "react-hot-toast";
import {
    Clock, Calendar, MapPin, CheckCircle, AlertTriangle, User, CreditCard,
    Plane, ChevronRight, Users, ArrowRight, X
} from "lucide-react";

const FlightDetails = () => {
  const { id } = useParams();
  const { auth } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();

  const [flight, setFlight] = useState(null);
  const [isBooking, setIsBooking] = useState(false);
  const [passengers, setPassengers] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchFlight = async () => {
        try {
            const res = await api.get(`/flights/${id}/`);
            setFlight(res.data);
        } catch (err) {
            console.error(err);
            toast.error("Failed to load flight details");
            navigate('/');
        }
    };
    fetchFlight();
  }, [id, navigate]);

  const startBooking = () => {
    if (!auth.user) {
      // Redirect to login then back here
      toast('Please login to continue booking', { icon: '🔒' });
      navigate("/login", { state: { from: location } });
    } else {
      setIsBooking(true);
      // Initialize first passenger as logged in user (Auto-fill)
      setPassengers([{ 
        first_name: auth.user.first_name || "", 
        last_name: auth.user.last_name || "", 
        email: auth.user.email || ""
      }]);
      // Scroll to booking section
      setTimeout(() => {
          document.getElementById('booking-form')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  const handlePassengerChange = (index, field, value) => {
    const newPassengers = [...passengers];
    newPassengers[index][field] = value;
    setPassengers(newPassengers);
  };

  const addPassenger = () => {
    if (passengers.length >= 10) {
        toast.error("Maximum 10 passengers allowed");
        return;
    }
    setPassengers([...passengers, { first_name: "", last_name: "", email: "" }]);
  };

  const removePassenger = (index) => {
      if (passengers.length === 1) return;
      const newPassengers = passengers.filter((_, i) => i !== index);
      setPassengers(newPassengers);
  };

  const submitBooking = async () => {
    // Validation
    for (let i = 0; i < passengers.length; i++) {
        const p = passengers[i];
        if (!p.first_name || !p.last_name || !p.email) {
            toast.error(`Please fill in all details for Passenger ${i + 1}`);
            return;
        }
    }

    setIsSubmitting(true);
    const toastId = toast.loading("Processing your booking...");

    try {
      const bookingData = {
        flight_id: flight.flight_id,
        passengers: passengers.length,
        passengers_list: passengers // Sending full list to backend
      };

      await api.post("/bookings/", bookingData);
      
      toast.success("Booking Confirmed! Have a safe trip.", { id: toastId });
      navigate("/history");
    } catch (err) {
      console.error(err);
      toast.error(
          err.response?.data?.detail || "Booking Failed. Please try again.", 
          { id: toastId }
      );
    } finally {
        setIsSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
        case 'scheduled': return 'bg-green-100 text-green-700 border-green-200';
        case 'delayed': return 'bg-orange-100 text-orange-700 border-orange-200';
        case 'cancelled': return 'bg-red-100 text-red-700 border-red-200';
        default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  if (!flight) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
    </div>
  );

  return (
    <div className="max-w-5xl mx-auto py-12 px-4">
      
      {/* Flight Header Card */}
      <div className="bg-white rounded-3xl shadow-xl border border-gray-100 overflow-hidden mb-8 animate-fade-in-down">
        {/* Top Banner */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 h-32 relative">
            <div className="absolute -bottom-10 left-8 p-4 bg-white rounded-2xl shadow-lg">
                <div className="bg-blue-50 p-3 rounded-full">
                    <Plane className="w-8 h-8 text-blue-600" />
                </div>
            </div>
            <div className="absolute top-6 right-8">
                 <span className={`px-4 py-1.5 rounded-full text-sm font-bold uppercase tracking-wider shadow-sm border ${getStatusColor(flight.status)}`}>
                    {flight.status}
                 </span>
            </div>
        </div>

        <div className="pt-14 px-8 pb-8">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
                        {flight.departure_location.city} <span className="text-gray-300 font-light">to</span> {flight.arrival_location.city}
                    </h1>
                    <p className="text-lg text-gray-500 font-medium flex items-center">
                        Flight {flight.flight_number}
                        <span className="mx-2 text-gray-300">•</span>
                        <span className="text-blue-600">{
                            new Date(flight.departure_time).toLocaleDateString(undefined, {weekday:'long', month:'long', day:'numeric'})
                        }</span>
                    </p>
                </div>
                <div className="text-right">
                    <p className="text-sm text-gray-500 mb-1">Price per person</p>
                    <p className="text-4xl font-bold text-green-600 tracking-tight">${flight.price}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
                {/* Departure */}
                <div className="relative pl-8 border-l-2 border-dashed border-gray-300">
                    <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-white"></div>
                    <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Departure</p>
                    <p className="text-2xl font-bold text-gray-900">{new Date(flight.departure_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                    <p className="text-lg font-medium text-gray-700 mt-1">{flight.departure_location.city}</p>
                    <p className="text-gray-500">{flight.departure_location.airport_code}</p>
                </div>

                {/* Arrival */}
                <div className="relative pl-8 border-l-2 border-dashed border-gray-300 md:border-none md:pl-0">
                    <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-indigo-500 ring-4 ring-white md:hidden"></div>
                    <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Arrival</p>
                    <p className="text-2xl font-bold text-gray-900">{new Date(flight.arrival_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                    <p className="text-lg font-medium text-gray-700 mt-1">{flight.arrival_location.city}</p>
                    <p className="text-gray-500">{flight.arrival_location.airport_code}</p>
                </div>
            </div>

            <div className="mt-10 pt-8 border-t border-gray-100 flex items-center justify-between">
                <div className="flex items-center text-sm text-gray-600">
                    <Users className="w-5 h-5 mr-2 text-gray-400" />
                    <span className="font-semibold mr-1">{flight.available_seats}</span> seats remaining
                </div>
                {!isBooking && (
                    <button
                        onClick={startBooking}
                        disabled={flight.status === 'cancelled' || flight.available_seats === 0}
                        className={`flex items-center px-8 py-3 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-1 ${
                            flight.status === 'cancelled' || flight.available_seats === 0 
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                    >
                        Book This Flight
                        <ArrowRight className="ml-2 w-5 h-5" />
                    </button>
                )}
            </div>
        </div>
      </div>

      {/* Booking Form Section */}
      {isBooking && (
        <div id="booking-form" className="animate-fade-in-up">
            <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                    <CreditCard className="w-6 h-6 mr-3 text-blue-600" />
                    Passenger Details
                </h3>

                <div className="space-y-6">
                {passengers.map((p, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-2xl p-6 border border-gray-200 relative group transition-all hover:bg-white hover:shadow-md hover:border-blue-200">
                        <div className="flex justify-between items-center mb-4">
                            <h4 className="font-bold text-gray-800 flex items-center">
                                <span className="bg-blue-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs mr-3">
                                    {idx + 1}
                                </span>
                                Passenger Information
                            </h4>
                            {passengers.length > 1 && (
                                <button 
                                    onClick={() => removePassenger(idx)}
                                    className="text-gray-400 hover:text-red-500 transition-colors"
                                    title="Remove Passenger"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            )}
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                            <div>
                                <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">First Name</label>
                                <input
                                className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="J.K."
                                value={p.first_name}
                                onChange={e => handlePassengerChange(idx, 'first_name', e.target.value)}
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Last Name</label>
                                <input
                                className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="Rowling"
                                value={p.last_name}
                                onChange={e => handlePassengerChange(idx, 'last_name', e.target.value)}
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-semibold text-gray-500 uppercase mb-1">Email Address</label>
                                <input
                                type="email"
                                className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="auth@hogwarts.edu"
                                value={p.email}
                                onChange={e => handlePassengerChange(idx, 'email', e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                ))}
                </div>

                <div className="flex flex-col md:flex-row justify-between items-center mt-8 gap-4 pt-6 border-t border-gray-100">
                    <button
                        onClick={addPassenger}
                        className="w-full md:w-auto text-blue-600 font-semibold px-6 py-3 rounded-lg hover:bg-blue-50 transition-colors flex items-center justify-center border border-dashed border-blue-300"
                    >
                        <Users className="w-5 h-5 mr-2" />
                        Add Another Passenger
                    </button>
                    
                    <div className="w-full md:w-auto flex items-center gap-4">
                        <div className="text-right hidden md:block">
                            <p className="text-gray-500 text-sm">Total Amount</p>
                            <p className="text-2xl font-bold text-gray-900">${(flight.price * passengers.length).toFixed(2)}</p>
                        </div>
                        <button
                            onClick={submitBooking}
                            disabled={isSubmitting}
                            className={`w-full md:w-auto bg-green-600 hover:bg-green-700 text-white font-bold py-3.5 px-8 rounded-xl shadow-lg hover:shadow-green-200/50 transition-all flex items-center justify-center ${isSubmitting ? 'opacity-70 cursor-wait' : ''}`}
                        >
                            {isSubmitting ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                            ) : (
                                <CheckCircle className="w-5 h-5 mr-2" />
                            )}
                            Confirm Booking
                        </button>
                    </div>
                </div>
            </div>
        </div>
      )}
    </div>
  );
};

export default FlightDetails;
