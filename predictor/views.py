import os
import tempfile
import uuid
from datetime import datetime
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated  # Add this line
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from PIL import Image

from .serializers import PredictSerializer
from . import utils

# Ensure media folder exists
os.makedirs(getattr(settings, "MEDIA_ROOT", "media"), exist_ok=True)

class PredictAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request, format=None):
        user = request.user  # Fetch logged-in user from the request

        # Fetch user details from the logged-in user
        name = user.full_name if hasattr(user, 'full_name') else "Unknown"
        phone = user.phone if hasattr(user, 'phone') else "N/A"
        email = user.email if hasattr(user, 'email') else "N/A"
       

        # Extract prediction flags
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
        generate_report = serializer.validated_data.get("generate_report", False)

        tmp_audio_path = tmp_image_path = None
        details = {}
        audio_result = image_result = fused_result = None
        spectrogram_bytes = heatmap_bytes = None

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
            if use_image and use_audio:
                fused_result, fused_err = utils.predict_fused(tmp_audio_path, tmp_image_path)
                if fused_err:
                    details["fusion_error"] = fused_err

            # --- FINAL LABEL & CONFIDENCE ---
            final_confidence = 0.0
            if fused_result:
                final_label = fused_result.get("label", 0)
                final_confidence = fused_result.get("probability", 0.0)
            else:
                if audio_result:
                    final_label = audio_result.get("label", 0)
                    final_confidence = audio_result.get("probability", 0.0)
                if image_result:
                    final_label = image_result.get("label", 0)
                    final_confidence = image_result.get("probability", 0.0)

            # --- DEBUGGING LOGS ---
            print("=== DEBUG PREDICTION ===")
            print("Audio result:", audio_result)
            print("Image result:", image_result)
            print("Fused result:", fused_result)
            print("Final confidence:", final_confidence)
            print("Final label:", final_label)
            print("========================\n")

            resp = {
                "result": "Parkinsons" if int(final_label) == 1 else "No Parkinsons",
                "final_label": int(final_label),
                "final_confidence": float(final_confidence) if final_confidence is not None else None,
                "fusion_used": False,  # update if fusion is used
                "audio_prediction": audio_result,
                "image_prediction": image_result,
                "fused_prediction": fused_result,
                "details": details,
            }

            # --- REPORT GENERATION ---
            if generate_report:
                try:
                    # Prepare user info from the database (from logged-in user)
                    user_info = {
                        "name": name,
                        "phone": phone,
                        "email": email,
                        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    pdf_bytes = utils.generate_pdf_report(
                        prediction=resp,
                        spectrogram_bytes=spectrogram_bytes,
                        heatmap_bytes=heatmap_bytes,
                        user_info=user_info   # Pass user info here
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
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        user = request.user  # Fetch logged-in user from the request

        # Fetch user details
        name = user.full_name if hasattr(user, 'full_name') else "Unknown"
        phone = user.phone if hasattr(user, 'phone') else "N/A"
        email = user.email if hasattr(user, 'email') else "N/A"

        # Extract prediction flags
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
        generate_report = serializer.validated_data.get("generate_report", False)

        tmp_audio_path = tmp_image_path = None
        details = {}
        audio_result = image_result = fused_result = None
        spectrogram_bytes = heatmap_bytes = None

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
            if use_image and use_audio:
                fused_result, fused_err = utils.predict_fused(tmp_audio_path, tmp_image_path)
                if fused_err:
                    details["fusion_error"] = fused_err

            # --- FINAL LABEL & CONFIDENCE ---
            final_confidence = 0.0
            if fused_result:
                final_label = fused_result.get("label", 0)
                final_confidence = fused_result.get("probability", 0.0)
            else:
                if audio_result:
                    final_label = audio_result.get("label", 0)
                    final_confidence = audio_result.get("probability", 0.0)
                if image_result:
                    final_label = image_result.get("label", 0)
                    final_confidence = image_result.get("probability", 0.0)

            # --- DEBUGGING LOGS ---
            print("=== DEBUG PREDICTION ===")
            print("Audio result:", audio_result)
            print("Image result:", image_result)
            print("Fused result:", fused_result)
            print("Final confidence:", final_confidence)
            print("Final label:", final_label)
            print("========================\n")

            resp = {
                "result": "Parkinsons" if int(final_label) == 1 else "No Parkinsons",
                "final_label": int(final_label),
                "final_confidence": float(final_confidence) if final_confidence is not None else None,
                "fusion_used": False,  # update if fusion is used
                "audio_prediction": audio_result,
                "image_prediction": image_result,
                "fused_prediction": fused_result,
                "details": details,
            }

            # --- REPORT GENERATION ---
            if generate_report:
                try:
                    # Prepare user info from the database (from logged-in user)
                    user_info = {
                        "name": name,  # You can add age if it is available
                        "phone": phone,
                        "email": email,
                        "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }

                    pdf_bytes = utils.generate_pdf_report(
                        prediction=resp,
                        spectrogram_bytes=spectrogram_bytes,
                        heatmap_bytes=heatmap_bytes,
                        user_info=user_info   # Pass user info here
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