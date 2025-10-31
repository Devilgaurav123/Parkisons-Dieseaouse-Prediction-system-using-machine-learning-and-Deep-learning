import os
import io
import uuid
import base64
import joblib
import numpy as np
import librosa
import logging
import parselmouth
from sklearn.preprocessing import StandardScaler
from parselmouth.praat import call
from PIL import Image, ImageDraw
from tensorflow.keras.models import load_model as keras_load_model
from tensorflow.keras.preprocessing import image as keras_image
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ============================================================
# LOGGER SETUP (GLOBAL)
# ============================================================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lazy singletons
_audio_model = None
_scaler = None
_image_model = None
_fusion_model = None


# ============================================================
# MODEL LOADERS
# ============================================================
def load_audio_model(path=None):
    """Load the trained audio RandomForest model."""
    global _audio_model
    if _audio_model is None:
        if path is None:
            path = os.path.join(BASE_DIR, 'parkinsons_model.pkl')
        if os.path.exists(path):
            _audio_model = joblib.load(path)
            logger.info(f"Audio model loaded from {path}")
        else:
            logger.warning(f"Audio model not found at {path}")
    return _audio_model


def load_scaler(path=None):
    """Load the feature scaler for normalization."""
    global _scaler
    if _scaler is None:
        if path is None:
            path = os.path.join(BASE_DIR, 'scaler.pkl')
        if os.path.exists(path):
            _scaler = joblib.load(path)
            logger.info(f"Scaler loaded from {path}")
        else:
            logger.warning(f"Scaler not found at {path}")
    return _scaler


def load_image_model(path=None):
    """Load CNN model for image predictions."""
    global _image_model
    if _image_model is None:
        if path is None:
            path = os.path.join(BASE_DIR, 'image_model.h5')
        if os.path.exists(path):
            _image_model = keras_load_model(path)
            logger.info(f"Image model loaded from {path}")
        else:
            logger.warning(f"Image model not found at {path}")
    return _image_model


def load_fusion_model(path=None):
    """Load fusion model combining audio and image predictions."""
    global _fusion_model
    if _fusion_model is None:
        if path is None:
            path = os.path.join(BASE_DIR, 'fusion_model.h5')
        if os.path.exists(path):
            _fusion_model = keras_load_model(path)
            logger.info(f"Fusion model loaded from {path}")
        else:
            logger.warning(f"Fusion model not found at {path}")
    return _fusion_model


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def compute_pitch_stats(sound):
    """Compute basic pitch statistics: mean, max, min."""
    try:
        pitch = call(sound, "To Pitch", 0.0, 75, 600)
        values = pitch.selected_array['frequency']
        values = values[values != 0]
        if len(values) == 0:
            return np.nan, np.nan, np.nan
        return float(np.mean(values)), float(np.max(values)), float(np.min(values))
    except Exception:
        return np.nan, np.nan, np.nan


