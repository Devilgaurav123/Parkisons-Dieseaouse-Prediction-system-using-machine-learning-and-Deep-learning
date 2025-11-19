import React, { useEffect, useState } from "react";
import "../App.css";
import { fetchResults } from "../api";
import axios from "axios";

const Results = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const loadResults = async () => {
      try {
        const storedResult = localStorage.getItem("latest_result");
        if (storedResult && storedResult !== "undefined" && storedResult !== "null") {
          setResult(JSON.parse(storedResult));
        } else {
          const data = await fetchResults();
          setResult(data && data.length ? data[data.length - 1] : null);
        }
      } catch (err) {
        console.error("❌ Error loading results:", err);
        setError("⚠️ Failed to fetch prediction results.");
      } finally {
        setLoading(false);
      }
    };
    loadResults();
  }, []);

  const handleDownload = async () => {
    if (!result || !result.report_url) return;

    setDownloading(true);

    try {
      const token = localStorage.getItem("access");
      if (!token) throw new Error("No access token found. Please log in.");

      const response = await axios.get(result.report_url, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "Parkinsons_Report.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error(err);
      alert("Failed to download report. Make sure you are logged in.");
    } finally {
      setDownloading(false);
    }
  };

  if (loading)
    return (
      <div className="center-wrapper">
        <p className="loading">⏳ Fetching your prediction result...</p>
      </div>
    );

  if (error)
    return (
      <div className="center-wrapper">
        <div className="result-card-modern">
          <h2 className="result-title">Prediction Result</h2>
          <p className="error-message">{error}</p>
        </div>
      </div>
    );

  if (!result)
    return (
      <div className="center-wrapper">
        <div className="result-card-modern">
          <h2 className="result-title">Prediction Result</h2>
          <p>No prediction found. Please upload your data first.</p>
        </div>
      </div>
    );

  const CONFIDENCE = result.final_confidence || 0;
  const isParkinsons = result.final_label === 1;

  // Borderline warning: probability between 0.4 and 0.5
  const borderline = !isParkinsons && CONFIDENCE >= 0.4 && CONFIDENCE < 0.5;

  return (
    <div className="center-wrapper">
      <div className="result-card-modern">
        <h2 className="result-title">🧠 Prediction Result</h2>

        <div className="result-status">
          {isParkinsons ? (
            <h3 className="result-bad">⚠️ Parkinson’s Detected</h3>
          ) : borderline ? (
            <h3 className="result-warning">
              ⚠️ Borderline prediction — Parkinson’s might be present
            </h3>
          ) : (
            <h3 className="result-good">✅ Healthy — No Parkinson’s Detected</h3>
          )}
        </div>

        <p>
          <strong>Confidence:</strong> {CONFIDENCE ? `${(CONFIDENCE * 100).toFixed(2)}%` : "N/A"}
        </p>

        {result.user && (
          <div className="user-info">
            <h4>👤 Patient Information</h4>
            <p><strong>Name:</strong> {result.user.full_name || "N/A"}</p>
            <p><strong>Email:</strong> {result.user.email || "N/A"}</p>
            <p><strong>Phone:</strong> {result.user.phone || "N/A"}</p>
          </div>
        )}

        {(result.spectrogram_base64 || result.heatmap_base64) && (
          <div className="image-wrapper">
            {result.spectrogram_base64 && (
              <div className="image-preview">
                <h4>🎵 Spectrogram</h4>
                <img
                  src={`data:image/png;base64,${result.spectrogram_base64}`}
                  alt="Spectrogram"
                />
              </div>
            )}
            {result.heatmap_base64 && (
              <div className="image-preview">
                <h4>🧬 MRI Heatmap</h4>
                <img
                  src={`data:image/png;base64,${result.heatmap_base64}`}
                  alt="MRI Heatmap"
                />
              </div>
            )}
          </div>
        )}

        <button
          className="download-report-btn"
          onClick={handleDownload}
          disabled={downloading}
        >
          {downloading ? "Downloading..." : "📄 Download Prediction Report"}
        </button>
      </div>
    </div>
  );
};

export default Results;
