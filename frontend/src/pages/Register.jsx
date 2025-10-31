import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function Register() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.name || !form.email || !form.phone || !form.password) {
      setMessage("⚠️ Please fill out all fields.");
      return;
    }

    try {
      console.log("User Registered:", form);

      // Mock successful registration
      localStorage.setItem("isLoggedIn", "true");
      setMessage("✅ Registration successful! Redirecting...");
      setTimeout(() => navigate("/home"), 1000);
    } catch (error) {
      setMessage("❌ Registration failed. Try again.");
    }
  };

  return (
    <div className="auth-container">
      <h1>🧾 Create Your Account</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="text"
          name="name"
          placeholder="Full Name"
          value={form.name}
          onChange={handleChange}
        />
        <input
          type="email"
          name="email"
          placeholder="Email Address"
          value={form.email}
          onChange={handleChange}
        />
        <input
          type="text"
          name="phone"
          placeholder="Phone Number"
          value={form.phone}
          onChange={handleChange}
        />
        <input
          type="password"
          name="password"
          placeholder="Create Password"
          value={form.password}
          onChange={handleChange}
        />
        <button type="submit" className="auth-btn">
          Register
        </button>
      </form>
      {message && <p className="auth-message">{message}</p>}

      <p className="auth-switch">
        Already have an account?{" "}
        <a href="/login" className="auth-link">
          Log in
        </a>
      </p>
    </div>
  );
}
