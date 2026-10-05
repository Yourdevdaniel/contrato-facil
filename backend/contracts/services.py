import hashlib
import html
from decimal import Decimal

from django.utils import timezone

from .models import Clause, Contract, SignatureEvent


class SafeAnswers(dict):
    def __missing__(self, key):
        return f"[{key}]"


def brl(value):
    amount = Decimal(str(value or 0))
    return f"R$ {amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def condition_matches(condition, answers):
    if not condition:
        return True
    actual = answers.get(condition.get("key"))
    if "equals" in condition:
        return actual == condition["equals"]
    return bool(actual)


def render_contract(template, answers):
    values = SafeAnswers({key: html.escape(str(value)) for key, value in answers.items()})
    values["value_brl"] = brl(answers.get("value"))
    if answers.get("down_payment_percent"):
        values["down_payment_brl"] = brl(Decimal(str(answers.get("value", 0))) * Decimal(str(answers["down_payment_percent"])) / 100)
    rendered = []
    visible = []
    for clause in template.clauses.all():
        if condition_matches(clause.condition, answers):
            text = clause.text.format_map(values)
            rendered.append(f"<section><h2>{clause.title}</h2><p>{text}</p></section>")
            visible.append(clause)
    return "\n".join(rendered), visible


def finalize_contract(contract):
    signatures = "|".join(f"{party.name}:{party.signed_at.isoformat()}" for party in contract.parties.all())
    contract.hash_sha256 = hashlib.sha256(f"{contract.final_body}|{signatures}".encode()).hexdigest()
    contract.status = "signed"
    contract.save(update_fields=["hash_sha256", "status", "updated_at"])


def record_event(party, event_type, request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    return SignatureEvent.objects.create(
        party=party,
        type=event_type,
        ip=forwarded or request.META.get("REMOTE_ADDR") or None,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
    )
