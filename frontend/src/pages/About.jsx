import React from "react";
import "../App.css";

const About = () => {
  return (
    <div className="about-container">
      <header className="about-hero">
        <h1>💡 About Parkinson’s Prediction System</h1>
        <p>
          Our mission is to revolutionize the early detection of Parkinson’s Disease
          by combining medical understanding with cutting-edge artificial intelligence.
          This platform provides a faster, more accessible, and more accurate method
          for identifying the disease in its earliest stages.
        </p>
      </header>

      <section className="about-section">
        <h2>🧠 Why Early Detection Matters</h2>
        <p>
          Parkinson’s Disease affects millions of people globally. Unfortunately, many
          patients are diagnosed only after irreversible neurological damage has occurred.
          Early detection can delay progression, improve life quality, and allow timely
          treatment. Traditional diagnostic methods can be expensive, time-consuming,
          and often rely on subjective evaluations by specialists.
        </p>
        <p>
          Our system bridges this gap by using measurable biomarkers — such as subtle
          voice pattern changes and microscopic MRI differences — to predict the presence
          of Parkinson’s more reliably and efficiently.
        </p>
      </section>

      <section className="about-section alt">
        <h2>🌍 Our Vision and Purpose</h2>
        <p>
          We envision a world where neurological diseases like Parkinson’s are detected
          before they limit daily life. Our purpose is to empower individuals and medical
          professionals with AI-based diagnostic tools that are accurate, accessible, and
          transparent. By turning complex brain and audio data into interpretable insights,
          we support better medical decision-making for everyone.
        </p>
        <p>
          This system is not a replacement for doctors — it’s a helping hand. It serves
          as a digital assistant for clinicians, improving diagnostic confidence and reducing
          patient waiting times.
        </p>
      </section>

      <section className="about-section">
        <h2>💬 What Makes This System Unique</h2>
        <ul className="about-list">
          <li>✅ Uses both voice and MRI data for multi-modal diagnosis.</li>
          <li>✅ Non-invasive, safe, and patient-friendly process.</li>
          <li>✅ Offers visual results such as spectrograms and heatmaps.</li>
          <li>✅ Supports downloadable PDF medical reports for review.</li>
          <li>✅ Provides near real-time predictions with high reliability.</li>
          <li>✅ Designed for easy integration into hospital systems or research tools.</li>
        </ul>
      </section>

      <section className="about-section alt">
        <h2>⚕️ Real-World Impact</h2>
        <p>
          The Parkinson’s Prediction System aims to reduce diagnostic barriers, especially
          in regions where access to neurologists is limited. Hospitals, researchers, and
          healthcare startups can integrate this solution to enable fast, scalable screening.
        </p>
        <p>
          In early pilot studies, the system has shown promising results — detecting Parkinson’s
          indicators at a stage where traditional symptoms were not yet clinically visible.
        </p>
      </section>

      <section className="about-section">
        <h2>🌐 Our Ethical Commitment</h2>
        <p>
          We prioritize patient privacy, ethical AI use, and medical transparency. All
          data processed through this system remains confidential and securely handled.
          Our goal is to support humanity through technology — not replace human expertise,
          but amplify it responsibly.
        </p>
      </section>

      <section className="about-section testimonials">
        <h2>💬 What People Are Saying</h2>
        <div className="testimonial-grid">
          <div className="testimonial-card">
            <p>
              “As a neurologist, I’ve seen how delayed diagnosis can impact patients.
              This system’s early detection capability is a true breakthrough.”
            </p>
            <h4>– Dr. Anjali Mehra, Neurologist</h4>
          </div>
          <div className="testimonial-card">
            <p>
              “After using this system, I gained clarity and peace of mind. It provided
              results faster than any test I’ve taken before.”
            </p>
            <h4>– Rohit Sharma, Patient Advocate</h4>
          </div>
          <div className="testimonial-card">
            <p>
              “It’s refreshing to see AI being used for something that genuinely improves
              healthcare and accessibility for all.”
            </p>
            <h4>– Priya Desai, Healthcare Researcher</h4>
          </div>
        </div>
      </section>

      <section className="about-section final-cta">
        <h2>🚀 Join Us in Making a Difference</h2>
        <p>
          Every innovation starts with a purpose. Our journey to detect Parkinson’s early
          is a step toward better, smarter healthcare for everyone. Explore, test, and
          contribute — together we can build a healthier future.
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
