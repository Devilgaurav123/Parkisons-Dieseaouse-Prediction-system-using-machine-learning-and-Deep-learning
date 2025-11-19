import os
import tempfile
import uuid
from datetime import datetime
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from PIL import Image

from .serializers import PredictSerializer
from . import utils

# Ensure media folder exists
os.makedirs(getattr(settings, "MEDIA_ROOT", "media"), exist_ok=True)

class PredictAPIView(APIView):
    """
    Main prediction endpoint.
    Accepts either multipart POST (with audio_file/image_file)
    or JSON (for testing).
    Flags:
      - use_audio (bool)
      - use_image (bool)
      - combine_features (bool)
      - return_spectrogram (bool)
      - return_heatmap (bool)
      - generate_report (bool)
    """
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, format=None):
        # Handle JSON-only test mode
        if request.content_type == "application/json":
            return Response({
                "message": "✅ JSON mode active — please upload multipart/form-data for real predictions.",
                "received_data": request.data
            }, status=status.HTTP_200_OK)

        serializer = PredictSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extract flags and data
        use_audio = serializer.validated_data.get("use_audio", True)
        use_image = serializer.validated_data.get("use_image", False)
        combine_features = serializer.validated_data.get("combine_features", True)
        return_spectrogram = serializer.validated_data.get("return_spectrogram", False)
        return_heatmap = serializer.validated_data.get("return_heatmap", False)
        generate_report = serializer.validated_data.get("generate_report", False)

        # User info
        name = serializer.validated_data.get("name", "Unknown")
        age = serializer.validated_data.get("age", "N/A")
        gender = serializer.validated_data.get("gender", "N/A")

        # File handling
        audio_file = serializer.validated_data.get("audio_file", None)
        image_file = serializer.validated_data.get("image_file", None)

        tmp_audio_path = None
        tmp_image_path = None
        details = {}
        audio_result = image_result = fused_result = None
        spectrogram_bytes = heatmap_bytes = None
        report_url = None

        try:
            # --- AUDIO PREDICTION ---
            if use_audio and audio_file:
                tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                tmp_audio.write(audio_file.read())
                tmp_audio.close()
                tmp_audio_path = tmp_audio.name

                audio_result, audio_err = utils.predict_audio_from_file(tmp_audio_path)
                if audio_err:
                    details["audio_error"] = audio_err

            # --- IMAGE PREDICTION ---
            if use_image and image_file:
                tmp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tmp_image.write(image_file.read())
                tmp_image.close()
                tmp_image_path = tmp_image.name

                try:
                    pil = Image.open(tmp_image_path)
                    image_result, image_err = utils.predict_image_from_pil(pil)
                    if image_err:
                        details["image_error"] = image_err
                except Exception as e:
                    details["image_error"] = f"Cannot open image: {str(e)}"

            # --- FUSION ---
            if combine_features and tmp_audio_path and tmp_image_path:
                fused_result, fused_err = utils.predict_fused(tmp_audio_path, tmp_image_path)
                if fused_err:
                    details["fusion_error"] = fused_err

            # --- OPTIONAL SPECTROGRAM ---
            if return_spectrogram and tmp_audio_path:
                try:
                    spectrogram_bytes = utils.audio_spectrogram_bytes(tmp_audio_path)
                except Exception as e:
                    details["spectrogram_error"] = str(e)

            # --- OPTIONAL HEATMAP ---
            if return_heatmap and tmp_image_path:
                try:
                    heatmap_bytes = utils.image_gradcam_bytes(tmp_image_path)
                except Exception as e:
                    details["heatmap_error"] = str(e)

            # --- FINAL DECISION ---
            final_label = None
            final_confidence = None
            fusion_used = False

            if fused_result is not None:
                fusion_used = True
                final_label = int(fused_result.get("label", 0))
                final_confidence = fused_result.get("probability")
            else:
                if audio_result and image_result:
                    a_label = int(audio_result.get("label", 0))
                    i_label = int(image_result.get("label", 0))
                    final_label = 1 if (a_label == 1 or i_label == 1) else 0
                    probs = [p.get("probability") for p in (audio_result, image_result)
                             if p.get("probability") is not None]
                    final_confidence = max(probs) if probs else None
                elif audio_result:
                    final_label = int(audio_result.get("label", 0))
                    final_confidence = audio_result.get("probability")
                elif image_result:
                    final_label = int(image_result.get("label", 0))
                    final_confidence = image_result.get("probability")
                else:
                    return Response({"error": "No valid prediction", "details": details},
                                    status=status.HTTP_400_BAD_REQUEST)

            resp = {
                "result": "Parkinsons" if int(final_label) == 1 else "No Parkinsons",
                "final_label": int(final_label),
                "final_confidence": float(final_confidence) if final_confidence is not None else None,
                "fusion_used": fusion_used,
                "audio_prediction": audio_result,
                "image_prediction": image_result,
                "fused_prediction": fused_result,
                "details": details,
            }

            # --- REPORT GENERATION ---
            if generate_report:
                try:
                    user_info = {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    pdf_bytes = utils.generate_pdf_report(
                        prediction=resp,
                        spectrogram_bytes=spectrogram_bytes,
                        heatmap_bytes=heatmap_bytes,
                        user_info=user_info   # ✅ Pass user info
                    )

                    filename = f"parkinson_report_{uuid.uuid4().hex}.pdf"
                    media_root = getattr(settings, "MEDIA_ROOT", "media")
                    os.makedirs(media_root, exist_ok=True)
                    file_path = os.path.join(media_root, filename)

                    with open(file_path, "wb") as f:
                        f.write(pdf_bytes)

                    # ✅ Correct download link
                    report_url = request.build_absolute_uri(
                        f"/api/predictor/download/{filename}/"
                    )
                    resp["report_url"] = report_url
                except Exception as e:
                    resp["report_error"] = str(e)

            return Response(resp, status=status.HTTP_200_OK)

        finally:
            # Clean up temporary files
            for p in (tmp_audio_path, tmp_image_path):
                try:
                    if p and os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass


class SpectrogramAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        audio_file = request.FILES.get("audio_file", None)
        if not audio_file:
            return Response({"error": "audio_file required"}, status=status.HTTP_400_BAD_REQUEST)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        tmp.write(audio_file.read())
        tmp.close()
        try:
            b = utils.audio_spectrogram_bytes(tmp.name)
            return HttpResponse(b, content_type="image/png")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            try:
                os.remove(tmp.name)
            except Exception:
                pass

class ReportAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = PredictSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid input", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        use_audio = serializer.validated_data.get("use_audio", True)
        use_image = serializer.validated_data.get("use_image", False)
        audio_file = serializer.validated_data.get("audio_file", None)
        image_file = serializer.validated_data.get("image_file", None)

        tmp_audio_path = tmp_image_path = None

        try:
            spectrogram_bytes = heatmap_bytes = None
            details = {}
            audio_result = image_result = fused_result = None

            # --- AUDIO PREDICTION ---
            if use_audio and audio_file:
                tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                tmp_audio.write(audio_file.read())
                tmp_audio.close()
                tmp_audio_path = tmp_audio.name
                audio_result, audio_err = utils.predict_audio_from_file(tmp_audio_path)
                if audio_err:
                    details["audio_error"] = audio_err
                try:
                    spectrogram_bytes = utils.audio_spectrogram_bytes(tmp_audio_path)
                except Exception:
                    spectrogram_bytes = None

            # --- IMAGE PREDICTION ---
            if use_image and image_file:
                tmp_image = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tmp_image.write(image_file.read())
                tmp_image.close()
                tmp_image_path = tmp_image.name
                try:
                    pil = Image.open(tmp_image_path)
                    image_result, image_err = utils.predict_image_from_pil(pil)
                    if image_err:
                        details["image_error"] = image_err
                    try:
                        heatmap_bytes = utils.image_gradcam_bytes(tmp_image_path)
                    except Exception:
                        heatmap_bytes = None
                except Exception as e:
                    details["image_error"] = f"Cannot open image: {str(e)}"

            # --- FUSED PREDICTION ---
            if tmp_audio_path and tmp_image_path:
                fused_result, fused_err = utils.predict_fused(tmp_audio_path, tmp_image_path)
                if fused_err:
                    details["fusion_error"] = fused_err

            # --- FINAL LABEL & CONFIDENCE ---
            final_confidence = 0.0
            final_label = 0
            borderline_flag = False

            # Compute final confidence using max probability across all available predictions
            probs = []
            if fused_result and "probability" in fused_result:
                probs.append(fused_result["probability"])
            if audio_result and "probability" in audio_result:
                probs.append(audio_result["probability"])
            if image_result and "probability" in image_result:
                probs.append(image_result["probability"])

            if probs:
                final_confidence = max(probs)
            else:
                final_confidence = 0.0

            # Threshold logic
            THRESHOLD = 0.5
            BORDERLINE_LOWER = 0.45  # optional for borderline detection
            if final_confidence >= THRESHOLD:
                final_label = 1
            elif final_confidence >= BORDERLINE_LOWER:
                final_label = 0
                borderline_flag = True
            else:
                final_label = 0

            # --- DEBUG LOGS ---
            print("=== DEBUG PREDICTION ===")
            print("Audio result:", audio_result)
            print("Image result:", image_result)
            print("Fused result:", fused_result)
            print("Final confidence:", final_confidence)
            print("Final label:", final_label)
            print("Borderline:", borderline_flag)
            print("========================\n")

            resp = {
                "result": "Parkinsons" if final_label == 1 else "No Parkinsons",
                "final_label": final_label,
                "final_confidence": float(final_confidence),
                "borderline": borderline_flag,
                "audio_prediction": audio_result,
                "image_prediction": image_result,
                "fused_prediction": fused_result,
                "details": details,
            }

            # --- GENERATE PDF REPORT ---
            pdf_bytes = utils.generate_pdf_report(
                prediction=resp,
                spectrogram_bytes=spectrogram_bytes,
                heatmap_bytes=heatmap_bytes
            )

            # Save PDF to media folder
            media_root = getattr(settings, "MEDIA_ROOT", "media")
            os.makedirs(media_root, exist_ok=True)
            filename = f"parkinson_report_{tempfile.mktemp()[-8:]}.pdf"
            file_path = os.path.join(media_root, filename)
            with open(file_path, "wb") as f:
                f.write(pdf_bytes)

            resp["report_file"] = filename
            resp["report_url"] = request.build_absolute_uri(f"/api/predictor/download/{filename}/")

            return Response(resp, status=status.HTTP_200_OK)

        finally:
            # Cleanup temporary files
            for p in (tmp_audio_path, tmp_image_path):
                try:
                    if p and os.path.exists(p):
                        os.remove(p)
                except Exception:
                    pass


class DownloadReportView(APIView):
    """
    Download previously generated report from MEDIA_ROOT
    """
    def get(self, request, filename):
        media_root = getattr(settings, "MEDIA_ROOT", "media")
        file_path = os.path.join(media_root, filename)
        if not os.path.exists(file_path):
            raise Http404("Report not found.")
        return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)