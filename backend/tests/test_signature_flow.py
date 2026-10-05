import pytest
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient
from contracts.models import Party


def create_contract(client):
    template = client.get("/api/templates/").json()[0]
    return client.post(
        "/api/contracts/",
        {"template": template["id"], "responses": {
            "client_name": "Loja Aurora", "provider_name": "Ana Souza", "service": "Site",
            "value": "1200", "start_date": "2026-08-01", "end_date": "2026-08-30",
            "payment_method": "Pix", "has_down_payment": False, "has_late_fee": True,
        }},
        format="json",
    ).json()


@pytest.mark.django_db
def test_two_party_signature_audit_pdf_and_pix_webhook():
    call_command("seed_demo")
    client = APIClient()
    auth = client.post(
        "/api/auth/register/",
        {"name": "Ana", "email": "ana@example.com", "password": "senha-segura-123"},
        format="json",
    ).json()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth['access']}")
    contract = create_contract(client)

    sent = client.post(
        f"/api/contracts/{contract['id']}/send/",
        {
            "parties": [
                {"name": "Ana Souza", "cpf_cnpj": "12345678901", "contact": "ana@example.com", "signing_order": 1},
                {"name": "Loja Aurora", "cpf_cnpj": "12345678000199", "contact": "11999999999", "signing_order": 2},
            ],
            "installments": [{"amount": "1200.00", "due_date": "2026-08-30"}],
            "message": "Pode assinar, por favor?",
        },
        format="json",
    )
    assert sent.status_code == 200
    links = sent.json()["signing_links"]
    assert len(links) == 2
    assert sent.json()["status"] == "sent"
    assert Party.objects.get(token=links[0]["token"]).verification_code != links[0]["verification_code"]

    public = APIClient()
    first = links[0]
    second = links[1]
    assert public.get(f"/public/sign/{first['token']}/").status_code == 200

    blocked = public.post(
        f"/public/sign/{second['token']}/sign/",
        {"code": second["verification_code"], "signature": "Loja Aurora"},
        format="json",
    )
    assert blocked.status_code == 409

    verified = public.post(
        f"/public/sign/{first['token']}/verify/",
        {"code": first["verification_code"]},
        format="json",
    )
    assert verified.status_code == 200
    signed = public.post(
        f"/public/sign/{first['token']}/sign/",
        {"code": first["verification_code"], "signature": "Ana Souza"},
        format="json",
    )
    assert signed.status_code == 200
    assert signed.json()["contract_status"] == "partial"

    assert public.post(f"/public/sign/{second['token']}/verify/", {"code": second["verification_code"]}, format="json").status_code == 200
    final = public.post(
        f"/public/sign/{second['token']}/sign/",
        {"code": second["verification_code"], "signature": "Loja Aurora"},
        format="json",
    )
    assert final.status_code == 200
    assert final.json()["contract_status"] == "signed"
    assert len(final.json()["hash_sha256"]) == 64

    audit = client.get(f"/api/contracts/{contract['id']}/audit/")
    assert audit.status_code == 200
    assert {event["type"] for event in audit.json()} == {"viewed", "verified", "signed"}
    pdf = client.get(f"/api/contracts/{contract['id']}/pdf/")
    assert pdf.status_code == 200
    assert pdf["Content-Type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")

    installment = client.get(f"/api/contracts/{contract['id']}/").json()["installments"][0]
    webhook = APIClient().post(
        "/webhooks/pix/",
        {"txid": installment["pix_txid"], "status": "paid"},
        format="json",
        HTTP_X_WEBHOOK_SECRET=settings.PIX_WEBHOOK_SECRET,
    )
    assert webhook.status_code == 200
    assert webhook.json()["status"] == "paid"
