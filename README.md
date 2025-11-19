# Parkinson’s Disease Prediction System using Machine Learning and Deep Learning

## Overview
This project is an AI-powered web application that predicts Parkinson’s Disease (PD) using **voice samples** and/or **MRI brain images**. It leverages machine learning and deep learning models to analyze patient data, provide predictions, and generate downloadable PDF reports with prediction results, confidence scores, and visualizations like spectrograms and heatmaps.

---

## Features
- Predict Parkinson’s Disease from **voice/audio samples**.
- Predict Parkinson’s Disease from **MRI images**.
- **Fused prediction** combining both audio and image modalities for higher accuracy.
- Generate **PDF report** including:
  - Prediction result
  - Confidence score
  - Spectrogram of audio
  - MRI heatmap
  - User info and test date
- View latest prediction results on the web frontend.
- Download generated reports securely.
- User authentication with JWT tokens.

---

## Tech Stack

### Backend
- **Django** + Django REST Framework (DRF)
- **Python** for model inference and data processing
- **Parselmouth** for audio feature extraction
- **TensorFlow / Keras** for deep learning image prediction
- **scikit-learn** for machine learning audio models
- **ReportLab** for PDF report generation
- **Pillow (PIL)** for image handling

### Frontend
- **React.js** for interactive UI
- **Axios** for API calls
- Responsive design with CSS

### Others
- **PostgreSQL** (optional) or any database for storing user info and results
- JWT for secure authentication
- `localStorage` for storing latest results

POST /api/predictor/predict/
- Accepts multipart form data (audio and/or image files).
- Flags:
  - `use_audio` (bool)
  - `use_image` (bool)
  - `combine_features` (bool)
  - `return_spectrogram` (bool)
  - `return_heatmap` (bool)
  - `generate_report` (bool)
- Returns JSON:
```json
{
  "result": "Parkinsons",
  "final_label": 1,
  "final_confidence": 0.562,
  "fusion_used": true,
  "audio_prediction": {"label": 0, "probability": 0.49},
  "image_prediction": {"label": 1, "probability": 0.63},
  "fused_prediction": {"label": 1, "probability": 0.562},
  "details": {},
  "report_file": "parkinson_report_123abc.pdf",
  "report_url": "http://127.0.0.1:8000/api/predictor/download/parkinson_report_123abc.pdf/"
}

Download Report
GET /api/predictor/download/<filename>/

Installation
Backend
# Clone repository
git clone https://github.com/Devilgaurav123/Parkisons-Dieseaouse-Prediction-system-using-machine-learning-and-Deep-learning.git
cd parkinson_site

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Migrate database (if using)
python manage.py migrate

# Run server
python manage.py runserver

Frontend
cd frontend
npm install
npm start

Usage

Open the React frontend in your browser (usually http://localhost:3000).

Upload a voice sample (.wav) and/or MRI image (.png/.jpg).

Click Predict Parkinson’s.

View the prediction results and confidence.

Download the generated PDF report.

Notes:
The system uses threshold-based labeling:
probability >= 0.5 → Parkinsons detected
probability < 0.5 → No Parkinsons
Probabilities are dynamically calculated from audio, image, or fused features.
Ensure that audio files are clear and MRI images are properly formatted.

License

This project is licensed under the MIT License.


This README covers:

- Project overview and purpose  
- Features  
- Tech stack  
- Folder structure  
- API endpoints with example JSON response  
- Installation & usage instructions  
- Notes on prediction logic  

