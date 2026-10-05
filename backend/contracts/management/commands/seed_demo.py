from django.core.management.base import BaseCommand

from contracts.models import Clause, ContractTemplate, Question


COMMON_FINAL_CLAUSES = [
    (
        "electronic-signature",
        "DA ASSINATURA ELETRÔNICA",
        "As Partes reconhecem como válidas as assinaturas eletrônicas realizadas neste instrumento, inclusive por meio não certificado pela ICP-Brasil, desde que aceito pelas Partes e capaz de comprovar autoria e integridade, nos termos do art. 10, § 2º, da Medida Provisória nº 2.200-2/2001, observada a Lei nº 14.063/2020 quando aplicável.",
        {},
        "Reconhece a assinatura eletrônica e os registros de integridade.",
    ),
    (
        "forum",
        "DO FORO",
        "Fica definido o foro legalmente aplicável para resolver controvérsias decorrentes deste instrumento, respeitadas as regras legais obrigatórias.",
        {},
        "Indica que conflitos serão tratados pelo foro definido em lei.",
    ),
    (
        "closing",
        "DAS DISPOSIÇÕES FINAIS",
        "Por estarem de acordo, as Partes declaram ter lido, compreendido e aceitado integralmente este instrumento e o assinam eletronicamente para que produza seus efeitos legais.",
        {},
        "Registra a concordância final das partes.",
    ),
]


