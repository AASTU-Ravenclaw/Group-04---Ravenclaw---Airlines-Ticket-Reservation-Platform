import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import api from '../api/axios';

const ProfileEdit = () => {
  const { auth, setAuth } = useContext(AuthContext);
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (auth.user) {
      setFormData({
        first_name: auth.user.first_name || '',
        last_name: auth.user.last_name || ''
      });
    }
  }, [auth.user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.put('/users/me', formData);
      // Update the auth context with new user data
      setAuth({
        ...auth,
        user: response.data
      });
      navigate('/'); // Redirect to home or back to previous page
    } catch (err) {
      setError('Failed to update profile. Please try again.');
      console.error('Profile update error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!auth.user) {
    return <div className="text-center mt-8">Please log in to edit your profile.</div>;
  }

  return (
    <div className="max-w-md mx-auto mt-8 bg-white p-8 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Edit Profile</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="first_name" className="block text-gray-700 font-medium mb-2">
            First Name
          </label>
          <input
            type="text"
            id="first_name"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="mb-6">
          <label htmlFor="last_name" className="block text-gray-700 font-medium mb-2">
            Last Name
          </label>
          <input
            type="text"
            id="last_name"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition duration-300 disabled:opacity-50"
          >
            {loading ? 'Updating...' : 'Update Profile'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="flex-1 bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-md transition duration-300"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProfileEdit;