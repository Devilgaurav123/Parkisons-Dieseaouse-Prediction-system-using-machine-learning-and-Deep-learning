import React, { useEffect } from "react";
import "../App.css";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const navigate = useNavigate();

  // ✅ Redirect to login if user is not authenticated
  useEffect(() => {
    const token = localStorage.getItem("access");
    if (!token) {
      navigate("/login");
    }
  }, [navigate]);

  // ✅ Handles navigation with authentication check
  const handleStartPrediction = () => {
    const token = localStorage.getItem("access");
    if (token) {
      navigate("/upload");
    } else {
      navigate("/login");
    }
  };

  return (
    <div className="home-container">
      <header className="hero-section">
        <h1 className="hero-title">🧠 Parkinson’s Prediction System</h1>
        <p className="hero-subtitle">
          Empowering early detection of Parkinson’s Disease through advanced AI-driven
          analysis of voice and MRI data — bringing accuracy, speed, and confidence
          to both patients and healthcare providers.
        </p>
        <button className="cta-btn" onClick={handleStartPrediction}>
          🚀 Start Prediction
        </button>
      </header>

      <section className="about-disease">
        <h2>🧩 Understanding Parkinson’s Disease</h2>
        <p>
          Parkinson’s Disease is a progressive neurological disorder that affects movement,
          speech, and cognitive abilities. Early symptoms can be subtle — such as changes in
          voice tone, tremors, or slowed movements — often making diagnosis challenging.
          Early detection plays a crucial role in improving quality of life, enabling timely
          medical interventions, and slowing disease progression.
        </p>
      </section>

      <section className="features-section">
        <h2>💡 What Makes Our System Different?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>🎤 Advanced Voice Biomarker Analysis</h3>
            <p>
              Our model detects subtle vocal variations that even trained professionals may
              overlook, providing a non-invasive and reliable detection method.
            </p>
          </div>
          <div className="feature-card">
            <h3>🧬 MRI-Based Brain Pattern Recognition</h3>
            <p>
              Using advanced neural interpretation, our system identifies microscopic brain
              pattern differences linked to Parkinson’s with high confidence.
            </p>
          </div>
          <div className="feature-card">
            <h3>📊 Detailed Diagnostic Insights</h3>
            <p>
              Get visual results like spectrograms and heatmaps that make the diagnosis process
              transparent, interpretable, and easy for doctors to validate.
            </p>
          </div>
          <div className="feature-card">
            <h3>⚡ Fast, Accessible, and User-Friendly</h3>
            <p>
              Designed for both researchers and healthcare professionals, the system delivers
              predictions in seconds — securely and effortlessly.
            </p>
          </div>
        </div>
      </section>

      <section className="impact-section">
        <h2>🌍 Our Mission</h2>
        <p>
          We aim to make early Parkinson’s detection accessible to everyone by combining
          medical expertise and AI intelligence. Our system assists doctors in identifying
          early warning signs, empowering patients to take proactive steps toward managing
          their health effectively and confidently.
        </p>
      </section>

      <section className="cta-section">
        <h2>🧠 Take the First Step Toward Early Detection</h2>
        <p>
          Early intervention can make a life-changing difference. Upload your voice or MRI data
          and let our intelligent system assist you in identifying early signs of Parkinson’s.
        </p>
        <button className="cta-btn" onClick={handleStartPrediction}>
          Upload Data Now
        </button>
      </section>
    </div>
  );
};

export default Home;