TEMPLATES = [
    {
        "slug": "prestacao-servicos", "name": "Prestação de serviços", "category": "Serviços",
        "description": "Para freelancers, MEIs e prestadores em geral.",
        "opening": (
            "Pelo presente instrumento particular de contrato de prestação de serviços, {client_name}, doravante denominada CONTRATANTE, e {provider_name}, doravante denominado CONTRATADO, têm entre si justo e contratado o presente ajuste, regido pelos arts. 421, 421-A e 422, bem como pelos arts. 593 a 609 da Lei nº 10.406/2002 (Código Civil), mediante as cláusulas e condições seguintes."
        ),
        "questions": [
            ("client_name", "Quem está contratando?", "text"), ("provider_name", "Quem vai prestar o serviço?", "text"),
            ("service", "Qual serviço será feito?", "textarea"), ("value", "Qual é o valor total?", "value"),
            ("start_date", "Quando começa?", "date"), ("end_date", "Quando termina?", "date"),
            ("payment_method", "Como será o pagamento?", "option"), ("has_down_payment", "Haverá sinal?", "bool"),
            ("down_payment_percent", "Qual percentual do sinal?", "number"), ("has_late_fee", "Haverá multa por atraso?", "bool"),
        ],
        "clauses": [
            ("object", "DO OBJETO", "O CONTRATADO prestará os seguintes serviços: {service}. O serviço deverá ser realizado com cuidado, boa-fé e de acordo com as condições previstas neste contrato.", {}, "Define exatamente o que será entregue."),
            ("term", "DO PRAZO", "A execução dos serviços terá início em {start_date} e deverá ser concluída até {end_date}, salvo prorrogação expressamente acordada entre as Partes.", {}, "Marca início e fim do trabalho."),
            ("payment", "DA REMUNERAÇÃO", "Pela execução completa do serviço, a CONTRATANTE pagará ao CONTRATADO o valor de {value_brl}, por meio de {payment_method}.", {}, "Registra valor e forma de pagamento."),
            ("down-payment", "DO SINAL E PRINCÍPIO DE PAGAMENTO", "A CONTRATANTE pagará, a título de sinal e princípio de pagamento, o percentual de {down_payment_percent}% do valor total, correspondente a {down_payment_brl}, quantia que será integralmente abatida do saldo contratual.", {"key": "has_down_payment", "equals": True}, "Reserva a agenda e integra o preço final."),
            ("late-fee", "DO ATRASO NO PAGAMENTO", "O atraso no pagamento sujeitará a Parte devedora à multa de 2% sobre o débito e a juros de 1% ao mês, calculados proporcionalmente ao período de atraso, sem prejuízo das consequências previstas nos arts. 389, 395 e 408 a 416 do Código Civil.", {"key": "has_late_fee", "equals": True}, "Define consequência objetiva para atraso."),
        ],
    },
    {
        "slug": "confissao-divida", "name": "Confissão de dívida", "category": "Financeiro",
        "description": "Formalize valor devido, parcelas e vencimentos.",
        "opening": (
            "Pelo presente instrumento particular de confissão de dívida, {debtor_name}, doravante denominado DEVEDOR, reconhece em favor de {creditor_name}, doravante denominado CREDOR, obrigação regida pelos arts. 389, 394, 395, 421, 421-A e 422 da Lei nº 10.406/2002 (Código Civil), mediante as cláusulas e condições seguintes."
        ),
        "questions": [
            ("creditor_name", "Quem tem o valor a receber?", "text"), ("debtor_name", "Quem vai pagar?", "text"),
            ("value", "Qual é o valor da dívida?", "value"), ("origin", "De onde veio a dívida?", "textarea"),
            ("due_date", "Quando vence?", "date"), ("payment_method", "Como será paga?", "option"),
            ("has_late_fee", "Haverá multa por atraso?", "bool"), ("witness_name", "Nome da testemunha", "text"),
        ],
        "clauses": [
            ("acknowledgement", "DO RECONHECIMENTO DA DÍVIDA", "O DEVEDOR reconhece, de forma expressa, dever ao CREDOR a quantia líquida de {value_brl}, decorrente de {origin}, declarando conhecer a origem e a composição da obrigação.", {}, "Registra a existência e origem da dívida."),
            ("payment", "DO PAGAMENTO", "A dívida vencerá em {due_date} e será paga por meio de {payment_method}. O pagamento será considerado concluído quando o valor estiver disponível ao CREDOR.", {}, "Define como e quando quitar."),
            ("late-fee", "DO INADIMPLEMENTO", "O atraso no pagamento sujeitará o DEVEDOR à multa moratória de 2% sobre o débito e a juros de 1% ao mês, calculados proporcionalmente ao período de mora, sem prejuízo dos arts. 389, 394 e 395 do Código Civil.", {"key": "has_late_fee", "equals": True}, "Prevê encargos por atraso."),
            ("enforceability", "DA FORÇA EXECUTIVA", "O presente instrumento poderá constituir título executivo extrajudicial quando preenchidos os requisitos do art. 784, III e § 4º, da Lei nº 13.105/2015 (Código de Processo Civil), sem prejuízo da verificação judicial dos requisitos de certeza, liquidez e exigibilidade.", {}, "Explica quando a dívida pode ser cobrada por execução."),
            ("witness", "DA TESTEMUNHA", "Figura como testemunha do presente instrumento: {witness_name}.", {}, "Identifica quem acompanha a assinatura."),
        ],
    },
    {
        "slug": "freela-criativo", "name": "Freela criativo", "category": "Serviços",
        "description": "Para design, foto, vídeo e criação com direitos autorais.",
        "opening": (
            "Pelo presente instrumento particular de prestação de serviços criativos e cessão de direitos patrimoniais, {client_name}, doravante denominada CONTRATANTE, e {provider_name}, doravante denominado CRIADOR, têm entre si justo e contratado o presente ajuste, regido pelos arts. 421, 421-A, 422 e 593 a 609 do Código Civil e pelos arts. 49 e 50 da Lei nº 9.610/1998, mediante as cláusulas e condições seguintes."
        ),
        "questions": [
            ("client_name", "Quem encomendou o trabalho?", "text"), ("provider_name", "Quem fará a criação?", "text"),
            ("service", "O que será criado?", "textarea"), ("value", "Qual é o valor?", "value"),
            ("end_date", "Qual é a data de entrega?", "date"), ("payment_method", "Como será pago?", "option"),
            ("has_down_payment", "Haverá sinal?", "bool"), ("down_payment_percent", "Qual percentual do sinal?", "number"),
        ],
        "clauses": [
            ("scope", "DO OBJETO E ESCOPO CRIATIVO", "O CRIADOR desenvolverá para a CONTRATANTE o seguinte trabalho: {service}, obrigando-se a entregar a versão final aprovada até {end_date}.", {}, "Delimita a entrega criativa."),
            ("payment", "DA REMUNERAÇÃO", "Pelos serviços e pela cessão patrimonial delimitada neste instrumento, a CONTRATANTE pagará ao CRIADOR o montante de {value_brl}, por meio de {payment_method}.", {}, "Registra preço e pagamento."),
            ("down-payment", "DO SINAL E PRINCÍPIO DE PAGAMENTO", "A CONTRATANTE pagará sinal correspondente a {down_payment_percent}% do valor total, equivalente a {down_payment_brl}, a ser integralmente abatido do saldo contratual.", {"key": "has_down_payment", "equals": True}, "Reserva a agenda do profissional."),
            ("rights", "DA CESSÃO DE DIREITOS PATRIMONIAIS", "Após o pagamento integral, o CRIADOR cede à CONTRATANTE, de forma definitiva e para uso no território nacional, os direitos patrimoniais necessários ao uso da entrega final aprovada para a finalidade prevista neste contrato, nos termos dos arts. 49 e 50 da Lei nº 9.610/1998. Permanecem protegidos os direitos morais do autor, bem como os estudos, arquivos e propostas não aprovados.", {}, "Define o que o cliente pode usar e o que fica com o criador."),
        ],
    },
    {
        "slug": "aluguel-bem-movel", "name": "Aluguel de bem móvel", "category": "Locação",
        "description": "Para equipamentos, ferramentas, roupas e outros bens.",
        "opening": (
            "Pelo presente instrumento particular de locação de bem móvel, {owner_name}, doravante denominado LOCADOR, e {renter_name}, doravante denominado LOCATÁRIO, têm entre si justo e contratado o presente ajuste, regido pelos arts. 421, 421-A e 422, bem como pelos arts. 565 a 578 da Lei nº 10.406/2002 (Código Civil), mediante as cláusulas e condições seguintes."
        ),
        "questions": [
            ("owner_name", "Quem é dono do bem?", "text"), ("renter_name", "Quem vai alugar?", "text"),
            ("asset", "Qual bem será alugado?", "textarea"), ("value", "Qual é o valor do aluguel?", "value"),
            ("start_date", "Quando será retirado?", "date"), ("end_date", "Quando será devolvido?", "date"),
            ("payment_method", "Como será pago?", "option"), ("has_late_fee", "Haverá multa por atraso?", "bool"),
        ],
        "clauses": [
            ("asset", "DO OBJETO DA LOCAÇÃO", "O LOCADOR entrega ao LOCATÁRIO, em locação temporária, o seguinte bem móvel: {asset}.", {}, "Identifica o objeto alugado."),
            ("term", "DO PRAZO E DA RESTITUIÇÃO", "A locação vigorará de {start_date} a {end_date}, data em que o LOCATÁRIO deverá restituir o bem ao LOCADOR, salvo prorrogação expressamente acordada.", {}, "Define retirada e devolução."),
            ("payment", "DO ALUGUEL", "Pela utilização do bem, o LOCATÁRIO pagará ao LOCADOR o valor de {value_brl}, por meio de {payment_method}.", {}, "Registra o preço."),
            ("care", "DA CONSERVAÇÃO E RESPONSABILIDADE", "O LOCATÁRIO deverá conservar e utilizar o bem de acordo com sua finalidade e devolvê-lo no estado em que o recebeu, exceto pelo desgaste natural do uso regular. Também responderá pelos danos causados por sua ação ou omissão.", {}, "Atribui responsabilidade pela conservação."),
            ("late-fee", "DA MORA NA RESTITUIÇÃO", "A restituição após o prazo pactuado sujeitará o LOCATÁRIO à multa moratória de 2% e ao pagamento do aluguel diário proporcional até a efetiva devolução, sem prejuízo das perdas e danos comprovadas.", {"key": "has_late_fee", "equals": True}, "Define consequência do atraso."),
        ],
    },
    {
        "slug": "parceria-comercial", "name": "Parceria comercial", "category": "Negócios",
        "description": "Organize responsabilidades, divisão de receita e prazo.",
        "opening": (
            "Pelo presente instrumento particular de parceria comercial, {partner_one}, doravante denominado PRIMEIRO PARCEIRO, e {partner_two}, doravante denominado SEGUNDO PARCEIRO, têm entre si justo e contratado o presente ajuste atípico, autorizado pelo art. 425 e regido pelos arts. 421, 421-A e 422 da Lei nº 10.406/2002 (Código Civil), mediante as cláusulas e condições seguintes."
        ),
        "questions": [
            ("partner_one", "Quem é o primeiro parceiro?", "text"), ("partner_two", "Quem é o segundo parceiro?", "text"),
            ("service", "Qual é o objetivo da parceria?", "textarea"), ("revenue_split", "Qual é a divisão da receita?", "text"),
            ("start_date", "Quando começa?", "date"), ("end_date", "Quando termina?", "date"),
        ],
        "clauses": [
            ("purpose", "DO OBJETO DA PARCERIA", "As Partes obrigam-se a cooperar, de forma coordenada e autônoma, para a seguinte finalidade: {service}.", {}, "Registra o objetivo comum."),
            ("revenue", "DA APURAÇÃO E DIVISÃO DE RECEITAS", "A receita líquida recebida na parceria será calculada e distribuída entre as Partes segundo o seguinte critério: {revenue_split}.", {}, "Define como o resultado será repartido."),
            ("term", "DO PRAZO", "A parceria vigorará de {start_date} a {end_date}, podendo ser prorrogada mediante manifestação expressa de ambas as Partes.", {}, "Define a duração do acordo."),
            ("independence", "DA AUTONOMIA DAS PARTES", "Cada Parte conservará autonomia jurídica, técnica, administrativa e financeira. A celebração deste instrumento, por si só, não constitui sociedade, associação, representação, solidariedade ou vínculo empregatício, sem prejuízo da realidade da relação efetivamente mantida.", {}, "Evita interpretar a parceria como outra relação."),
        ],
    },
    {
        "slug": "nda", "name": "Acordo de confidencialidade", "category": "Proteção",
        "description": "Proteja informações compartilhadas antes de uma negociação.",
        "opening": (
            "Pelo presente instrumento particular de acordo de confidencialidade, {discloser_name}, doravante denominada PARTE REVELADORA, e {receiver_name}, doravante denominada PARTE RECEPTORA, têm entre si justo e contratado o presente ajuste, regido pelos arts. 421, 421-A e 422 da Lei nº 10.406/2002 (Código Civil) e, quando houver tratamento de dados pessoais, pelos arts. 7º, V, e 46 da Lei nº 13.709/2018 (Lei Geral de Proteção de Dados), mediante as cláusulas e condições seguintes."
        ),
        "questions": [
            ("discloser_name", "Quem vai compartilhar informações?", "text"), ("receiver_name", "Quem vai recebê-las?", "text"),
            ("service", "Qual é o assunto protegido?", "textarea"), ("start_date", "Quando começa a confidencialidade?", "date"),
            ("end_date", "Até quando ela vale?", "date"), ("purpose", "Para qual finalidade as informações serão usadas?", "textarea"),
        ],
        "clauses": [
            ("information", "DAS INFORMAÇÕES CONFIDENCIAIS", "Consideram-se confidenciais as informações reveladas pela PARTE REVELADORA à PARTE RECEPTORA relacionadas a {service}, independentemente do meio em que sejam transmitidas, desde que sua natureza reservada seja expressa ou razoavelmente reconhecível.", {}, "Delimita o conteúdo protegido."),
            ("purpose", "DA FINALIDADE E RESTRIÇÃO DE USO", "A PARTE RECEPTORA utilizará as informações confidenciais exclusivamente para {purpose} e não poderá empregá-las em benefício próprio ou de terceiros para outra finalidade.", {}, "Impede uso para outra finalidade."),
            ("term", "DO PRAZO DE CONFIDENCIALIDADE", "As obrigações de confidencialidade vigorarão de {start_date} a {end_date}, sem prejuízo da proteção que decorra de lei ou da natureza de segredo empresarial após esse período.", {}, "Define a duração do sigilo."),
            ("care", "DO DEVER DE PROTEÇÃO", "A PARTE RECEPTORA adotará medidas técnicas e administrativas razoáveis para impedir acesso, uso, alteração ou divulgação não autorizados, limitará o conhecimento às pessoas estritamente necessárias e comunicará prontamente qualquer incidente à PARTE REVELADORA, observando o art. 46 da Lei nº 13.709/2018 quando houver dados pessoais.", {}, "Explica como preservar o sigilo."),
            ("exceptions", "DAS EXCEÇÕES", "Não serão consideradas confidenciais as informações comprovadamente públicas sem violação deste instrumento, legitimamente conhecidas antes da revelação, recebidas de terceiro autorizado ou cuja divulgação seja exigida por lei ou ordem de autoridade competente.", {}, "Define situações em que o dever de sigilo não se aplica."),
        ],
    },
]


