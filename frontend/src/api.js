// src/api.js
import axios from "axios";

// ✅ Base URL — Django backend
const API_BASE = "http://127.0.0.1:8000/api";
const PREDICTOR_API = `${API_BASE}/predictor`;
const AUTH_API = `${API_BASE}/auth`; // Correct endpoint for auth routes

// ✅ Helper: Attach auth token safely
const authHeader = () => {
  const token = localStorage.getItem("access");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// 🧠 Predict Parkinson’s Disease
export const predictParkinsons = async (formData) => {
  const headers = { "Content-Type": "multipart/form-data", ...authHeader() };
  try {
    const response = await axios.post(`${PREDICTOR_API}/predict/`, formData, { headers });
    return response;
  } catch (error) {
    return handleApiError(error, "Prediction failed");
  }
};

// 📊 Fetch Results
export const fetchResults = async () => {
  const headers = { ...authHeader() };
  try {
    const response = await axios.get(`${PREDICTOR_API}/results/`, { headers });
    return response.data;
  } catch (error) {
    return handleApiError(error, "Failed to fetch results");
  }
};

// 🔐 User Login
export const loginUser = async (formData) => {
  try {
    const response = await axios.post(`${AUTH_API}/login/`, formData);
    return response.data;
  } catch (error) {
    return handleApiError(error, "Login failed");
  }
};

// 🧍‍♂️ User Registration
export const registerUser = async (formData) => {
  try {
    const response = await axios.post(`${AUTH_API}/register/`, formData);
    return response.data;
  } catch (error) {
    return handleApiError(error, "Registration failed");
  }
};

// 🧩 Centralized error handler
const handleApiError = (error, fallbackMessage) => {
  console.error("API Error:", error);

  // Default response object
  const safeResponse = { success: false, error: fallbackMessage };

  if (error.response) {
    const data = error.response.data;

    // HTML error (like 404 pages)
    if (typeof data === "string" && data.startsWith("<!DOCTYPE html")) {
      safeResponse.error = `${fallbackMessage}. Server route not found.`;
      return safeResponse;
    }

    // Django REST validation error
    if (typeof data === "object") {
      const combined = Object.values(data).flat().join(" ");
      safeResponse.error = `${fallbackMessage}. ${combined}`;
      return safeResponse;
    }

    safeResponse.error = data?.error || fallbackMessage;
    return safeResponse;
  }

  if (error.request) {
    safeResponse.error = "Server unreachable. Please check your backend connection.";
    return safeResponse;
  }

  safeResponse.error = fallbackMessage;
  return safeResponse;
};
