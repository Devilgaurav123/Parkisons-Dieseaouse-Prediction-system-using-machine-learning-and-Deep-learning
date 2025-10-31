import axios from "axios";

const API_BASE = "http://127.0.0.1:8000"; // Django backend

export const predictParkinsons = async (formData) => {
  return await axios.post(`${API_BASE}/predict/`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
