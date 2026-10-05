import secrets
import hashlib
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.decorators import throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import Contract, ContractTemplate, Installment, Party, SignatureEvent
from .serializers import (
    ContractSerializer,
    ContractUpdateSerializer,
    LoginSerializer,
    EventSerializer,
    QuestionSerializer,
    RegisterSerializer,
    SendContractSerializer,
    TemplateSerializer,
    token_payload,
)
from .services import finalize_contract, record_event
from .tasks import send_signing_link
from .pdf import contract_pdf_html, render_pdf


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(token_payload(serializer.save()), status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response(token_payload(serializer.validated_data["user"]))


@api_view(["GET"])
@permission_classes([AllowAny])
def templates(request):
    queryset = ContractTemplate.objects.filter(active=True).prefetch_related("questions")
    return Response(TemplateSerializer(queryset, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def template_questions(request, template_id):
    template = get_object_or_404(ContractTemplate, pk=template_id, active=True)
    return Response(QuestionSerializer(template.questions.all(), many=True).data)


@api_view(["GET", "POST"])
def contracts(request):
    if request.method == "GET":
        queryset = Contract.objects.filter(user=request.user).select_related("template").prefetch_related("parties", "installments")
        return Response(ContractSerializer(queryset, many=True).data)
    serializer = ContractSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PATCH"])
def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id, user=request.user)
    if request.method == "PATCH":
        serializer = ContractUpdateSerializer(contract, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    return Response(ContractSerializer(contract).data)


@api_view(["POST"])
def send_contract(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id, user=request.user, status="draft")
    serializer = SendContractSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    now = timezone.now()
    links = []
    with transaction.atomic():
        for data in serializer.validated_data["parties"]:
            code = f"{secrets.randbelow(1_000_000):06d}"
            party = Party.objects.create(
                contract=contract,
                verification_code=hashlib.sha256(code.encode()).hexdigest(),
                code_expires_at=now + timedelta(minutes=30),
                **data,
            )
            link = f"{settings.FRONTEND_URL}/assinar/{party.token}"
            send_signing_link.delay(party.contact, party.name, link, serializer.validated_data.get("message", ""))
            item = {"name": party.name, "token": party.token, "url": link}
            if settings.DEBUG or settings.CELERY_TASK_ALWAYS_EAGER:
                item["verification_code"] = code
            links.append(item)
        for data in serializer.validated_data.get("installments", []):
            Installment.objects.create(contract=contract, pix_txid=f"CF-{contract.id}-{secrets.token_hex(8)}", **data)
        contract.status = "sent"
        contract.save(update_fields=["status", "updated_at"])
    return Response({"status": contract.status, "signing_links": links})


def public_party(token):
    return get_object_or_404(Party.objects.select_related("contract", "contract__template"), token=token)


@api_view(["GET"])
@permission_classes([AllowAny])
def public_signing(request, token):
    party = public_party(token)
    if not party.events.filter(type="viewed").exists():
        record_event(party, "viewed", request)
    if party.status == "pending":
        party.status = "viewed"
        party.save(update_fields=["status"])
    return Response({
        "contract": {"title": party.contract.title, "final_body": party.contract.final_body, "status": party.contract.status},
        "party": {"name": party.name, "status": party.status},
    })


def valid_code(party, code):
    digest = hashlib.sha256(str(code).encode()).hexdigest() if code else ""
    return bool(code and secrets.compare_digest(digest, party.verification_code) and party.code_expires_at and party.code_expires_at >= timezone.now())


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def verify_signature(request, token):
    party = public_party(token)
    if not valid_code(party, request.data.get("code")):
        return Response({"detail": "Código inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)
    if party.status != "signed" and not party.events.filter(type="verified").exists():
        record_event(party, "verified", request)
        party.status = "verified"
        party.save(update_fields=["status"])
    return Response({"verified": True})


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle])
def sign(request, token):
    party = public_party(token)
    if party.contract.parties.filter(signing_order__lt=party.signing_order).exclude(status="signed").exists():
        return Response({"detail": "Aguarde as partes anteriores assinarem."}, status=status.HTTP_409_CONFLICT)
    if party.status != "verified" or not valid_code(party, request.data.get("code")):
        return Response({"detail": "Verifique o código antes de assinar."}, status=status.HTTP_400_BAD_REQUEST)
    signature = str(request.data.get("signature", "")).strip()
    if len(signature) < 2:
        return Response({"signature": "Digite ou desenhe sua assinatura."}, status=status.HTTP_400_BAD_REQUEST)
    party.signature = signature
    party.status = "signed"
    party.signed_at = timezone.now()
    party.save(update_fields=["signature", "status", "signed_at"])
    record_event(party, "signed", request)
    if party.contract.parties.exclude(status="signed").exists():
        party.contract.status = "partial"
        party.contract.save(update_fields=["status", "updated_at"])
    else:
        finalize_contract(party.contract)
    return Response({"contract_status": party.contract.status, "hash_sha256": party.contract.hash_sha256})


@api_view(["GET"])
def audit(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id, user=request.user)
    events = SignatureEvent.objects.filter(party__contract=contract).select_related("party")
    return Response(EventSerializer(events, many=True).data)


@api_view(["GET"])
def contract_pdf(request, contract_id):
    contract = get_object_or_404(Contract, pk=contract_id, user=request.user)
    events = SignatureEvent.objects.filter(party__contract=contract).select_related("party")
    response = HttpResponse(render_pdf(contract_pdf_html(contract, events)), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="contrato-{contract.id}.pdf"'
    return response


@api_view(["POST"])
@permission_classes([AllowAny])
def pix_webhook(request):
    provided = request.headers.get("X-Webhook-Secret", "")
    if not secrets.compare_digest(provided, settings.PIX_WEBHOOK_SECRET):
        return Response({"detail": "Assinatura inválida."}, status=status.HTTP_401_UNAUTHORIZED)
    installment = get_object_or_404(Installment, pix_txid=request.data.get("txid"))
    if request.data.get("status") == "paid" and installment.status != "paid":
        installment.status = "paid"
        installment.paid_at = timezone.now()
        installment.save(update_fields=["status", "paid_at"])
    return Response({"status": installment.status})
