import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";
import { predictParkinsons, getSpectrogram } from "../api";

export default function Upload() {
  const [audioFile, setAudioFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleAudioChange = (e) => {
    setAudioFile(e.target.files[0]);
  };

  const handleImageChange = (e) => {
    setImageFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!audioFile && !imageFile) {
      setError("⚠️ Please upload at least one file (audio or image).");
      return;
    }

    setLoading(true);
    setError("");

    const formData = new FormData();
    if (audioFile) formData.append("audio_file", audioFile);
    if (imageFile) formData.append("image_file", imageFile);
    formData.append("use_audio", !!audioFile);
    formData.append("use_image", !!imageFile);
    formData.append("combine_features", true);
    formData.append("return_spectrogram", true);
    formData.append("return_heatmap", true);
    formData.append("generate_report", true);

    try {
      if (audioFile) {
        await getSpectrogram(formData);
      }

      const prediction = await predictParkinsons(formData);
      localStorage.setItem("latest_result", JSON.stringify(prediction));
      navigate("/results");
    } catch (err) {
      console.error("❌ Upload error:", err);
      setError("❌ Failed to connect to backend. Please check your server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-card">
        <h2 className="upload-title">🧠 Upload Data for Prediction</h2>
        <p className="upload-subtitle">
          Upload your <strong>voice sample (.wav)</strong> or{" "}
          <strong>MRI image (.jpg / .png)</strong> to get AI-based predictions.
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
