import React from "react";
import "./ResultCard.css";

export default function ResultCard({ result }) {
  // ✅ Prevent crash if `result` is null or undefined
  if (!result) {
    return (
      <div className="result-container">
        <div className="result-card empty-card">
          <h2>🧠 No Prediction Yet</h2>
          <p>Please upload your audio or MRI data to get a result.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="result-container">
      <div className="result-card">
        <h2>🧩 Prediction Result</h2>

        <p>
          <strong>Status:</strong> {result.result || "Unknown"}
        </p>
        <p>
          <strong>Confidence:</strong>{" "}
          {result.final_confidence
            ? `${(result.final_confidence * 100).toFixed(2)}%`
            : "N/A"}
        </p>

        {result.spectrogram_base64 && (
          <div className="image-section">
            <h4>🎵 Spectrogram</h4>
            <img
              src={`data:image/png;base64,${result.spectrogram_base64}`}
              alt="Spectrogram"
            />
          </div>
        )}

        {result.heatmap_base64 && (
          <div className="image-section">
            <h4>🔥 MRI Heatmap</h4>
            <img
              src={`data:image/png;base64,${result.heatmap_base64}`}
              alt="Heatmap"
            />
          </div>
        )}

        {result.report_base64 && (
          <button
            className="download-btn"
            onClick={() => {
              const link = document.createElement("a");
              link.href = `data:application/pdf;base64,${result.report_base64}`;
              link.download = "Parkinsons_Report.pdf";
              link.click();
            }}
          >
            📄 Download Report
          </button>
        )}
      </div>
    </div>
  );
}
