// src/pages/Upload.jsx

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { predictParkinsons } from "../api";

export default function Upload() {
  const [audioFile, setAudioFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleAudioChange = (e) => setAudioFile(e.target.files[0]);
  const handleImageChange = (e) => setImageFile(e.target.files[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!audioFile && !imageFile) {
      setError("⚠️ Please upload at least one file (audio or image).");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      if (audioFile) formData.append("audio_file", audioFile);
      if (imageFile) formData.append("image_file", imageFile);

      // Send flags as booleans, not as strings
      formData.append("use_audio", audioFile ? true : false);
      formData.append("use_image", imageFile ? true : false);
      formData.append("combine_features", true);  // Send as boolean
      formData.append("return_spectrogram", true); // Send as boolean
      formData.append("return_heatmap", true); // Send as boolean
      formData.append("generate_report", true); // Send as boolean

      const prediction = await predictParkinsons(formData);

      console.log("✅ Prediction data:", prediction);

      // Check report URL
      if (!prediction?.data?.report_url && !prediction?.data?.report_file) {
        setError("❌ No report generated.");
        return;
      }

      // Save result for Results page
      localStorage.setItem("latest_result", JSON.stringify(prediction.data));

      // Slight delay before navigating
      setTimeout(() => navigate("/results"), 300);
    } catch (err) {
      console.error("❌ Upload error:", err);
      if (err.response?.status === 401) {
        setError("⚠️ Session expired. Please login again.");
        setTimeout(() => navigate("/login"), 2000);
      } else {
        setError("❌ Could not connect to backend. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-card">
        <h2 className="upload-title">🧠 Upload Data for Prediction</h2>
        <p className="upload-subtitle">
          Upload your <strong>voice sample (.wav)</strong> and/or{" "}
          <strong>MRI image (.png / .jpg)</strong> to get AI-based predictions.
        </p>

        <form onSubmit={handleSubmit} className="upload-form-modern">
          {/* 🎤 Audio Upload */}
          <label className="modern-upload-btn">
            <input
              type="file"
              accept=".wav"
              hidden
              onChange={handleAudioChange}
            />
            🎵 {audioFile ? audioFile.name : "Upload Audio (.wav)"}
          </label>

          {/* 🧠 Image Upload */}
          <label className="modern-upload-btn">
            <input
              type="file"
              accept=".png,.jpg,.jpeg"
              hidden
              onChange={handleImageChange}
            />
            🧬 {imageFile ? imageFile.name : "Upload MRI Image (.png / .jpg)"}
          </label>

          {/* 🚀 Predict Button */}
          <button
            type="submit"
            className="modern-predict-btn"
            disabled={loading || (!audioFile && !imageFile)}
          >
            {loading ? "Processing..." : "🚀 Predict Parkinson’s"}
          </button>
        </form>

        {error && <p className="error-message">{error}</p>}
      </div>
    </div>
  );
}
