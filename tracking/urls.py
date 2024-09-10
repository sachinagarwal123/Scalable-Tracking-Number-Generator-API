

from django.urls import path
from .views import NextTrackingNumberView

urlpatterns = [
    path('next-tracking-number/', NextTrackingNumberView.as_view(), name='next-tracking-number')
]
