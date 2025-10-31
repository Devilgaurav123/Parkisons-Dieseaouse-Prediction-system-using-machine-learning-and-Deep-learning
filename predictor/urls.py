# predictor/urls.py
from django.urls import path
from .views import PredictAPIView, SpectrogramAPIView, ReportAPIView, DownloadReportView

urlpatterns = [
    path('predict/', PredictAPIView.as_view(), name='predict'),
    path('spectrogram/', SpectrogramAPIView.as_view(), name='spectrogram'),
    path('report/', ReportAPIView.as_view(), name='report'),
    path('download/<str:filename>/', DownloadReportView.as_view(), name='download-report'),  # ✅ added
]
