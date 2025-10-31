from django.db import models

class ParkinsonPrediction(models.Model):   # ✅ Correct class name
    uploaded_at = models.DateTimeField(auto_now_add=True)
    prediction_type = models.CharField(max_length=50)  # 'audio' or 'image'
    result = models.CharField(max_length=50)           # 'Positive' or 'Negative'
    probability = models.FloatField(null=True, blank=True)
    file_path = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.prediction_type} - {self.result} ({self.uploaded_at})"
