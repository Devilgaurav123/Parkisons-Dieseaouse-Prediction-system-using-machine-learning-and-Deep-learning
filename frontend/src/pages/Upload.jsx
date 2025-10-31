import React from "react";
import UploadForm from "../components/UploadForm";
import "../App.css";

export default function Upload() {
  return (
    <div className="page-container">
      <h2 className="page-title">Upload Data for Prediction</h2>
      <UploadForm />
    </div>
  );
}
