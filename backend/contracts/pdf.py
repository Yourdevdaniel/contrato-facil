import html
import os
import re
from html.parser import HTMLParser

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

# Rodapé de todas as páginas do PDF (WeasyPrint via @page no template; fallback abaixo).
PDF_FOOTER = (
    "Modelo gerado automaticamente. Não é aconselhamento jurídico: revise com um advogado antes de usar.",
    "O uso é por sua conta e risco; os autores não se responsabilizam por danos ou disputas.",
)


class BlockParser(HTMLParser):
    """Reduz o corpo salvo a blocos de texto puro (h2/p); nenhuma marcação original chega ao PDF."""

    def __init__(self):
        super().__init__()
        self.blocks = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag in {"h2", "p"}:
            self.current = {"tag": tag, "text": ""}
            self.blocks.append(self.current)

    def handle_endtag(self, tag):
        if tag in {"h2", "p"}:
            self.current = None

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"] += data
        elif data.strip():
            self.blocks.append({"tag": "p", "text": data})


def contract_blocks(body):
    parser = BlockParser()
    parser.feed(body or "")
    parser.close()
    return parser.blocks


def contract_pdf_html(contract, events):
    """HTML do PDF. O template tem autoescape: título, nomes, IP e texto das cláusulas saem escapados."""
    return render_to_string("contracts/contract_pdf.html", {
        "contract": contract,
        "blocks": contract_blocks(contract.final_body),
        "events": events,
        # Constante do código (não vem do usuário) e precisa ir crua para dentro do <style>.
        "footer_css": mark_safe(' "\\A" '.join(f'"{line}"' for line in PDF_FOOTER)),
    })


def safe_url_fetcher(url):
    """Impede o WeasyPrint de buscar recursos fora do documento (http, https, file, caminhos relativos)."""
    if not url.startswith("data:"):
        raise ValueError(f"Recurso externo bloqueado no PDF: {url[:80]}")
    from weasyprint import default_url_fetcher

    return default_url_fetcher(url)


def pdf_text(line):
    return line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def basic_pdf(document):
    """PDF local simples; o Docker usa WeasyPrint para a versão diagramada."""
    # Limite: uma página, só texto, até 52 linhas. Remover quando o ambiente local tiver GTK para o WeasyPrint.
    document = re.sub(r"<style.*?</style>", "", document, flags=re.S | re.I)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", document))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    commands = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
    for line in lines[:52]:
        commands.extend([f"({pdf_text(line)[:105]}) Tj", "T*"])
    commands.extend(["ET", "BT", "/F1 7 Tf", "50 40 Td", "9 TL"])
    for line in PDF_FOOTER:
        commands.extend([f"({pdf_text(line)}) Tj", "T*"])
    commands.append("ET")
    stream = "\n".join(commands).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    result = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    result.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    result.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(result)


def render_pdf(document):
    if os.name == "nt":
        return basic_pdf(document)
    from weasyprint import HTML

    return HTML(string=document, url_fetcher=safe_url_fetcher).write_pdf()
