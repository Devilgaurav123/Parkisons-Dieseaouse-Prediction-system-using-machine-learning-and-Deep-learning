import React from "react";
import "../App.css";

const About = () => {
  return (
    <div className="about-container">
      <header className="about-hero">
        <h1>💡 About Parkinson’s Prediction System</h1>
        <p>
          Our mission is to revolutionize early detection of Parkinson’s Disease using
          AI and medical insight for accessible, reliable diagnostics.
        </p>
      </header>

      <section className="about-section">
        <h2>🧠 Why Early Detection Matters</h2>
        <p>
          Early detection of Parkinson’s can significantly improve patient outcomes.
          This system leverages subtle voice and MRI biomarkers for accurate prediction.
        </p>
      </section>

      <section className="about-section alt">
        <h2>🌍 Our Vision</h2>
        <p>
          We aim to make AI-based diagnostics transparent and accessible, empowering
          both patients and healthcare providers.
        </p>
      </section>

      <section className="about-section">
        <h2>💬 What Makes This System Unique</h2>
        <ul className="about-list">
          <li>✅ Uses both voice and MRI data for diagnosis.</li>
          <li>✅ Offers spectrogram and heatmap visualization.</li>
          <li>✅ Generates downloadable medical reports.</li>
          <li>✅ Delivers near real-time predictions.</li>
        </ul>
      </section>

      <section className="about-section final-cta">
        <h2>🚀 Join Us</h2>
        <p>
          Start your prediction now and be part of a future where early Parkinson’s
          detection is accessible to everyone.
        </p>
        <button
          className="cta-btn"
          onClick={() => (window.location.href = "/upload")}
        >
          Start Your Prediction →
        </button>
      </section>
    </div>
  );
};

export default About;
