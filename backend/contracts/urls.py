from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health),
    path("auth/register/", views.register),
    path("auth/login/", views.login),
    path("templates/", views.templates),
    path("templates/<int:template_id>/questions/", views.template_questions),
    path("contracts/", views.contracts),
    path("contracts/<int:contract_id>/", views.contract_detail),
    path("contracts/<int:contract_id>/send/", views.send_contract),
    path("contracts/<int:contract_id>/audit/", views.audit),
    path("contracts/<int:contract_id>/pdf/", views.contract_pdf),
]
