import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

const FlightsList = () => {
  const [flights, setFlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ from: "", to: "", date: "" });

  const fetchFlights = async () => {
    setLoading(true);
    try {
      const res = await api.get("/flights/", {
        params: { ...filters, _t: Date.now() },
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      setFlights(res.data);
    } catch (err) {
      console.error("Error fetching flights:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFlights();
  }, []);

  const deleteFlight = async (flightId) => {
    if (!window.confirm("Are you sure you want to delete this flight?")) return;
    try {
      await api.delete(`/flights/${flightId}/`);
      fetchFlights();
    } catch (err) {
      alert("Error deleting flight");
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Flight Management</h1>
            <p className="text-gray-600">View, edit, and delete existing flights</p>
          </div>
          <Link
            to="/admin"
            className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter Flights</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="From (City or Airport Code)"
              value={filters.from}
              onChange={e => setFilters({...filters, from: e.target.value})}
            />
            <input
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="To (City or Airport Code)"
              value={filters.to}
              onChange={e => setFilters({...filters, to: e.target.value})}
            />
            <input
              type="date"
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={filters.date}
              onChange={e => setFilters({...filters, date: e.target.value})}
            />
            <button
              onClick={fetchFlights}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Flights List */}
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading flights...</p>
        </div>
      </div>
    );
  } else {
    return (
      <div className="max-w-7xl mx-auto py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Flight Management</h1>
            <p className="text-gray-600">View, edit, and delete existing flights</p>
          </div>
          <Link
            to="/admin"
            className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
          >
            Back to Dashboard
          </Link>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Filter Flights</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="From (City or Airport Code)"
              value={filters.from}
              onChange={e => setFilters({...filters, from: e.target.value})}
            />
            <input
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="To (City or Airport Code)"
              value={filters.to}
              onChange={e => setFilters({...filters, to: e.target.value})}
            />
            <input
              type="date"
              className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={filters.date}
              onChange={e => setFilters({...filters, date: e.target.value})}
            />
            <button
              onClick={fetchFlights}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Flights List */}
        <div className="space-y-4">
          {flights.length === 0 ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <p className="text-gray-500">No flights found</p>
            </div>
          ) : (
            flights.map(f => (
              <div key={f.flight_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">{f.flight_number}</h3>
                      <span className="text-sm text-gray-500">ID: {f.flight_id.slice(-8)}</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Route</p>
                        <p className="font-medium text-gray-900">
                          {f.departure_location.city} ({f.departure_location.airport_code}) → {f.arrival_location.city} ({f.arrival_location.airport_code})
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Schedule</p>
                        <p className="font-medium text-gray-900">
                          {new Date(f.departure_time).toLocaleString()} - {new Date(f.arrival_time).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Seats</p>
                        <p className="font-medium text-gray-900">
                          {f.available_seats} / {f.total_seats} available
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Price</p>
                        <p className="font-medium text-green-600 text-lg">${f.price}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Status</p>
                        <p className="font-medium text-gray-900 capitalize">{f.status || 'scheduled'}</p>
                      </div>
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <Link
                      to={`/admin/flights/${f.flight_id}/edit`}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      Edit
                    </Link>
                    <button
                      onClick={() => deleteFlight(f.flight_id)}
                      className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    );
  }
};

export default FlightsList;