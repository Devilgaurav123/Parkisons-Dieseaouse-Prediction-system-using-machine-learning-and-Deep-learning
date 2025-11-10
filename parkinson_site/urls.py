# parkinson_site/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Add these two includes
    path('api/auth/', include('accounts.urls')),
    path('api/predictor/', include('predictor.urls')),
]
