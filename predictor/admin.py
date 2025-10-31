from django.contrib import admin
from .models import ParkinsonPrediction   # ✅ must match the model name

@admin.register(ParkinsonPrediction)
class ParkinsonPredictionAdmin(admin.ModelAdmin):
    list_display = ('prediction_type', 'result', 'uploaded_at')
