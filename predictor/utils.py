import matplotlib
matplotlib.use("Agg")  # ✅ must be the first Matplotlib-related line!

import os
import io
import uuid
import base64
import joblib
import numpy as np
import librosa
import logging
import parselmouth
import matplotlib.pyplot as plt
import librosa.display
from sklearn.preprocessing import StandardScaler
from parselmouth.praat import call
from PIL import Image
from tensorflow.keras.models import load_model as keras_load_model
from tensorflow.keras.preprocessing import image as keras_image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ============================================================
# LOGGER SETUP
# ============================================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_audio_model = None
_scaler = None
_image_model = None
_fusion_model = None


# ============================================================
# MODEL LOADERS
# ============================================================
def load_audio_model(path=None):
    global _audio_model
    if _audio_model is None:
        path = path or os.path.join(BASE_DIR, "parkinsons_model.pkl")
        if os.path.exists(path):
            _audio_model = joblib.load(path)
            logger.info(f"Audio model loaded from {path}")
        else:
            logger.warning(f"Audio model not found at {path}")
    return _audio_model


def load_scaler(path=None):
    global _scaler
    if _scaler is None:
        path = path or os.path.join(BASE_DIR, "scaler.pkl")
        if os.path.exists(path):
            _scaler = joblib.load(path)
            logger.info(f"Scaler loaded from {path}")
        else:
            logger.warning(f"Scaler not found at {path}")
    return _scaler


def load_image_model(path=None):
    global _image_model
    if _image_model is None:
        path = path or os.path.join(BASE_DIR, "image_model.h5")
        if os.path.exists(path):
            _image_model = keras_load_model(path)
            logger.info(f"Image model loaded from {path}")
        else:
            logger.warning(f"Image model not found at {path}")
    return _image_model


def load_fusion_model(path=None):
    global _fusion_model
    if _fusion_model is None:
        path = path or os.path.join(BASE_DIR, "fusion_model.h5")
        if os.path.exists(path):
            _fusion_model = keras_load_model(path)
            logger.info(f"Fusion model loaded from {path}")
        else:
            logger.warning(f"Fusion model not found at {path}")
    return _fusion_model

# ===============================
# FEATURE EXTRACTION
# ===============================
def compute_pitch_stats(sound):
    try:
        pitch = call(sound, "To Pitch", 0.0, 75, 600)
        values = pitch.selected_array["frequency"]
        values = values[values != 0]
        if len(values) == 0:
            return np.nan, np.nan, np.nan
        return float(np.mean(values)), float(np.max(values)), float(np.min(values))
    except Exception:
        return np.nan, np.nan, np.nan


def extract_parselmouth_measures(sound):
    try:
        point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)
    except Exception:
        point_process = None

    jitter_local = shimmer_local = np.nan
    hnr = nhr = np.nan

    if point_process is not None:
        try:
            jitter_local = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            shimmer_local = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        except Exception:
            pass

    try:
        harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
        hnr_val = call(harmonicity, "Get mean", 0, 0)
        hnr = float(hnr_val)
        nhr = float(10 ** (-hnr / 10.0))
    except Exception:
        pass

    return {"jitter_local": jitter_local, "shimmer_local": shimmer_local, "hnr": hnr, "nhr": nhr}


def extract_audio_features(file_path, sr=22050):
    try:
        y, sr = librosa.load(file_path, sr=sr, mono=True)
        if y.size == 0:
            return None
        sound = parselmouth.Sound(y, sampling_frequency=sr)
        fo_mean, fo_max, fo_min = compute_pitch_stats(sound)
        measures = extract_parselmouth_measures(sound)
        feature_vector = [
            fo_mean,
            fo_max,
            fo_min,
            measures.get("jitter_local", 0),
            measures.get("shimmer_local", 0),
            measures.get("hnr", 0),
            measures.get("nhr", 0),
        ]
        feature_vector += [0.0] * (40 - len(feature_vector))
        fv = np.array(feature_vector).reshape(1, -1)
        scaler = load_scaler()
        if scaler is not None:
            fv = scaler.transform(fv)
        return fv
    except Exception as e:
        logger.exception(f"Feature extraction failed: {e}")
        return np.zeros((1, 40), dtype=np.float32)

# ===============================
# PREDICTORS
# ===============================
def predict_audio_from_file(file_path):
    model = load_audio_model()
    if model is None:
        return None, "Audio model not found (parkinsons_model.pkl)"
    try:
        fv = extract_audio_features(file_path)
        pred = model.predict(fv)
        label = int(np.round(pred[0]))
        prob = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(fv)
            prob = float(probs[0][1]) if probs.shape[1] > 1 else float(probs[0][0])
        return {"label": label, "probability": prob}, None
    except Exception as e:
        logger.exception(f"Audio prediction failed: {e}")
        return None, str(e)


