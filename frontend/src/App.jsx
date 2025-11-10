// src/App.jsx

import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";

import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Upload from "./pages/Upload";
import Results from "./pages/Results";
import About from "./pages/About";
import Login from "./pages/Login";
import Register from "./pages/Register";

// ✅ Auth Guard
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem("access");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

// ✅ Layout (Navbar/Footer control)
const Layout = ({ children }) => {
  const location = useLocation();
  const hideLayout =
    location.pathname === "/login" || location.pathname === "/register";

  return (
    <>
      {!hideLayout && <Navbar />}
      <main style={{ minHeight: "80vh" }}>{children}</main>
      {!hideLayout && <Footer />}
    </>
  );
};

// ✅ Wrapper component so useLocation works inside Router
const AppContent = () => {
  const token = localStorage.getItem("access");

  return (
    <Layout>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={token ? <Navigate to="/home" replace /> : <Login />}
        />
        <Route
          path="/register"
          element={token ? <Navigate to="/home" replace /> : <Register />}
        />

        {/* Protected routes */}
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <Upload />
            </ProtectedRoute>
          }
        />
        <Route
          path="/results"
          element={
            <ProtectedRoute>
              <Results />
            </ProtectedRoute>
          }
        />
        <Route
          path="/about"
          element={
            <ProtectedRoute>
              <About />
            </ProtectedRoute>
          }
        />

        {/* Default redirect */}
        <Route
          path="/"
          element={
            token ? <Navigate to="/home" replace /> : <Navigate to="/login" replace />
          }
        />

        {/* 404 handler */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
};

// ✅ Root App component (Router wrapper)
export default function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
