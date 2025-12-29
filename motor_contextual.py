import re
from unicodedata import normalize

class MotorContextual:
    """
    MOTOR NIVEL STARTUP:
    Não usa apenas Regex. Usa Tokenização e Análise Posicional.
    Lê o PDF como um humano: Identifica o Rótulo -> Pega o Valor associado.
    """

    def __init__(self, texto_pdf):
        # 1. Limpeza e Tokenização (Quebra o texto em linhas limpas)
        self.linhas_raw = [l.strip() for l in texto_pdf.split('\n') if l.strip()]
        self.texto_completo = " ".join(self.linhas_raw).upper()
        self.dados = {
            "tipo": "DESCONHECIDO",
            "valor": "0,00",
            "data": None,
            "favorecido": None,
            "pagador": None,
            "banco": "DESCONHECIDO"
        }
        
        # Executa a pipeline de inteligencia
        self._analisar_estrutura()

    def _normalizar(self, txt):
        return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII').upper()

    def _is_money(self, texto):
        # Verifica se a string parece dinheiro (ex: 52,50 ou 1.000,00)
        return re.match(r'^R?\s?[\d\.]*,\d{2}$', texto.strip())

    def _is_date(self, texto):
        # Verifica se a string é uma data
        return re.match(r'^\d{2}/\d{2}/\d{4}$', texto.strip())

    def _analisar_estrutura(self):
        """
        O CORAÇÃO DO MOTOR:
        Varre as linhas procurando 'Gatilhos' e captura o conteúdo adjacente.
        """
        
        # --- 1. Identificação do Banco e Tipo (Via Palavras-Chave Globais) ---
        if "BANCO DO BRASIL" in self.texto_completo:
            self.dados["banco"] = "BANCO DO BRASIL"
        elif "BANESTES" in self.texto_completo:
            self.dados["banco"] = "BANESTES"

        # Detecção de Tipo baseada em cabeçalhos fortes
        if "RFB-DARF" in self.texto_completo or "DARF" in self.texto_completo: # 
            self.dados["tipo"] = "IMPOSTO_DARF"
        elif "PAGAMENTO" in self.texto_completo and "BOLETO" in self.texto_completo:
            self.dados["tipo"] = "PAGAMENTO_BOLETO"
        elif "PIX" in self.texto_completo:
            self.dados["tipo"] = "PIX"

        # --- 2. LOOP INTELIGENTE (LINHA A LINHA) ---
        # Aqui está a mágica. Iteramos pelo índice para olhar "para frente" e "para trás".
        
        total_linhas = len(self.linhas_raw)
        
        for i, linha in enumerate(self.linhas_raw):
            linha_norm = self._normalizar(linha)
            
            # --- LÓGICA DE CAPTURA DE VALOR ---
            # Se encontrar "VALOR TOTAL", "VALOR PAGO", etc.
            if "VALOR" in linha_norm and ("TOTAL" in linha_norm or "PAGO" in linha_norm or "DOCUMENTO" in linha_norm):
                # ESTRATÉGIA A: O valor está na MESMA linha? (Ex: Valor: 50,00)
                partes = linha.split(':')
                if len(partes) > 1 and self._is_money(partes[1].strip()):
                    self.dados["valor"] = partes[1].strip()
                
                # ESTRATÉGIA B: O valor está na PRÓXIMA linha? (Comum no BB) 
                elif i + 1 < total_linhas:
                    proxima_linha = self.linhas_raw[i+1].strip()
                    # Remove R$ se tiver e checa
                    limpa = proxima_linha.replace("R$", "").strip()
                    if self._is_money(limpa):
                        self.dados["valor"] = limpa

            # --- LÓGICA DE CAPTURA DE DATA ---
            # Procura "DATA DO PAGAMENTO" ou "DATA"
            if "DATA" in linha_norm and ("PAGAMENTO" in linha_norm or "EFETIVACAO" in linha_norm): # 
                # Verifica próxima linha 
                if i + 1 < total_linhas:
                    cand = self.linhas_raw[i+1].strip()
                    if self._is_date(cand):
                        self.dados["data"] = cand
            
            # --- LÓGICA DE CAPTURA DE FAVORECIDO/CLIENTE ---
            if "CLIENTE" in linha_norm or "NOME" in linha_norm: # [cite: 8]
                # Pega o que vem depois dos dois pontos
                partes = linha.split(':')
                if len(partes) > 1 and len(partes[1]) > 3:
                    self.dados["pagador"] = partes[1].strip()

            if "AGENTE ARRECADADOR" in linha_norm: # [cite: 14]
                 # Logica especifica para DARF/Impostos onde o BB recebe
                 self.dados["favorecido"] = "RECEITA FEDERAL / ORGAO PUBLICO"

    def extrair(self):
        return self.dados

# --- SIMULAÇÃO COM O SEU ARQUIVO ---
# Copiei o texto exato do seu arquivo 52,50_Desconhecido.pdf
conteudo_pdf_simulado = """
17/12/2025, 10:09
SISTEMA DE INFORMACOES BANCO DO BRASIL
SISBB
17/12/2025
0312300312
AUTOATENDIMENTO
SEGUNDA VIA
COMPROVANTE DE PAGAMENTO
CLIENTE: INVISA INSTITUTO VIDA ES
AGENCIA: 0312-3 CONTA:
29.647-3
10.09.08
0001
Convenio RFB-DARF CODIGO DE BARRAS
Agente Arrecadador: CNC 001 Banco do Brasil S.A.
Codigo de Barras
85880000000-8 52500385253-6
53070125343-0
08003382220-2
Data do pagamento
16/12/2025
Numero do Documento
07.01.25343.0800338-2
Valor Total
52,50
Modelo aprovado pelo Ato Declaratorio Executivo
"""

motor = MotorContextual(conteudo_pdf_simulado)
resultado = motor.extrair()

print("-" * 30)
print("🤖 RESULTADO DA I.A. LÓGICA:")
print(f"🏦 Banco: {resultado['banco']}")
print(f"📄 Tipo: {resultado['tipo']}")
print(f"💰 Valor: R$ {resultado['valor']}")
print(f"📅 Data: {resultado['data']}")
print(f"👤 Pagador: {resultado['pagador']}")
print("-" * 30)