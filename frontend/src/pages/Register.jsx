import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { registerUser } from "../api";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    full_name: "",
    email: "",
    phone: "",
    password: "",
    password2: "",
  });

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // ✅ If already logged in, redirect directly to home
  useEffect(() => {
    const token = localStorage.getItem("access");
    if (token) {
      navigate("/home");
    }
  }, [navigate]);

  // Handle input change
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!form.username || !form.email || !form.password || !form.password2) {
      setMessage("⚠️ Please fill all required fields.");
      return;
    }

    if (form.password !== form.password2) {
      setMessage("⚠️ Passwords do not match.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const res = await registerUser(form);

      // ✅ Save tokens & user info if backend returns them
      if (res.access) localStorage.setItem("access", res.access);
      if (res.refresh) localStorage.setItem("refresh", res.refresh);
      if (res.user) localStorage.setItem("user", JSON.stringify(res.user));

      setMessage("✅ Registration successful! Redirecting...");

      // ✅ After successful registration → redirect to home
      setTimeout(() => navigate("/home"), 1200);
    } catch (error) {
      console.error("❌ Registration Error:", error);

      if (error.response && error.response.data) {
        const data = error.response.data;
        let errMsg = "❌ Registration failed. ";

        if (typeof data === "object") {
          errMsg += Object.values(data).flat().join(" ");
        } else {
          errMsg += data;
        }

        setMessage(errMsg);
      } else {
        setMessage("❌ Something went wrong. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h1>🧾 User Registration</h1>
      <form onSubmit={handleSubmit} className="auth-form">
        <input
          type="text"
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          required
        />
        <input
          type="text"
          name="full_name"
          placeholder="Full Name"
          value={form.full_name}
          onChange={handleChange}
        />
        <input
          type="email"
          name="email"
          placeholder="Email Address"
          value={form.email}
          onChange={handleChange}
          required
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
          placeholder="Enter Password"
          value={form.password}
          onChange={handleChange}
          required
        />
        <input
          type="password"
          name="password2"
          placeholder="Confirm Password"
          value={form.password2}
          onChange={handleChange}
          required
        />

        <button type="submit" className="auth-btn" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>

      {message && <p className="auth-message">{message}</p>}

      <p className="auth-switch">
        Already have an account?{" "}
        <a href="/login" className="auth-link">
          Login here
        </a>
      </p>
    </div>
  );
}
