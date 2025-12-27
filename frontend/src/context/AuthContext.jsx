import { createContext, useState, useEffect } from "react";
import api from "../api/axios";

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({});
  const [loading, setLoading] = useState(true);

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
    }
    return false;
  };

  const logout = () => {
    localStorage.clear();
    setAuth({});
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ auth, setAuth, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;