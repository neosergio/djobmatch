from __future__ import annotations

from django.urls import path

from config.api import api

urlpatterns = [
    path("api/", api.urls),
]
