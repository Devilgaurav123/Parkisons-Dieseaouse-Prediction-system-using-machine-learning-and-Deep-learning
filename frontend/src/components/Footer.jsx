import React from "react";
import "./Footer.css";

function Footer() {
  return (
    <footer className="footer">
      <p>© {new Date().getFullYear()} Parkinson’s Detection System</p>
      <p>Developed using Django REST & React</p>
    </footer>
  );
}

export default Footer;
