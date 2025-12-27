import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

const AdminDashboard = () => {
  const [locations, setLocations] = useState([]);
  
  // Forms State
  const [locForm, setLocForm] = useState({ name: "", airport_code: "", city: "", country: "" });
  const [flightForm, setFlightForm] = useState({ 
    flight_number: "", departure_time: "", arrival_time: "", 
    total_seats: 0, available_seats: 0, price: 0, 
    departure_location: "", arrival_location: "" 
  });
  
  // Edit State
  const [editingLocId, setEditingLocId] = useState(null);

  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    const res = await api.get("/locations/");
    setLocations(res.data);
  };

  // --- Location Handlers ---
  const handleLocSubmit = async (e) => {
    e.preventDefault();
    if (editingLocId) {
      await api.patch(`/locations/${editingLocId}/`, locForm);
      setEditingLocId(null);
    } else {
      await api.post("/locations/", locForm);
    }
    setLocForm({ name: "", airport_code: "", city: "", country: "" });
    fetchLocations();
  };

  const editLocation = (loc) => {
    setEditingLocId(loc.location_id);
    setLocForm(loc);
  };

  // --- Flight Handlers ---
  const handleFlightSubmit = async (e) => {
    e.preventDefault();
    if (flightForm.departure_location === flightForm.arrival_location) {
      return alert("Departure and Arrival cannot be the same");
    }
    await api.post("/flights/", flightForm);
    alert("Flight Added");
    setFlightForm({ ...flightForm, flight_number: "" }); // Reset some fields
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
        <p className="text-gray-600">Manage locations and add flights</p>
      </div>

      <div className="space-y-8">
        {/* Manage Locations */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            {editingLocId ? "Edit Location" : "Add New Location"}
          </h2>
          <form onSubmit={handleLocSubmit} className="space-y-4 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="locName" className="block text-sm font-medium text-gray-700 mb-1">Airport Name</label>
                <input
                  id="locName"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="John F. Kennedy International"
                  value={locForm.name}
                  onChange={e => setLocForm({...locForm, name: e.target.value})}
                  required
                />
              </div>
              <div>
                <label htmlFor="airportCode" className="block text-sm font-medium text-gray-700 mb-1">Airport Code</label>
                <input
                  id="airportCode"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="JFK"
                  value={locForm.airport_code}
                  onChange={e => setLocForm({...locForm, airport_code: e.target.value})}
                  required
                />
              </div>
              <div>
                <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-1">City</label>
                <input
                  id="city"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="New York"
                  value={locForm.city}
                  onChange={e => setLocForm({...locForm, city: e.target.value})}
                  required
                />
              </div>
              <div>
                <label htmlFor="country" className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                <input
                  id="country"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="USA"
                  value={locForm.country}
                  onChange={e => setLocForm({...locForm, country: e.target.value})}
                  required
                />
              </div>
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                {editingLocId ? "Update Location" : "Add Location"}
              </button>
              {editingLocId && (
                <button
                  type="button"
                  onClick={() => setEditingLocId(null)}
                  className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  Cancel
                </button>
              )}
            </div>
          </form>

          <h3 className="text-lg font-semibold text-gray-900 mb-4">Existing Locations</h3>
          <div className="space-y-3">
            {locations.map(l => (
              <div key={l.location_id} className="flex justify-between items-center p-4 bg-gray-50 rounded-md">
                <div>
                  <span className="font-medium text-gray-900">{l.airport_code}</span>
                  <span className="text-gray-600 ml-2">{l.name}, {l.city}, {l.country}</span>
                </div>
                <div className="space-x-2">
                  <button
                    onClick={() => editLocation(l)}
                    className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    Edit
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Add Flight */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Add New Flight</h2>
          <form onSubmit={handleFlightSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="flightNumber" className="block text-sm font-medium text-gray-700 mb-1">Flight Number</label>
                <input
                  id="flightNumber"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="AA101"
                  onChange={e => setFlightForm({...flightForm, flight_number: e.target.value})}
                  required
                />
              </div>
              <div>
                <label htmlFor="totalSeats" className="block text-sm font-medium text-gray-700 mb-1">Total Seats</label>
                <input
                  id="totalSeats"
                  type="number"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="200"
                  onChange={e => setFlightForm({...flightForm, total_seats: parseInt(e.target.value), available_seats: parseInt(e.target.value)})}
                  required
                />
              </div>
              <div>
                <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-1">Price ($)</label>
                <input
                  id="price"
                  type="number"
                  step="0.01"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="299.99"
                  onChange={e => setFlightForm({...flightForm, price: parseFloat(e.target.value)})}
                  required
                />
              </div>
              <div>
                <label htmlFor="departureLoc" className="block text-sm font-medium text-gray-700 mb-1">Departure Location</label>
                <select
                  id="departureLoc"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={e => setFlightForm({...flightForm, departure_location: e.target.value})}
                  required
                >
                  <option value="">Select Departure</option>
                  {locations.map(l => <option key={l.location_id} value={l.airport_code}>{l.city} ({l.airport_code})</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="arrivalLoc" className="block text-sm font-medium text-gray-700 mb-1">Arrival Location</label>
                <select
                  id="arrivalLoc"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={e => setFlightForm({...flightForm, arrival_location: e.target.value})}
                  required
                >
                  <option value="">Select Arrival</option>
                  {locations.map(l => <option key={l.location_id} value={l.airport_code}>{l.city} ({l.airport_code})</option>)}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="departureTime" className="block text-sm font-medium text-gray-700 mb-1">Departure Time</label>
                <input
                  id="departureTime"
                  type="datetime-local"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={e => setFlightForm({...flightForm, departure_time: e.target.value})}
                  required
                />
              </div>
              <div>
                <label htmlFor="arrivalTime" className="block text-sm font-medium text-gray-700 mb-1">Arrival Time</label>
                <input
                  id="arrivalTime"
                  type="datetime-local"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  onChange={e => setFlightForm({...flightForm, arrival_time: e.target.value})}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
            >
              Add Flight
            </button>
          </form>
        </section>

        {/* Link to Manage Flights */}
        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Manage Existing Flights</h2>
          <p className="text-gray-600 mb-4">View, edit, or delete existing flights</p>
          <Link
            to="/admin/flights"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-md transition-colors"
          >
            Go to Flight Management
          </Link>
        </section>
      </div>
    </div>
  );
};

export default AdminDashboard;