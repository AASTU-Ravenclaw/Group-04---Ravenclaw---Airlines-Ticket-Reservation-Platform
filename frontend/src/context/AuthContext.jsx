import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import api from "../api/axios";

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({});
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const user = JSON.parse(localStorage.getItem("user"));
    const token = localStorage.getItem("accessToken");
    if (user && token) {
      setAuth({ user, accessToken: token });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const res = await api.post(`/auth/login`, { email, password });
      
      if (res.data.access && res.data.refresh && res.data.user) {
        const { access, refresh, user } = res.data;

        localStorage.setItem("accessToken", access);
        localStorage.setItem("refreshToken", refresh);
        localStorage.setItem("user", JSON.stringify(user));

        setAuth({ user, accessToken: access });
        return true;
      }
    } catch (error) {
      console.error("Login failed:", error);
      toast.error(error.response?.data?.detail || "Login failed. Please check your credentials.");
    }
    return false;
  };

  const logout = () => {
    localStorage.clear();
    setAuth({});
    navigate("/login");
    toast.success("Logged out successfully");
  };

  return (
    <AuthContext.Provider value={{ auth, setAuth, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;