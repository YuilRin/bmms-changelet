from django.urls import path
from . import views

urlpatterns = [
    path('normalize/', views.normalize_view, name='normalize'),
    path('validate/', views.validate_view, name='validate'),
    path('convert/', views.convert_view, name='convert'),
]
