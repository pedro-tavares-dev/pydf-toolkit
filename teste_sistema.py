import os
import sys
import shutil
import time
import subprocess
from pypdf import PdfWriter, PdfReader

# Tenta importar o Motor para teste lógico
try:
    from motor import MotorExtracao
    MOTOR_DISPONIVEL = True
except ImportError:
    MOTOR_DISPONIVEL = False

# Cores para o Terminal
VERDE = "\033[92m"
VERMELHO = "\033[91m"
AMARELO = "\033[93m"
RESET = "\033[0m"

DIR_TESTE = os.path.join(os.getcwd(), "teste")

# --- AMBIENTE UTF-8 (Vacina para Windows) ---
ENV_UTF8 = os.environ.copy()
ENV_UTF8["PYTHONUTF8"] = "1"

def log_pass(msg):
    print(f"{VERDE}[PASS]{RESET} {msg}")

def log_fail(msg):
    print(f"{VERMELHO}[FAIL]{RESET} {msg}")

def log_info(msg):
    print(f"{AMARELO}[INFO]{RESET} {msg}")

def criar_pdf_fake(nome_arquivo, paginas, texto_conteudo="Teste"):
    caminho = os.path.join(DIR_TESTE, nome_arquivo)
    writer = PdfWriter()
    for i in range(paginas):
        writer.add_blank_page(width=200, height=200)
    writer.add_metadata({"/Title": texto_conteudo})
    with open(caminho, "wb") as f:
        writer.write(f)
    return caminho

def setup_ambiente():
    if os.path.exists(DIR_TESTE):
        shutil.rmtree(DIR_TESTE)
    os.makedirs(DIR_TESTE)
    
    log_info("Gerando PDFs de teste (Mock)...")
    criar_pdf_fake("teste1.pdf", 1, "Arquivo pagina unica")
    criar_pdf_fake("teste2.pdf", 2, "Arquivo pagina dupla") # Usado no Smart e no Fatiar
    criar_pdf_fake("teste_pix.pdf", 1, "PIX VALOR 100,00") 

def teste_fatiar():
    print(f"\n--- TESTE 1: FATIAR PADRÃO (dividir.py) ---")
    alvo = os.path.join(DIR_TESTE, "teste2.pdf")
    
    cmd = [sys.executable, "dividir.py", alvo]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=ENV_UTF8)
    
    pasta_esperada = os.path.join(DIR_TESTE, "teste2_fatiado")
    
    if os.path.exists(pasta_esperada):
        arquivos = os.listdir(pasta_esperada)
        if len(arquivos) == 2:
            log_pass("Pasta criada com 2 arquivos divididos.")
        else:
            log_fail(f"Pasta criada, mas quantidade errada: {len(arquivos)} arquivos.")
    else:
        log_fail("Falha ao dividir teste2.pdf (Pasta nao encontrada)")
        print(proc.stderr)

def teste_juntar():
    print(f"\n--- TESTE 2: JUNTAR (juntar.py) ---")
    # Usa a pasta criada pelo Teste 1
    pasta_alvo = os.path.join(DIR_TESTE, "teste2_fatiado")
    
    if not os.path.exists(pasta_alvo):
        log_fail("Impossivel testar Juntar: Pasta do teste anterior nao existe.")
        return

    cmd = [sys.executable, "juntar.py", pasta_alvo]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=ENV_UTF8)
    
    arquivo_esperado = os.path.join(pasta_alvo, "Unificados.pdf")
    
    if os.path.exists(arquivo_esperado):
        reader = PdfReader(arquivo_esperado)
        if len(reader.pages) == 2:
            log_pass(f"Arquivo Unificados.pdf gerado com 2 paginas.")
        else:
            log_fail(f"Arquivo gerado mas paginas incorretas: {len(reader.pages)}")
    else:
        log_fail(f"Arquivo Unificados.pdf nao foi criado em {pasta_alvo}")
        print(f"Log Script: {proc.stderr}")

def teste_smart():
    print(f"\n--- TESTE 3: DIVIDIR SMART (dividir_smart.py) ---")
    alvo = os.path.join(DIR_TESTE, "teste2.pdf")
    
    cmd = [sys.executable, "dividir_smart.py", alvo]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', env=ENV_UTF8)
    
    arquivo_esperado_1 = os.path.join(DIR_TESTE, "teste2_Pag01.pdf")
    arquivo_esperado_2 = os.path.join(DIR_TESTE, "teste2_Pag02.pdf")
    
    if os.path.exists(arquivo_esperado_1) and os.path.exists(arquivo_esperado_2):
        log_pass("Smart Split executado com sucesso (Arquivos gerados na raiz).")
    else:
        log_fail("Falha no Smart Split (Arquivos não encontrados na raiz).")
        print(f"Log de Erro: {proc.stderr}")
        print(f"Output: {proc.stdout}")

def teste_logica_renomear():
    print(f"\n--- TESTE 4: LOGICA DE RENOMEACAO (Motor + Regex) ---")
    
    if not MOTOR_DISPONIVEL:
        log_fail("Arquivo motor.py nao encontrado.")
        return

    texto_fake_pix = "COMPROVANTE DE TRANSFERENCIA\nPIX\nVALOR: 1.500,00"
    texto_fake_boleto = "COMPROVANTE DE PAGAMENTO\nCODIGO DE BARRAS: 8364\nVALOR COBRADO: 558,38"

    motor1 = MotorExtracao(texto_fake_pix)
    if motor1.get_tipo() == "PIX": log_pass("Detecção PIX OK")
    else: log_fail("Erro PIX")

    motor2 = MotorExtracao(texto_fake_boleto)
    if motor2.get_tipo() == "BOLETO": log_pass("Detecção Boleto OK")
    else: log_fail("Erro Boleto")

def main():
    print(f"{VERDE}=== INICIANDO SISTEMA DE AUTO-DIAGNOSTICO PYDF ==={RESET}")
    setup_ambiente()
    teste_fatiar()
    teste_juntar()
    teste_smart()
    teste_logica_renomear()
    print(f"\n{VERDE}=== FIM ==={RESET}")

if __name__ == "__main__":
    main()