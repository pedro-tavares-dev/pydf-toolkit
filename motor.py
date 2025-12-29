import re
from unicodedata import normalize

class MotorExtracao:
    """
    MOTOR V4.1 - CORREÇÃO BANESTES
    Ajuste fino para não confundir Saldo com Conta.
    """

    def __init__(self, texto_pdf):
        self.linhas_raw = [l.strip() for l in texto_pdf.split('\n') if l.strip()]
        self.texto_completo = " ".join(self.linhas_raw).upper()
        self.texto_sem_acento = self._normalizar(self.texto_completo)
        
        self.dados = {
            "tipo": "DOC",
            "valor": "0,00",
            "data": None,
            "favorecido": "Desconhecido",
            "conta": "Geral"
        }
        
        self._analisar_estrutura()

    def _normalizar(self, txt):
        return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII').upper()

    def _is_money(self, texto):
        return re.match(r'^R?\s?[\d\.]*,\d{2}$', texto.strip())

    def _is_date(self, texto):
        return re.match(r'^\d{2}/\d{2}/\d{4}$', texto.strip())

    def _analisar_estrutura(self):
        texto_full = self.texto_sem_acento

        # --- 1. CLASSIFICAÇÃO DE TIPO ---
        if "RFB-DARF" in texto_full or "DARF" in texto_full: self.dados["tipo"] = "DARF"
        elif "PIX" in texto_full: self.dados["tipo"] = "PIX"
        elif "EXTRATO" in texto_full: self.dados["tipo"] = "EXTRATO"
        elif "BOLETO" in texto_full or "LINHA DIGITAVEL" in texto_full: self.dados["tipo"] = "BOLETO"
        elif "COMPROVANTE" in texto_full: self.dados["tipo"] = "COMPROVANTE"

        # --- 2. CAPTURA DE CONTA (PRIORIDADE MÁXIMA) ---
        # A lógica antiga estava pegando o saldo. Agora usamos âncoras fortes.
        conta_encontrada = None
        
        # Padrão Banestes Exato: "Conta: XXXXXXX-X"
        match_banestes = re.search(r'CONTA\s*[:\.]\s*(\d{5,10}-?\d{1})', texto_full)
        if match_banestes:
            conta_encontrada = match_banestes.group(1)
        
        # Padrão Genérico: "Agência/Conta: ..."
        elif not conta_encontrada:
            match_ag_cc = re.search(r'(?:AGENCIA|AG)\.?\s*[:\.]?.+?(?:CONTA|C\.C)\.?\s*[:\.]?\s*([\d\.-]+)', texto_full)
            if match_ag_cc:
                conta_encontrada = match_ag_cc.group(1)

        # Se achou, limpa e salva
        if conta_encontrada:
            self.dados["conta"] = conta_encontrada.replace(" ", "").strip()
        
        # --- 3. VARREDURA POSICIONAL (RESTO DOS DADOS) ---
        total_linhas = len(self.linhas_raw)
        
        for i, linha in enumerate(self.linhas_raw):
            linha_norm = self._normalizar(linha)
            
            # VALOR (Ignora se for título de saldo)
            if "VALOR" in linha_norm and "SALDO" not in linha_norm:
                partes = linha.split(':')
                if len(partes) > 1:
                    cand = partes[-1].strip().replace("R$", "").strip()
                    if self._is_money(cand): self.dados["valor"] = cand
                elif i + 1 < total_linhas:
                    cand = self.linhas_raw[i+1].strip().replace("R$", "").strip()
                    if self._is_money(cand): self.dados["valor"] = cand
            
            # Se for EXTRATO, o "Valor" do documento costuma ser o SALDO FINAL
            if self.dados["tipo"] == "EXTRATO" and "SALDO TOTAL" in linha_norm:
                 if i + 1 < total_linhas:
                    cand = self.linhas_raw[i+1].strip().replace("R$", "").strip()
                    if self._is_money(cand): self.dados["valor"] = cand

            # DATA
            if "DATA" in linha_norm and ("PAGAMENTO" in linha_norm or "EMISSAO" in linha_norm or "PERIODO" in linha_norm):
                match_data = re.search(r'(\d{2}/\d{2}/\d{4})', linha)
                if match_data: self.dados["data"] = match_data.group(1)
                elif i + 1 < total_linhas:
                    cand = self.linhas_raw[i+1].strip()
                    if self._is_date(cand): self.dados["data"] = cand

            # FAVORECIDO / CLIENTE
            if "CLIENTE" in linha_norm or "NOME" in linha_norm:
                 partes = linha.split(':')
                 if len(partes) > 1 and len(partes[1]) > 3:
                     self.dados["favorecido"] = self._limpar_nome(partes[1])

        # --- FALLBACKS ---
        if self.dados["valor"] == "0,00":
             # Em extratos, pega o maior valor (geralmente saldo)
             valores = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})', texto_full)
             if valores: self.dados["valor"] = valores[-1]
             
        if not self.dados["data"]:
            datas = re.findall(r'(\d{2}/\d{2}/\d{4})', texto_full)
            if datas: self.dados["data"] = datas[-1] # Extratos: data final é melhor

    def _limpar_nome(self, nome):
        if not nome: return "Desconhecido"
        nome = re.sub(r'[<>:"/\\|?*]', '', nome).strip()
        nome = nome.replace("BANCO DO BRASIL", "").replace("S.A.", "").strip()
        return nome if len(nome) > 2 else "Desconhecido"

    # MÉTODOS PÚBLICOS
    def get_valor(self): return self.dados["valor"]
    def get_tipo(self): return self.dados["tipo"]
    def get_data(self): return self.dados["data"] if self.dados["data"] else "00-00-0000"
    def get_conta(self): return self.dados["conta"]
    def get_favorecido(self): return self.dados["favorecido"]