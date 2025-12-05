import re
from unicodedata import normalize

class MotorExtracao:
    
    # Dicionário de Meses (Constante)
    MESES = {
        'JANEIRO': '01', 'FEVEREIRO': '02', 'MARCO': '03',
        'ABRIL': '04', 'MAIO': '05', 'JUNHO': '06', 'JULHO': '07',
        'AGOSTO': '08', 'SETEMBRO': '09', 'OUTUBRO': '10', 'NOVEMBRO': '11', 'DEZEMBRO': '12',
        'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04', 'MAI': '05', 'JUN': '06',
        'JUL': '07', 'AGO': '08', 'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
    }

    # Regex de Data (Compilados)
    RE_DATA_COLADA = re.compile(r"(\d{2}/\d{2}/\d{4})\s+(?:R\$)?\s*\d{1,3}(?:\.\d{3})*,\d{2}")
    RE_DATA_DUPLA  = re.compile(r"(\d{2}/\d{2}/\d{4}).{1,100}?(\d{2}/\d{2}/\d{4}).{1,50}?(\d{1,3}(?:\.\d{3})*,\d{2})")
    RE_REF         = re.compile(r"REFERENCIA\s*[:\.]*\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
    RE_PAGAMENTO   = re.compile(r"(?:PAGAMENTO|CRÉDITO|CREDITO).*?(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
    RE_VENCIMENTO  = re.compile(r"VENCIMENTO") # Para checagem negativa
    RE_DATA_GEN    = re.compile(r"(?:EMISSAO|PERÍODO|PERIODO|DATA).*?(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
    RE_MES_ANO     = re.compile(r"([A-ZÇç]+)/(\d{4})", re.IGNORECASE)
    RE_MM_AAAA     = re.compile(r"(\d{2})/(\d{4})")

    # Regex de Valor
    REGEX_MOEDA    = r"\D*?(\d{1,3}(?:\.\d{3})*,\d{2})"
    RE_VAL_FOLHA1  = re.compile(r"VALOR DOS PAGAMENTOS" + REGEX_MOEDA)
    RE_VAL_FOLHA2  = re.compile(r"TOTAL DE ACATADOS" + REGEX_MOEDA)
    RE_VAL_EXTRATO = re.compile(r"SALDO (?:LIQUIDO|ATUAL|TOTAL|ANTERIOR)" + REGEX_MOEDA, re.IGNORECASE)
    RE_VAL_GERAL   = [
        re.compile(r"VALOR PAGO" + REGEX_MOEDA, re.IGNORECASE),
        re.compile(r"VALOR DO DOCUMENTO" + REGEX_MOEDA, re.IGNORECASE),
        re.compile(r"VALOR COBRADO" + REGEX_MOEDA, re.IGNORECASE),
        re.compile(r"VALOR" + REGEX_MOEDA, re.IGNORECASE),
        re.compile(r"R\$" + REGEX_MOEDA, re.IGNORECASE)
    ]

    # Regex de Favorecido
    RE_CLIENTE     = re.compile(r"(?:CLIENTE|EMPRESA)[:\.]*\s*(.*?)(?:\n|$)", re.IGNORECASE)
    RE_BENEFICIARIO= re.compile(r"BENEFICIARIO:\s*(.*?)(?:NOME|CNPJ|CPF|$)", re.IGNORECASE | re.DOTALL)
    RE_DADOS_REC   = re.compile(r"DADOS DO RECEBEDOR.*?NOME\s*[:\.]?\s*(.*?)(?:CPF|CNPJ|$)", re.IGNORECASE | re.DOTALL)
    RE_CREDITADO   = re.compile(r"Creditado\s*\n\s*(.*?)\s*\n", re.IGNORECASE)
    RE_PARA        = re.compile(r"(?:PARA|FAVORECIDO|RECEBEDOR)[:\s]\s*(.*?)(?:\n|$)", re.IGNORECASE)

    # Regex de Conta
    RE_CONTAS = [
        re.compile(r"C\.CORRENTE[\.\s:]+([\d\.-]+)", re.IGNORECASE),
        re.compile(r"CONTA CORRENTE\s*([\d\.-]+)", re.IGNORECASE),
        re.compile(r"AGÊNCIA/CONTA.*?[\d\.-]+\s+([\d\.-]+)", re.IGNORECASE),
        re.compile(r"CONTA[:\.\s]*([\d\.-]+)", re.IGNORECASE)
    ]

    def __init__(self, texto):
        self.texto = texto
        self.texto_limpo = " ".join(texto.split())
        self.texto_sem_acento = self.remover_acentos(self.texto_limpo.upper())

    def remover_acentos(self, txt):
        return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

    def limpar_string(self, s):
        if not s: return None
        s = re.sub(r'[<>:"/\\|?*]', '', s).replace("\n", " ").strip()
        return s[:50]

    def converter_mes(self, mes_nome):
        mes_nome = self.remover_acentos(mes_nome.upper())
        return self.MESES.get(mes_nome, '00')

    def formatar_data(self, data_str):
        d, m, y = data_str.split('/')
        return f"{y}-{m}-{d}"

    def get_data(self):
        # 1. Colisão BB (Duas Datas)
        match = self.RE_DATA_DUPLA.search(self.texto_limpo)
        if match: return self.formatar_data(match.group(2))

        # 2. Data colada no valor
        match = self.RE_DATA_COLADA.search(self.texto_limpo)
        if match:
            # Check negativo para Vencimento
            inicio = max(0, match.start() - 25)
            contexto = self.texto_limpo[inicio:match.start()].upper()
            if not self.RE_VENCIMENTO.search(contexto):
                return self.formatar_data(match.group(1))

        # 3. Referencia
        match = self.RE_REF.search(self.texto)
        if match: return self.formatar_data(match.group(1))

        # 4. Pagamento Explicito
        match = self.RE_PAGAMENTO.search(self.texto)
        if match: return self.formatar_data(match.group(1))

        # 5. Generico
        match = self.RE_DATA_GEN.search(self.texto)
        if match: return self.formatar_data(match.group(1))

        # 6. Mês/Ano
        match = self.RE_MES_ANO.search(self.texto)
        if match:
            mes = self.converter_mes(match.group(1))
            if mes != '00': return f"{match.group(2)}-{mes}"

        # 7. MM/AAAA
        match = self.RE_MM_AAAA.search(self.texto)
        if match: return f"{match.group(2)}-{match.group(1)}"

        return "SemData"

    def get_tipo(self):
        s = self.texto_sem_acento
        
        # 1. Documentos Macro
        if "EXTRATO CONSOLIDADO" in s or "EXTRATO DE CONTA" in s: return "EXTRATO"
        if "SERVICO DE FOLHA" in s or "DETALHAMENTO DA REMESSA" in s: return "FOLHA"

        # 2. Pagamentos e Boletos (Correção para o arquivo 558,38)
        # O BB escreve "Codigo de Barras" nos comprovantes de pagamento.
        if "CODIGO DE BARRAS" in s or "LINHA DIGITAVEL" in s: return "BOLETO"
        
        # Captura guias de imposto que as vezes não leem a palavra boleto, mas são pagamentos
        if "FGTS" in s or "DARF" in s or "GRRF" in s or "GPS" in s or "DAE" in s: return "IMPOSTO"

        # 3. Transações Explícitas
        if "PIX" in s: return "PIX"
        if "TED" in s or "TRANSFERENCIA ELETRONICA" in s: return "TED"
        
        # 4. Transferência Interna (Correção para o arquivo 1.300,00)
        # Quando é de BB para BB, ele usa termos específicos
        if "DE CONTA CORRENTE P/" in s or "TRANSFERENCIA ENTRE CONTAS" in s: return "TRANSFERENCIA"

        # 5. Investimentos (Só olha isso depois de garantir que não é pagamento)
        termos_inv = ["INVESTIMENTO", "FUNDO", "RF CP", "CDB", "LCI", "LCA", 
                      "RENTABILIDADE", "APLICACOES FINANCEIRAS", "CP EMPRESA", "RENDA FIXA"]
        for t in termos_inv:
            if t in s: return "RENDIMENTOS"

        # 6. Extratos Genéricos
        if "SALDO ANTERIOR" in s or "LANCAMENTOS" in s or "SALDO TOTAL" in s: return "EXTRATO"
        
        # 7. O "Lixo" (Se não for nada acima, assumimos DOC ou Comprovante Genérico)
        return "DOC"

    def get_valor(self):
        tipo = self.get_tipo()

        if tipo == "FOLHA":
            match = self.RE_VAL_FOLHA1.search(self.texto_sem_acento)
            if match: return match.group(1)
            match = self.RE_VAL_FOLHA2.search(self.texto_sem_acento)
            if match: return match.group(1)

        if tipo in ["EXTRATO", "RENDIMENTOS"]:
            match = self.RE_VAL_EXTRATO.search(self.texto, re.IGNORECASE)
            if match: return match.group(1)

        for regex in self.RE_VAL_GERAL:
            match = regex.search(self.texto_sem_acento)
            if match: return match.group(1)
            
        return "0,00"

    def get_favorecido(self):
        tipo = self.get_tipo()
        if tipo in ["EXTRATO", "RENDIMENTOS", "FOLHA"]:
            match = self.RE_CLIENTE.search(self.texto)
            if match: return self.limpar_string(match.group(1))
            return "Proprio"
        
        match = self.RE_BENEFICIARIO.search(self.texto)
        if match: return self.limpar_string(match.group(1))
        
        match = self.RE_DADOS_REC.search(self.texto)
        if match: return self.limpar_string(match.group(1))

        match = self.RE_CREDITADO.search(self.texto)
        if match: return self.limpar_string(match.group(1))

        match = self.RE_PARA.search(self.texto)
        if match: return self.limpar_string(match.group(1))
        
        return "Desconhecido"

    def get_conta(self):
        for regex in self.RE_CONTAS:
            match = regex.search(self.texto)
            if match: return match.group(1).strip()
        return "ContaGeral"