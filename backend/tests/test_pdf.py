import pytest
from django.contrib.auth.models import User

from contracts.models import Contract, ContractTemplate, Party, SignatureEvent
from contracts.pdf import PDF_FOOTER, basic_pdf, contract_pdf_html, safe_url_fetcher
from tests._credentials import TEST_PASSWORD

PAYLOAD = '<img src="http://evil.test/x">'


def test_fallback_pdf_prints_legal_footer():
    pdf = basic_pdf("<h1>Contrato</h1><p>Texto</p>")
    assert pdf.startswith(b"%PDF")
    for line in PDF_FOOTER:
        assert line.encode("latin-1") in pdf


@pytest.mark.django_db
def test_pdf_html_escapes_user_values():
    user = User.objects.create_user(username="owner@example.com", password=TEST_PASSWORD)
    template = ContractTemplate.objects.create(name="Modelo", slug="modelo", category="Teste", description="Teste")
    contract = Contract.objects.create(
        user=user, template=template, title=PAYLOAD, responses={},
        final_body=f"<section><h2>DO OBJETO</h2><p>Serviço {PAYLOAD}</p></section>"
                   '<img src="file:///etc/passwd"><script>alert(1)</script>',
    )
    party = Party.objects.create(contract=contract, name=PAYLOAD, cpf_cnpj="12345678901", contact="cliente@example.com")
    SignatureEvent.objects.create(party=party, type="viewed", ip="127.0.0.1")

    document = contract_pdf_html(contract, SignatureEvent.objects.filter(party__contract=contract).select_related("party"))

    assert "<img" not in document
    assert "<script" not in document
    assert "&lt;img src=&quot;http://evil.test/x&quot;&gt;" in document
    assert "<h2>DO OBJETO</h2>" in document
    for line in PDF_FOOTER:
        assert line in document
    assert b"@page" not in basic_pdf(document)


@pytest.mark.parametrize("url", ["http://evil.test/x", "https://evil.test/x", "file:///etc/passwd", "logo.png"])
def test_pdf_url_fetcher_blocks_external_resources(url):
    with pytest.raises(ValueError):
        safe_url_fetcher(url)
