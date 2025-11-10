// src/pages/Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { loginUser } from "../api"; // Ensure this API is correct

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // ✅ Handle input change
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // ✅ Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.email || !form.password) {
      setMessage("⚠️ Please enter both email and password.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const res = await loginUser(form);

      if (res.access) localStorage.setItem("access", res.access);
      if (res.refresh) localStorage.setItem("refresh", res.refresh);
      if (res.user) localStorage.setItem("user", JSON.stringify(res.user));

      setMessage("✅ Login successful! Redirecting...");
      setTimeout(() => navigate("/home", { replace: true }), 500);
    } catch (error) {
      console.error("❌ Login Error:", error);
      if (error.response && error.response.data) {
        const data = error.response.data;
        setMessage(
          data.error ||
            data.detail ||
            "❌ Invalid credentials. Please try again."
        );
      } else {
        setMessage("❌ Server error. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h1>🔐 User Login</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="email"
          name="email"
          placeholder="Email Address"
          value={form.email}
          onChange={handleChange}
        />
        <input
          type="password"
          name="password"
          placeholder="Enter Password"
          value={form.password}
          onChange={handleChange}
        />
        <button type="submit" className="auth-btn" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      {message && <p className="auth-message">{message}</p>}

      <p className="auth-switch">
        Don’t have an account?{" "}
        <a href="/register" className="auth-link">
          Create one
        </a>
      </p>
    </div>
  );
}
