from django.urls import include, path
from contracts import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("api/", include("contracts.urls")),
    path("api/auth/refresh/", TokenRefreshView.as_view()),
    path("public/sign/<str:token>/", views.public_signing),
    path("public/sign/<str:token>/verify/", views.verify_signature),
    path("public/sign/<str:token>/sign/", views.sign),
    path("webhooks/pix/", views.pix_webhook),
]
