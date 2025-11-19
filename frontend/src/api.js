// src/api.js
import axios from "axios";

// ✅ Base URL — Django backend
const API_BASE = "http://127.0.0.1:8000/api";
const PREDICTOR_API = `${API_BASE}/predictor`;
const AUTH_API = `${API_BASE}/auth`;

// ✅ Helper: Attach auth token safely
const authHeader = () => {
  const token = localStorage.getItem("access");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// ✅ Helper: Refresh access token
const refreshToken = async () => {
  const refresh = localStorage.getItem("refresh");
  if (!refresh) return false;

  try {
    const response = await axios.post(`${AUTH_API}/token/refresh/`, { refresh });
    localStorage.setItem("access", response.data.access);
    return true;
  } catch (err) {
    console.error("❌ Refresh token failed:", err);
    return false;
  }
};

// ✅ Helper: Make request with automatic token refresh
const requestWithRetry = async (axiosRequest) => {
  try {
    return await axiosRequest();
  } catch (err) {
    // Retry if token expired
    if (err.response && err.response.status === 401) {
      const refreshed = await refreshToken();
      if (refreshed) {
        return await axiosRequest();
      }
    }
    throw err;
  }
};

// 🧠 Predict Parkinson’s Disease
export const predictParkinsons = async (formData) => {
  try {
    const response = await requestWithRetry(() =>
      axios.post(`${PREDICTOR_API}/predict/`, formData, {
        headers: { "Content-Type": "multipart/form-data", ...authHeader() },
      })
    );

    // Ensure consistent report property for frontend
    const data = response.data;
    if (data.report_file && !data.report_url) {
      data.report_url = `${PREDICTOR_API}/download/${data.report_file}/`;
    }

    return { data, status: response.status };
  } catch (error) {
    return handleApiError(error, "Prediction failed");
  }
};

// 📊 Fetch Results
export const fetchResults = async () => {
  try {
    const response = await requestWithRetry(() =>
      axios.get(`${PREDICTOR_API}/results/`, { headers: { ...authHeader() } })
    );
    return response.data;
  } catch (error) {
    return handleApiError(error, "Failed to fetch results");
  }
};

// 🔐 User Login
export const loginUser = async (formData) => {
  try {
    const response = await axios.post(`${AUTH_API}/login/`, formData);
    localStorage.setItem("access", response.data.access);
    localStorage.setItem("refresh", response.data.refresh);
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

// 📝 Download Parkinson’s Prediction Report
export const downloadReport = async (reportName) => {
  try {
    const response = await requestWithRetry(() =>
      axios.get(`${PREDICTOR_API}/download/${reportName}/`, {
        headers: { ...authHeader() },
        responseType: "blob",
      })
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", reportName);
    document.body.appendChild(link);
    link.click();
    link.remove();

    return { success: true };
  } catch (error) {
    return handleApiError(error, "Failed to download report");
  }
};

// 🧩 Centralized error handler
const handleApiError = (error, fallbackMessage) => {
  console.error("API Error:", error);

  const safeResponse = { success: false, error: fallbackMessage };

  if (error.response) {
    const data = error.response.data;

    if (typeof data === "string" && data.startsWith("<!DOCTYPE html")) {
      safeResponse.error = `${fallbackMessage}. Server route not found.`;
      return safeResponse;
    }

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

  return safeResponse;
};
