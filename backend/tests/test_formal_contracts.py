import pytest
from django.core.management import call_command

from contracts.models import ContractTemplate, Question
from contracts.services import render_contract


LEGAL_BASES = {
    "prestacao-servicos": "arts. 593 a 609",
    "freela-criativo": "Lei nº 9.610/1998",
    "aluguel-bem-movel": "arts. 565 a 578",
    "confissao-divida": "art. 784, III e § 4º",
    "parceria-comercial": "art. 425",
    "nda": "Lei nº 13.709/2018",
}

EXCESSIVE_TERMS = (
    "assinaturas eletrônicas apostas",
    "normas protetivas eventualmente incidentes",
    "efeitos juridicamente cabíveis",
    "condições ora pactuadas",
    "integral execução",
    "obrigação pecuniária",
    "efetiva disponibilidade do valor",
    "modalidades inerentes",
    "danos que lhe forem imputáveis",
    "receita líquida efetivamente auferida",
    "abstendo-se de",
)


@pytest.mark.django_db
def test_all_templates_use_formal_legal_language():
    call_command("seed_demo")
    answers = {question.key: "Parte Teste" for question in Question.objects.all()}
    answers.update(value="1000", has_down_payment=True, down_payment_percent=30, has_late_fee=True)

    for template in ContractTemplate.objects.all():
        body, _ = render_contract(template, answers)
        assert "Pelo presente instrumento particular" in body
        assert LEGAL_BASES[template.slug] in body
        assert "art. 10, § 2º, da Medida Provisória nº 2.200-2/2001" in body
        assert "Vossa Excelência" not in body
        assert "garantia absoluta" not in body.lower()
        assert not any(term in body.lower() for term in EXCESSIVE_TERMS)