class Command(BaseCommand):
    help = "Cria os modelos jurídicos de demonstração."

    def handle(self, *args, **options):
        for data in TEMPLATES:
            template, _ = ContractTemplate.objects.update_or_create(
                slug=data["slug"], defaults={key: data[key] for key in ("name", "category", "description")}
            )
            template.questions.all().delete()
            for order, (key, text, kind) in enumerate(data["questions"], 1):
                Question.objects.create(
                    template=template, key=key, text=text, type=kind, order=order,
                    options=["Pix", "Boleto", "Transferência"] if key == "payment_method" else [],
                    display_condition={"key": "has_down_payment", "equals": True} if key == "down_payment_percent" else {},
                    required=key not in {"down_payment_percent", "witness_name"},
                )
            template.clauses.all().delete()
            clauses = [
                ("preamble", "DO PREÂMBULO E FUNDAMENTO LEGAL", data["opening"], {}, "Identifica as partes e a legislação aplicável."),
                *data["clauses"],
                *COMMON_FINAL_CLAUSES,
            ]
            for order, (key, title, text, condition, explanation) in enumerate(clauses, 1):
                Clause.objects.create(template=template, key=key, title=title, text=text, condition=condition, order=order, simple_explanation=explanation)
        self.stdout.write(self.style.SUCCESS("Modelos de demonstração prontos."))
