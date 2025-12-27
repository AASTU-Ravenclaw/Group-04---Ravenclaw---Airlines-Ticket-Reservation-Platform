import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";

// Pages
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import FlightDetails from "./pages/FlightDetails";
import BookingHistory from "./pages/BookingHistory";
import AdminDashboard from "./pages/AdminDashboard";
import FlightsList from "./pages/FlightsList";
import FlightEdit from "./pages/FlightEdit";
import AdminBookings from "./pages/AdminBookings";
import ProfileEdit from "./pages/ProfileEdit";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/flight/:id" element={<FlightDetails />} />

              {/* Client Protected Routes */}
              <Route element={<ProtectedRoute allowedRoles={['CLIENT', 'ADMIN']} />}>
                <Route path="/history" element={<BookingHistory />} />
                <Route path="/profile" element={<ProfileEdit />} />
              </Route>

              {/* Admin Protected Routes */}
              <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
                <Route path="/admin" element={<AdminDashboard />} />
                <Route path="/admin/flights" element={<FlightsList />} />
                <Route path="/admin/flights/:flightId/edit" element={<FlightEdit />} />
                <Route path="/admin/bookings" element={<AdminBookings />} />
              </Route>

            </Routes>
          </main>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;