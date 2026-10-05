from decimal import Decimal
from html.parser import HTMLParser

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Clause, Contract, ContractTemplate, Installment, Party, Profile, Question, SignatureEvent
from .services import render_contract


class ContractHTMLParser(HTMLParser):
    allowed = {"section", "h2", "p"}

    def __init__(self):
        super().__init__()
        self.stack = []

    def handle_starttag(self, tag, attrs):
        valid_parent = (tag == "section" and not self.stack) or (tag in {"h2", "p"} and self.stack == ["section"])
        if tag not in self.allowed or attrs or not valid_parent:
            raise serializers.ValidationError("O contrato contém formatação não permitida.")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise serializers.ValidationError("A estrutura do contrato é inválida.")

    def handle_data(self, data):
        if data.strip() and (not self.stack or self.stack[-1] not in {"h2", "p"}):
            raise serializers.ValidationError("O texto deve estar dentro de uma cláusula.")

    def handle_comment(self, data):
        raise serializers.ValidationError("Comentários HTML não são permitidos.")


def token_payload(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {"id": user.id, "name": user.get_full_name(), "email": user.email},
    }


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    cpf_cnpj = serializers.CharField(max_length=18, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Já existe uma conta com este e-mail.")
        return value

    def create(self, data):
        name = data.pop("name").strip().split(" ", 1)
        cpf_cnpj = data.pop("cpf_cnpj", "")
        phone = data.pop("phone", "")
        user = User.objects.create_user(
            username=data["email"],
            email=data["email"],
            password=data["password"],
            first_name=name[0],
            last_name=name[1] if len(name) > 1 else "",
        )
        Profile.objects.create(user=user, cpf_cnpj=cpf_cnpj, phone=phone)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"].lower(), password=data["password"])
        if not user:
            raise serializers.ValidationError("E-mail ou senha inválidos.")
        return {"user": user}


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "key", "text", "type", "options", "order", "display_condition", "required", "help_text")


class TemplateSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="questions.count", read_only=True)

    class Meta:
        model = ContractTemplate
        fields = ("id", "name", "slug", "category", "version", "description", "question_count")


class ClauseSerializer(serializers.ModelSerializer):
    explanation = serializers.CharField(source="simple_explanation")

    class Meta:
        model = Clause
        fields = ("key", "title", "text", "explanation", "order")


class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ("id", "name", "cpf_cnpj", "contact", "signing_order", "status", "signed_at")


class InstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Installment
        fields = ("id", "amount", "due_date", "status", "pix_txid", "paid_at")


class ContractSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    clauses = serializers.SerializerMethodField()
    parties = PartySerializer(many=True, read_only=True)
    installments = InstallmentSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = (
            "id", "template", "template_name", "title", "responses", "final_body", "status",
            "hash_sha256", "expires_at", "created_at", "updated_at", "clauses", "parties", "installments",
        )
        read_only_fields = ("final_body", "status", "hash_sha256")
        extra_kwargs = {"title": {"required": False}}

    def get_clauses(self, obj):
        _, clauses = render_contract(obj.template, obj.responses)
        return ClauseSerializer(clauses, many=True).data

    def create(self, validated_data):
        template = validated_data["template"]
        body, _ = render_contract(template, validated_data["responses"])
        validated_data.setdefault("title", f"{template.name} — {validated_data['responses'].get('client_name') or validated_data['responses'].get('debtor_name') or 'Novo contrato'}")
        return Contract.objects.create(user=self.context["request"].user, final_body=body, **validated_data)


class ContractUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ("title", "final_body", "expires_at", "status")

    def validate_status(self, value):
        if value not in {"draft", "cancelled"}:
            raise serializers.ValidationError("Este status é controlado pelo fluxo de assinatura.")
        return value

    def validate_final_body(self, value):
        parser = ContractHTMLParser()
        parser.feed(value)
        parser.close()
        if parser.stack:
            raise serializers.ValidationError("A estrutura do contrato é inválida.")
        return value


class EventSerializer(serializers.ModelSerializer):
    party_name = serializers.CharField(source="party.name")

    class Meta:
        model = SignatureEvent
        fields = ("id", "party_name", "type", "ip", "user_agent", "timestamp")


class SendPartySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    cpf_cnpj = serializers.CharField(max_length=18)
    contact = serializers.CharField(max_length=160)
    signing_order = serializers.IntegerField(min_value=1)


class SendInstallmentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))
    due_date = serializers.DateField()


class SendContractSerializer(serializers.Serializer):
    parties = SendPartySerializer(many=True, min_length=1)
    installments = SendInstallmentSerializer(many=True, required=False)
    message = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_parties(self, parties):
        orders = [party["signing_order"] for party in parties]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("Cada parte precisa ter uma ordem diferente.")
        return parties
