import React from "react";
import "../App.css";

const Results = () => {
  return (
    <div className="page-container">
      <h1 className="page-title">Prediction Results</h1>

      <div className="result-container">
        <div className="result-card">
          <h2>🧠 No Prediction Yet</h2>
          <p>
            Please upload your audio or MRI data from the{" "}
            <strong>Upload</strong> page to get a result.
          </p>

          <div className="image-section">
            <img
              src="https://via.placeholder.com/400x250.png?text=No+Result+Available"
              alt="No result yet"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Results;
