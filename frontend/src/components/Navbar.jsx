// src/components/Navbar.jsx
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "../App.css";

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        {/* Left Logo Section */}
        <div className="navbar-logo" onClick={() => navigate("/home")}>
          <span role="img" aria-label="brain" className="navbar-logo-icon">
            🧠
          </span>
          <span className="navbar-logo-text">NeuroPredict</span>
        </div>

        {/* Right Navigation Links */}
        <ul className="navbar-links">
          <li>
            <Link to="/home">Home</Link>
          </li>
           <li>
            <Link to="/about">About</Link>
          </li>
          <li>
            <Link to="/upload">Upload</Link>
          </li>
          <li>
            <Link to="/results">Results</Link>
          </li>
         
          <li>
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
}
