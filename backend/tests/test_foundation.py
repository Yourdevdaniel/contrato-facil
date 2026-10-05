import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_healthcheck_and_authentication_flow():
    client = APIClient()
    health = client.get("/api/health/")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    registration = client.post(
        "/api/auth/register/",
        {
            "name": "Ana Souza",
            "email": "ana@example.com",
            "password": "senha-segura-123",
            "cpf_cnpj": "12345678901",
            "phone": "11999999999",
        },
        format="json",
    )
    assert registration.status_code == 201
    assert registration.json()["user"]["email"] == "ana@example.com"
    assert registration.json()["access"]

    login = client.post(
        "/api/auth/login/",
        {"email": "ana@example.com", "password": "senha-segura-123"},
        format="json",
    )
    assert login.status_code == 200
    assert login.json()["access"]
