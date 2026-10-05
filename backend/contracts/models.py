from django.conf import settings
from django.db import models
import secrets


class Profile(models.Model):
    PLAN_CHOICES = [("free", "Grátis"), ("pro", "Profissional"), ("business", "Empresa")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    cpf_cnpj = models.CharField(max_length=18, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default="free")

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class ContractTemplate(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=80)
    version = models.PositiveIntegerField(default=1)
    description = models.CharField(max_length=240)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Clause(models.Model):
    template = models.ForeignKey(ContractTemplate, on_delete=models.CASCADE, related_name="clauses")
    key = models.SlugField()
    title = models.CharField(max_length=120)
    text = models.TextField()
    condition = models.JSONField(default=dict, blank=True)
    order = models.PositiveIntegerField()
    simple_explanation = models.TextField()

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["template", "key"], name="unique_template_clause")]


class Question(models.Model):
    TYPES = [(key, key) for key in ("text", "value", "date", "option", "bool", "number", "textarea")]
    template = models.ForeignKey(ContractTemplate, on_delete=models.CASCADE, related_name="questions")
    key = models.SlugField()
    text = models.CharField(max_length=240)
    type = models.CharField(max_length=12, choices=TYPES)
    options = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField()
    display_condition = models.JSONField(default=dict, blank=True)
    required = models.BooleanField(default=True)
    help_text = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["order"]
        constraints = [models.UniqueConstraint(fields=["template", "key"], name="unique_template_question")]


class Contract(models.Model):
    STATUSES = [(key, label) for key, label in (
        ("draft", "Rascunho"), ("sent", "Enviado"), ("partial", "Parcial"),
        ("signed", "Assinado"), ("cancelled", "Cancelado"),
    )]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contracts")
    template = models.ForeignKey(ContractTemplate, on_delete=models.PROTECT)
    title = models.CharField(max_length=180)
    responses = models.JSONField(default=dict)
    final_body = models.TextField()
    status = models.CharField(max_length=10, choices=STATUSES, default="draft")
    hash_sha256 = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]


def signing_token():
    return secrets.token_urlsafe(32)


class Party(models.Model):
    STATUSES = [("pending", "Pendente"), ("viewed", "Visualizou"), ("verified", "Verificou"), ("signed", "Assinou")]
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="parties")
    name = models.CharField(max_length=150)
    cpf_cnpj = models.CharField(max_length=18)
    contact = models.CharField(max_length=160)
    signing_order = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUSES, default="pending")
    token = models.CharField(max_length=64, unique=True, default=signing_token, editable=False)
    verification_code = models.CharField(max_length=64, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    signature = models.TextField(blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["signing_order", "id"]


class SignatureEvent(models.Model):
    TYPES = [(key, label) for key, label in (("viewed", "Visualizou"), ("verified", "Verificou"), ("signed", "Assinou"))]
    party = models.ForeignKey(Party, on_delete=models.PROTECT, related_name="events")
    type = models.CharField(max_length=10, choices=TYPES)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Eventos de assinatura são imutáveis.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Eventos de assinatura são imutáveis.")


class Installment(models.Model):
    STATUSES = [("pending", "Pendente"), ("paid", "Pago"), ("overdue", "Vencido")]
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="installments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUSES, default="pending")
    pix_txid = models.CharField(max_length=64, unique=True)
    paid_at = models.DateTimeField(null=True, blank=True)