def predict_image_from_pil(pil_img):
    try:
        model = load_image_model()
        if model is None:
            return {"label": 0, "probability": 0.0}, None  # safer default
        img = pil_img.convert("RGB").resize((224, 224))
        arr = keras_image.img_to_array(img)
        arr = np.expand_dims(arr, axis=0) / 255.0
        pred = model.predict(arr)
        label = int(np.argmax(pred, axis=1)[0])
        prob = float(pred[0][label])
        return {"label": label, "probability": prob}, None
    except Exception as e:
        logger.exception(f"Image prediction failed: {e}")
        return None, str(e)


def predict_fused(audio_path, image_path):
    try:
        audio_res, _ = predict_audio_from_file(audio_path)
        img = Image.open(image_path)
        image_res, _ = predict_image_from_pil(img)

        # --- FIXED: use max probability across modalities ---
        a_prob = float(audio_res["probability"]) if audio_res and audio_res.get("probability") is not None else 0.0
        i_prob = float(image_res["probability"]) if image_res and image_res.get("probability") is not None else 0.0

        prob = max(a_prob, i_prob)
        label = 1 if prob >= 0.5 else 0

        return {"label": label, "probability": prob}, None
    except Exception as e:
        logger.exception(f"Fusion prediction failed: {e}")
        return None, str(e)
# ============================================================
# SPECTROGRAM GENERATION
# ============================================================
def audio_spectrogram_bytes(audio_path):
    try:
        y, sr = librosa.load(audio_path, sr=None)
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_DB = librosa.power_to_db(S, ref=np.max)
        fig, ax = plt.subplots(figsize=(6, 3))
        librosa.display.specshow(S_DB, sr=sr, x_axis="time", y_axis="mel", ax=ax)
        ax.set(title="Mel-Spectrogram")
        ax.axis("off")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        raise RuntimeError(f"Error generating spectrogram: {str(e)}")


# ============================================================
# ✅ FIXED PDF REPORT GENERATOR WITH BORDERLINE SUPPORT
# ============================================================
def generate_pdf_report(prediction, spectrogram_bytes=None, heatmap_bytes=None, user_info=None):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(50, height - 60, "🧠 Parkinson’s Disease Prediction Report")

    # User info (display name, email, and phone)
    p.setFont("Helvetica", 12)
    y = height - 100
    if user_info:
        name = user_info.get("name", "Unknown")
        email = user_info.get("email", "N/A")
        phone = user_info.get("phone", "N/A")
        test_date = user_info.get("test_date", "N/A")
        
        # Drawing user information
        p.drawString(50, y, f"Name: {name}")
        y -= 20
        p.drawString(50, y, f"Email: {email}")
        y -= 20
        p.drawString(50, y, f"Phone: {phone}")
        y -= 20
        p.drawString(50, y, f"Test Date: {test_date}")
        y -= 40  # Increased spacing after user information

    # Line separating user info from prediction result
    p.line(50, y, width - 50, y)
    y -= 20

    # Prediction result with borderline support
    p.setFont("Helvetica-Bold", 14)
    if prediction.get("final_label") == 1:
        result_text = "⚠️ Parkinson's Detected"
    elif prediction.get("borderline", False):
        result_text = "⚠️ Borderline — Parkinson’s might be present"
    else:
        result_text = "✅ No Parkinson’s"
    p.drawString(50, y, f"Prediction Result: {result_text}")
    y -= 25

    # Confidence
    p.setFont("Helvetica", 12)
    confidence = prediction.get("final_confidence")
    if confidence is not None:
        p.drawString(50, y, f"Confidence: {(confidence * 100):.2f}%")
    else:
        p.drawString(50, y, "Confidence: N/A")
    y -= 40

    # Spectrogram (if available)
    if spectrogram_bytes:
        try:
            image = ImageReader(io.BytesIO(spectrogram_bytes))
            p.drawString(50, y, "🎵 Audio Spectrogram:")
            y -= 180
            p.drawImage(image, 50, y, width=250, height=150, preserveAspectRatio=True, mask="auto")
            y -= 30
        except Exception as e:
            p.setFillColorRGB(1, 0, 0)
            p.drawString(50, y, f"[Error loading spectrogram: {str(e)}]")
            y -= 30
            p.setFillColorRGB(0, 0, 0)

    # Heatmap (if available)
    if heatmap_bytes:
        try:
            image = ImageReader(io.BytesIO(heatmap_bytes))
            p.drawString(50, y, "🧬 MRI Heatmap:")
            y -= 180
            p.drawImage(image, 320, y, width=200, height=150, preserveAspectRatio=True, mask="auto")
        except Exception as e:
            p.setFillColorRGB(1, 0, 0)
            p.drawString(50, y, f"[Error loading heatmap: {str(e)}]")
            y -= 30
            p.setFillColorRGB(0, 0, 0)

    # Finalize PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.getvalue()
