import axios from "axios";

// ✅ Base URL — your Django backend
const API_BASE = "http://127.0.0.1:8000/api";
const PREDICTOR_API = `${API_BASE}/predictor`;
const AUTH_API = `${API_BASE}/accounts`;

// ✅ Helper function to attach token consistently
const authHeader = () => {
  const token = localStorage.getItem("access");
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// 🧠 Parkinson’s Prediction
export const predictParkinsons = async (formData) => {
  const headers = {
    "Content-Type": "multipart/form-data",
    ...authHeader(),
  };

  const response = await axios.post(`${PREDICTOR_API}/predict/`, formData, { headers });
  return response; // return full response (not .data)
};

// 🎵 Generate Spectrogram
export const getSpectrogram = async (formData) => {
  const headers = {
    "Content-Type": "multipart/form-data",
    ...authHeader(),
  };

  const response = await axios.post(`${PREDICTOR_API}/spectrogram/`, formData, {
    headers,
    responseType: "blob",
  });

  return URL.createObjectURL(response.data);
};

// 🔐 User Registration
export const registerUser = async (userData) => {
  const response = await axios.post(`${AUTH_API}/register/`, userData);
  return response.data;
};

// 🔐 User Login
export const loginUser = async (credentials) => {
  const response = await axios.post(`${AUTH_API}/login/`, credentials);

  // ✅ Store access and refresh tokens
  if (response.data.access && response.data.refresh) {
    localStorage.setItem("access", response.data.access);
    localStorage.setItem("refresh", response.data.refresh);
  } else if (response.data.token) {
    // fallback if backend returns single token
    localStorage.setItem("access", response.data.token);
  }

  // optional: store user info if backend sends it
  if (response.data.user) {
    localStorage.setItem("user", JSON.stringify(response.data.user));
  }

  return response.data;
};

// 🧩 Fetch Past Prediction Results
export const fetchResults = async () => {
  const headers = authHeader();
  const response = await axios.get(`${PREDICTOR_API}/results/`, { headers });
  return response.data;
};
