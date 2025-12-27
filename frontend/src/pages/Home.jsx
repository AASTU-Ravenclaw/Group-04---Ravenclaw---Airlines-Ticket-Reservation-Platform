import React, { useEffect, useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/axios";
import AuthContext from "../context/AuthContext";

const Home = () => {
  const { auth } = useContext(AuthContext);
  const navigate = useNavigate();
  const [flights, setFlights] = useState([]);
  const [filters, setFilters] = useState({ from: "", to: "", date: "" });

  const fetchFlights = async () => {
    const res = await api.get("/flights/", { params: filters });
    setFlights(res.data);
  };

  useEffect(() => {
    if (auth?.user?.role === 'ADMIN') {
      navigate('/admin');
      return;
    }
    fetchFlights();
  }, [auth, navigate]);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Available Flights</h1>
        <p className="text-gray-600">Find and book your perfect flight</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Flights</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <input
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="From (City or Airport Code)"
            onChange={e => setFilters({...filters, from: e.target.value})}
          />
          <input
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="To (City or Airport Code)"
            onChange={e => setFilters({...filters, to: e.target.value})}
          />
          <input
            type="date"
            className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            onChange={e => setFilters({...filters, date: e.target.value})}
          />
          <button
            onClick={fetchFlights}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Search Flights
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {flights.map(f => (
          <div key={f.flight_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <div className="flex items-center space-x-4 mb-2">
                  <h3 className="text-xl font-semibold text-gray-900">{f.flight_number}</h3>
                  <span className="text-sm text-gray-500">ID: {f.flight_id.slice(-8)}</span>
                </div>
                <p className="text-gray-600 mb-4">{f.departure_location.city} to {f.arrival_location.city}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Departure</p>
                    <p className="font-medium text-gray-900">{new Date(f.departure_time).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Arrival</p>
                    <p className="font-medium text-gray-900">{new Date(f.arrival_time).toLocaleString()}</p>
                  </div>
                </div>
              </div>
              <div className="text-right ml-6">
                <p className="text-3xl font-bold text-green-600 mb-2">${f.price}</p>
                <p className="text-sm text-gray-500 mb-4">per person</p>
                <Link to={`/flight/${f.flight_id}`}>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md transition-colors">
                    View Details
                  </button>
                </Link>
              </div>
            </div>
            <div className="border-t border-gray-200 pt-4">
              <p className="text-gray-600">
                Available Seats: <span className="font-medium">{f.available_seats}/{f.total_seats}</span>
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Home;
