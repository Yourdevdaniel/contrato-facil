import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from tests._credentials import TEST_PASSWORD


def authenticated_client():
    client = APIClient()
    response = client.post(
        "/api/auth/register/",
        {"name": "Ana", "email": "ana@example.com", "password": TEST_PASSWORD},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")
    return client


@pytest.mark.django_db
def test_generates_contract_with_conditional_clauses():
    call_command("seed_demo")
    client = authenticated_client()
    templates = client.get("/api/templates/")
    assert templates.status_code == 200
    assert {item["slug"] for item in templates.json()} == {
        "prestacao-servicos", "freela-criativo", "aluguel-bem-movel",
        "confissao-divida", "parceria-comercial", "nda",
    }

    template = next(item for item in templates.json() if item["slug"] == "prestacao-servicos")
    questions = client.get(f"/api/templates/{template['id']}/questions/")
    assert questions.status_code == 200
    assert len(questions.json()) >= 8

    base_answers = {
        "client_name": "Loja Aurora",
        "provider_name": "Ana Souza",
        "service": "Identidade visual",
        "value": "5000.00",
        "start_date": "2026-08-01",
        "end_date": "2026-08-30",
        "payment_method": "Pix",
    }
    with_down_payment = client.post(
        "/api/contracts/",
        {"template": template["id"], "responses": {**base_answers, "has_down_payment": True, "down_payment_percent": 30}},
        format="json",
    )
    assert with_down_payment.status_code == 201
    assert "R$ 1.500,00" in with_down_payment.json()["final_body"]
    assert "sinal" in with_down_payment.json()["final_body"].lower()

    without_down_payment = client.post(
        "/api/contracts/",
        {"template": template["id"], "responses": {**base_answers, "has_down_payment": False}},
        format="json",
    )
    assert without_down_payment.status_code == 201
    assert "sinal" not in without_down_payment.json()["final_body"].lower()
    assert len(client.get("/api/contracts/").json()) == 2

    unsafe = client.patch(
        f"/api/contracts/{with_down_payment.json()['id']}/",
        {"final_body": "<section><h2>OBJETO</h2><script>alert(1)</script></section>"},
        format="json",
    )
    assert unsafe.status_code == 400
