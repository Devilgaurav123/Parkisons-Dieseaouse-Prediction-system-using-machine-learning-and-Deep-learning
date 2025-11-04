import React from "react";
import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <p>© {new Date().getFullYear()} NeuroPredict — Parkinson’s Detection System</p>
      <p>Developed with Django REST Framework & React</p>
    </footer>
  );
}

export default Footer;
