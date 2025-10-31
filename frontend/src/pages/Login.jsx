import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.email || !form.password) {
      setMessage("⚠️ Please enter both email and password.");
      return;
    }

    try {
      // Mock backend authentication
      console.log("User Logged In:", form);

      // Example check: accept any credentials for now
      localStorage.setItem("isLoggedIn", "true");
      setMessage("✅ Login successful! Redirecting...");
      setTimeout(() => navigate("/home"), 1000);
    } catch (error) {
      setMessage("❌ Invalid credentials. Try again.");
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
        <button type="submit" className="auth-btn">
          Login
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
