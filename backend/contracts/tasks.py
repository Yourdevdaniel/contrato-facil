from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Contract, Party


@shared_task
def send_signing_link(contact, name, link, message=""):
    if "@" not in contact:
        return {"channel": "whatsapp-local", "contact": contact, "link": link}
    send_mail(
        "Contrato aguardando sua assinatura",
        f"Olá, {name}. {message}\n\nLeia e assine: {link}",
        None,
        [contact],
    )
    return {"channel": "email", "contact": contact}


@shared_task
def pending_signature_reminders():
    pending = Party.objects.filter(contract__status__in=["sent", "partial"]).exclude(status="signed")
    count = 0
    for party in pending.iterator():
        send_signing_link.run(
            party.contact,
            party.name,
            f"{settings.FRONTEND_URL}/assinar/{party.token}",
            "Este é um lembrete: o contrato ainda aguarda sua assinatura.",
        )
        count += 1
    return count


@shared_task
def expiring_contract_alerts():
    today = timezone.localdate()
    contracts = Contract.objects.filter(expires_at__date__gte=today, expires_at__date__lte=today + timezone.timedelta(days=7)).select_related("user")
    count = 0
    for contract in contracts.iterator():
        if contract.user.email:
            send_mail(
                f"Contrato próximo do vencimento: {contract.title}",
                f"O contrato vence em {contract.expires_at:%d/%m/%Y}. Acesse seu cofre para revisar.",
                None,
                [contract.user.email],
            )
            count += 1
    return count