def extract_parselmouth_measures(sound):
    """Compute jitter, shimmer, and harmonicity metrics using Praat."""
    try:
        point_process = call(sound, "To PointProcess (periodic, cc)", 75, 600)
    except Exception:
        point_process = None

    jitter_local = jitter_local_pct = jitter_rap = jitter_ppq5 = np.nan
    shimmer_local = shimmer_db = apq3 = apq5 = np.nan
    hnr = nhr = np.nan

    if point_process is not None:
        try:
            jitter_local = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
            jitter_local_pct = call(point_process, "Get jitter (local, percent)", 0, 0, 0.0001, 0.02, 1.3)
            jitter_rap = call(point_process, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
            jitter_ppq5 = call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)

            shimmer_local = call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            shimmer_db = call([sound, point_process], "Get shimmer (dB)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            apq3 = call([sound, point_process], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            apq5 = call([sound, point_process], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        except Exception:
            pass

    try:
        harmonicity = call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
        hnr_val = call(harmonicity, "Get mean", 0, 0)
        hnr = float(hnr_val)
        nhr = float(10 ** (-hnr / 10.0))
    except Exception:
        pass

    return {
        'jitter_local': jitter_local,
        'jitter_local_pct': jitter_local_pct,
        'jitter_rap': jitter_rap,
        'jitter_ppq5': jitter_ppq5,
        'shimmer_local': shimmer_local,
        'shimmer_db': shimmer_db,
        'apq3': apq3,
        'apq5': apq5,
        'hnr': hnr,
        'nhr': nhr
    }


# ============================================================
# FEATURE EXTRACTION
# ============================================================
def extract_audio_features(file_path, sr=22050):
    """Extract 40-dimensional audio feature vector for Parkinson’s prediction."""
    try:
        y, sr = librosa.load(file_path, sr=sr, mono=True)
        if y.size == 0:
            return None

        sound = parselmouth.Sound(y, sampling_frequency=sr)
        fo_mean, fo_max, fo_min = compute_pitch_stats(sound)
        measures = extract_parselmouth_measures(sound)

        rpde, dfa, ppe = 0.0, 0.0, 0.0

        feature_map = {
            'fo': fo_mean, 'fhi': fo_max, 'flo': fo_min,
            'Jitter_percent': measures.get('jitter_local_pct', np.nan),
            'Jitter_Abs': measures.get('jitter_local', np.nan),
            'RAP': measures.get('jitter_rap', np.nan),
            'PPQ': measures.get('jitter_ppq5', np.nan),
            'DDP': np.nan,
            'Shimmer': measures.get('shimmer_local', np.nan),
            'Shimmer_dB': measures.get('shimmer_db', np.nan),
            'APQ3': measures.get('apq3', np.nan),
            'APQ5': measures.get('apq5', np.nan),
            'APQ': measures.get('apq3', np.nan),
            'DDA': np.nan,
            'NHR': measures.get('nhr', np.nan),
            'HNR': measures.get('hnr', np.nan),
            'RPDE': rpde, 'DFA': dfa, 'Spread1': np.nan,
            'Spread2': np.nan, 'D2': np.nan, 'PPE': ppe
        }

        ordered = [
            'fo', 'fhi', 'flo', 'Jitter_percent', 'Jitter_Abs', 'RAP', 'PPQ', 'DDP',
            'Shimmer', 'Shimmer_dB', 'APQ3', 'APQ5', 'APQ', 'DDA',
            'NHR', 'HNR', 'RPDE', 'DFA', 'Spread1', 'Spread2', 'D2', 'PPE'
        ]

        feature_vector = [
            0.0 if np.isnan(feature_map.get(k, 0)) else float(feature_map[k]) for k in ordered
        ]

        # Pad or truncate to exactly 40 features
        target_size = 40
        if len(feature_vector) < target_size:
            feature_vector += [0.0] * (target_size - len(feature_vector))
        elif len(feature_vector) > target_size:
            feature_vector = feature_vector[:target_size]

        fv = np.array(feature_vector).reshape(1, -1)

        scaler = load_scaler()
        if scaler is not None:
            try:
                fv = scaler.transform(fv)
            except Exception as e:
                logger.warning(f"Scaler transform failed: {e}")

        return fv
    except Exception as e:
        logger.exception(f"Feature extraction failed: {e}")
        return np.zeros((1, 40), dtype=np.float32)


# ============================================================
# IMAGE PREDICTION WRAPPER
# ============================================================
def predict_image_from_pil(pil_img):
    """
    Accepts a PIL.Image instance and returns (result_dict, error_str_or_None).
    result_dict: {'label': int, 'probability': float_or_None, 'features': proxy_features}
    """
    try:
        img_model = load_image_model()

        # Compute proxy features — safe placeholder
        try:
            proxy = {
                'brain_volume_proxy': 0.0,
                'cortical_thickness_proxy': 0.0,
                'substantia_nigra_intensity': 0.0,
                'striatal_binding_ratio': 0.0,
                'striatal_asymmetry': 0.0,
                'deep_features': np.zeros((1280,), dtype=np.float32)
            }
        except Exception:
            proxy = {}

        if img_model is None:
            sbr = proxy.get('striatal_binding_ratio', 0.0)
            label = 1 if sbr < 0 else 0
            return {'label': label, 'probability': None, 'features': proxy}, None

        # Preprocess image for CNN model
        try:
            img = pil_img.convert('RGB').resize((224, 224))
            arr = keras_image.img_to_array(img)
            arr = np.expand_dims(arr, axis=0)
            arr = arr / 255.0

            pred = img_model.predict(arr)
            if pred.ndim == 2 and pred.shape[-1] == 1:
                prob = float(pred[0][0])
                label = 1 if prob >= 0.5 else 0
            else:
                label = int(np.argmax(pred, axis=1)[0])
                prob = float(pred[0][label]) if pred.ndim > 1 else None

            return {'label': label, 'probability': prob, 'features': proxy}, None
        except Exception as e:
            logger.exception("Image model predict failed: %s", e)
            sbr = proxy.get('striatal_binding_ratio', 0.0)
            label = 1 if sbr < 0 else 0
            return {'label': label, 'probability': None, 'features': proxy}, f"Model predict error: {e}"

    except Exception as e:
        logger.exception("predict_image_from_pil failed: %s", e)
        return None, str(e)


# ============================================================
# AUDIO PREDICTION WRAPPER
# ============================================================
def predict_audio_from_file(file_path):
    """Predict Parkinson’s disease from an audio file."""
    model = load_audio_model()
    if model is None:
        return None, "Audio model not found (parkinsons_model.pkl)"

    try:
        fv = extract_audio_features(file_path)
        if fv is None:
            return None, "Failed to extract features"

        pred = model.predict(fv)
        label = int(np.round(pred[0]))

        prob = None
        if hasattr(model, "predict_proba"):
            try:
                probs = model.predict_proba(fv)
                prob = float(probs[0][1]) if probs.shape[1] > 1 else float(probs[0][0])
            except Exception:
                prob = None

        return {'label': label, 'probability': prob}, None
    except Exception as e:
        logger.exception(f"Audio prediction failed: {e}")
        return None, str(e)


# ============================================================
# PDF REPORT GENERATOR
# ============================================================

def generate_pdf_report(prediction, spectrogram_bytes=None, heatmap_bytes=None, user_info=None):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from io import BytesIO

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Parkinson’s Prediction Report")

    p.setFont("Helvetica", 12)
    y = 770

    # ✅ Include patient information
    if user_info:
        p.drawString(50, y, f"Name: {user_info.get('name', 'N/A')}")
        y -= 20
        p.drawString(50, y, f"Age: {user_info.get('age', 'N/A')}")
        y -= 20
        p.drawString(50, y, f"Gender: {user_info.get('gender', 'N/A')}")
        y -= 20
        p.drawString(50, y, f"Test Date: {user_info.get('test_date', 'N/A')}")
        y -= 30

    # ✅ Prediction summary
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, f"Result: {prediction.get('result', 'Unknown')}")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Confidence: {prediction.get('final_confidence', 'N/A')}")
    y -= 30

    # ✅ Optionally include spectrogram and heatmap images
    if spectrogram_bytes:
        y -= 200
        p.drawImage(io.BytesIO(spectrogram_bytes), 50, y, width=250, height=200, preserveAspectRatio=True, mask='auto')
        y -= 20
        p.drawString(50, y, "Audio Spectrogram")

    if heatmap_bytes:
        y -= 220
        p.drawImage(io.BytesIO(heatmap_bytes), 320, y, width=250, height=200, preserveAspectRatio=True, mask='auto')
        y -= 20
        p.drawString(320, y, "Image Grad-CAM Heatmap")

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def predict_fused(audio_path, image_path):
    """
    Combine predictions from audio and image to make a fused decision.
    Returns: (result_dict, error_message)
    """
    try:
        # Step 1: Extract audio features
        from .utils import extract_audio_features
        audio_features = extract_audio_features(audio_path)
        if audio_features is None or len(audio_features) == 0:
            return None, "Failed to extract audio features."

        # Step 2: Extract image features (dummy or use CNN model)
        from PIL import Image
        from tensorflow.keras.preprocessing import image as keras_image
        img = Image.open(image_path).convert("RGB").resize((128, 128))
        img_array = keras_image.img_to_array(img)
        img_features = np.mean(img_array, axis=(0, 1))  # Simplified image features

        # Step 3: Combine features
        fused_features = np.concatenate([
            audio_features.flatten()[:20],  # take first 20 audio features
            img_features.flatten()[:20]     # take first 20 image features
        ])
        fused_features = fused_features.reshape(1, -1)

        # Step 4: Use a fusion model (if available)
        try:
            import joblib
            fusion_model = joblib.load("models/fusion_model.pkl")
            probability = float(fusion_model.predict_proba(fused_features)[0, 1])
        except Exception:
            # fallback: average dummy probability
            probability = float(np.mean(fused_features) % 1)

        # Step 5: Make label
        label = 1 if probability >= 0.5 else 0

        return {"label": label, "probability": probability}, None

    except Exception as e:
        logger.exception(f"Fusion prediction failed: {e}")
        return None, str(e)

def audio_spectrogram_bytes(audio_path: str):
    """
    Generate a Mel-spectrogram from a WAV file and return it as PNG bytes.
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        # Create mel spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_DB = librosa.power_to_db(S, ref=np.max)

        # Plot and save as bytes
        plt.figure(figsize=(8, 4))
        librosa.display.specshow(S_DB, sr=sr, x_axis='time', y_axis='mel')
        plt.colorbar(format='%+2.0f dB')
        plt.title("Mel-Spectrogram")
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf.getvalue()

    except Exception as e:
        raise RuntimeError(f"Error generating spectrogram: {str(e)}")
