import pytest
from django.contrib.auth.models import User
from django.core import mail
from django.core.management import call_command

from contracts.models import Contract, ContractTemplate, Party
from contracts.tasks import pending_signature_reminders
from tests._credentials import TEST_PASSWORD


@pytest.mark.django_db
def test_pending_signature_reminder_is_dispatched():
    call_command("seed_demo")
    user = User.objects.create_user(username="owner@example.com", email="owner@example.com", password=TEST_PASSWORD)
    template = ContractTemplate.objects.first()
    contract = Contract.objects.create(user=user, template=template, title="Contrato pendente", responses={}, final_body="Documento", status="sent")
    Party.objects.create(contract=contract, name="Cliente", cpf_cnpj="12345678901", contact="cliente@example.com")

    assert pending_signature_reminders.run() == 1
    assert len(mail.outbox) == 1
    assert "assinatura" in mail.outbox[0].subject.lower()
