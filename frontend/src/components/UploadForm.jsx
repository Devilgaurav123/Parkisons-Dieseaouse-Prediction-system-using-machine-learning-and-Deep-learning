import React, { useState } from "react";
import "./UploadForm.css";
import { predictParkinsons } from "../api";
import ResultCard from "./ResultCard";

export default function UploadForm() {
  const [audioFile, setAudioFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [options, setOptions] = useState({
    use_audio: true,
    use_image: false,
    combine_features: true,
    return_spectrogram: true,
    return_heatmap: true,
    generate_report: true,
  });

  const handleChange = (e) => {
    setOptions({ ...options, [e.target.name]: e.target.checked });
  };

  const handleSubmit = async () => {
    if (!audioFile && !imageFile) {
      alert("Please upload at least one file!");
      return;
    }

    const formData = new FormData();
    if (audioFile) formData.append("audio_file", audioFile);
    if (imageFile) formData.append("image_file", imageFile);
    Object.entries(options).forEach(([k, v]) => formData.append(k, v));

    setLoading(true);
    try {
      const res = await predictParkinsons(formData);
      setResult(res.data);
    } catch (err) {
      console.error("Prediction error:", err);
      alert("Prediction failed. Check backend connection.");
      setResult(null); // ensure ResultCard doesn’t crash
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-form-container">
      <div className="upload-card">
        <h2>🧠 Upload MRI / Voice Data</h2>

        <div className="upload-section">
          <label className="file-upload">
            Upload Audio (.wav)
            <input
              type="file"
              accept=".wav"
              onChange={(e) => setAudioFile(e.target.files[0])}
            />
          </label>
          {audioFile && <p className="file-name">{audioFile.name}</p>}
        </div>

        <div className="upload-section">
          <label className="file-upload">
            Upload MRI Image (.png / .jpg)
            <input
              type="file"
              accept=".png,.jpg,.jpeg"
              onChange={(e) => setImageFile(e.target.files[0])}
            />
          </label>
          {imageFile && <p className="file-name">{imageFile.name}</p>}
        </div>

        <div className="options-section">
          {Object.keys(options).map((key) => (
            <label key={key} className="checkbox-label">
              <input
                type="checkbox"
                name={key}
                checked={options[key]}
                onChange={handleChange}
              />
              {key.replace(/_/g, " ")}
            </label>
          ))}
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="predict-btn"
        >
          {loading ? <div className="spinner"></div> : "🚀 Predict Parkinson’s"}
        </button>
      </div>

      {/* ✅ Safely render ResultCard */}
      <ResultCard result={result} />
    </div>
  );
}
