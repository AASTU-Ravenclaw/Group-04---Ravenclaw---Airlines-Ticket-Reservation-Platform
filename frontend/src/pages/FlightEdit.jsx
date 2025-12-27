import React, { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import api from "../api/axios";

const FlightEdit = () => {
  const { flightId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [flight, setFlight] = useState(null);
  const [status, setStatus] = useState("");
  const [departure_time, setDepartureTime] = useState("");
  const [arrival_time, setArrivalTime] = useState("");

  useEffect(() => {
    fetchFlight();
  }, [flightId]);

  const fetchFlight = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/flights/${flightId}/`);
      const flightData = res.data;
      setFlight(flightData);
      setStatus(flightData.status);
      setDepartureTime(new Date(flightData.departure_time).toISOString().slice(0, 16));
      setArrivalTime(new Date(flightData.arrival_time).toISOString().slice(0, 16));
    } catch (err) {
      console.error("Error fetching flight:", err);
      alert("Error loading flight details");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (flight.status === 'departed') {
      return alert("Cannot edit a flight that has departed");
    }

    setSaving(true);
    try {
      await api.patch(`/flights/${flightId}/`, { status, departure_time, arrival_time });
      alert("Flight updated successfully");
      navigate("/admin/flights");
    } catch (err) {
      console.error("Error updating flight:", err);
      alert("Error updating flight status");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading flight details...</p>
        </div>
      </div>
    );
  }

  if (!flight) {
    return (
      <div className="max-w-4xl mx-auto py-8">
        <p className="text-center text-gray-500">Flight not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Edit Flight</h1>
          <p className="text-gray-600">Update flight details</p>
        </div>
        <Link
          to="/admin/flights"
          className="bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
        >
          Back to Flights
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Flight Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Flight Number</label>
              <p className="text-gray-900">{flight.flight_number}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Departure Location</label>
              <p className="text-gray-900">{flight.departure_location.city} ({flight.departure_location.airport_code})</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Arrival Location</label>
              <p className="text-gray-900">{flight.arrival_location.city} ({flight.arrival_location.airport_code})</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Departure Time</label>
              <p className="text-gray-900">{new Date(flight.departure_time).toLocaleString()}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Arrival Time</label>
              <p className="text-gray-900">{new Date(flight.arrival_time).toLocaleString()}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Total Seats</label>
              <p className="text-gray-900">{flight.total_seats}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Available Seats</label>
              <p className="text-gray-900">{flight.available_seats}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Price</label>
              <p className="text-gray-900">${flight.price}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Current Status</label>
              <p className="text-gray-900 capitalize">{flight.status}</p>
            </div>
          </div>
        </div>

        {flight.status === 'departed' ? (
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
            <p className="text-yellow-800">This flight has departed and cannot be edited.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="departureTime" className="block text-sm font-medium text-gray-700 mb-2">Departure Time</label>
                <input
                  id="departureTime"
                  type="datetime-local"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={departure_time}
                  onChange={e => setDepartureTime(e.target.value)}
                  required
                />
              </div>
              <div>
                <label htmlFor="arrivalTime" className="block text-sm font-medium text-gray-700 mb-2">Arrival Time</label>
                <input
                  id="arrivalTime"
                  type="datetime-local"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={arrival_time}
                  onChange={e => setArrivalTime(e.target.value)}
                  required
                />
              </div>
            </div>
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">Update Status</label>
              <select
                id="status"
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={status}
                onChange={e => setStatus(e.target.value)}
                required
              >
                <option value="scheduled">Scheduled</option>
                <option value="boarding">Boarding</option>
                <option value="departed">Departed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <div className="flex space-x-4 pt-6 border-t border-gray-200">
              <button
                type="submit"
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-6 rounded-md transition-colors"
              >
                {saving ? "Saving..." : "Update Flight"}
              </button>
              <Link
                to="/admin/flights"
                className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-6 rounded-md transition-colors"
              >
                Cancel
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default FlightEdit;