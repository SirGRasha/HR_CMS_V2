from django.urls import path

from apps.accounts.views import MeAPIView


urlpatterns = [
    path("me/", MeAPIView.as_view(), name="me"),
]