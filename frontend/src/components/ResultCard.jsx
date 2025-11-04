import React, { useEffect, useState } from "react";
import "../App.css";
import { fetchResults } from "../api";

const Results = () => {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadResults = async () => {
      try {
        const storedResult = localStorage.getItem("latest_result");
        if (storedResult) {
          setResult(JSON.parse(storedResult));
        } else {
          const data = await fetchResults();
          setResult(data[data.length - 1] || null);
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

  if (loading)
    return <p className="loading">⏳ Fetching your prediction result...</p>;

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

  const isParkinsons =
    result.result?.toLowerCase().includes("parkinson") ||
    result.prediction?.toLowerCase().includes("parkinson");

  const handleDownload = () => {
    if (result.report_base64) {
      const link = document.createElement("a");
      link.href = `data:application/pdf;base64,${result.report_base64}`;
      link.download = "Parkinsons_Report.pdf";
      link.click();
    } else if (result.report_url) {
      window.open(result.report_url, "_blank");
    } else {
      alert("No report available for download.");
    }
  };

  return (
    <div className="center-wrapper">
      <div className="result-card-modern">
        <h2 className="result-title">🧠 Prediction Result</h2>

        <div className="result-status">
          {isParkinsons ? (
            <h3 className="result-bad">⚠️ Parkinson’s Detected</h3>
          ) : (
            <h3 className="result-good">✅ Healthy — No Parkinson’s Detected</h3>
          )}
        </div>

        <p>
          <strong>Confidence:</strong>{" "}
          {result.final_confidence
            ? `${(result.final_confidence * 100).toFixed(2)}%`
            : "N/A"}
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

        <button className="download-report-btn" onClick={handleDownload}>
          📄 Download Prediction Report
        </button>
      </div>
    </div>
  );
};

export default Results;
