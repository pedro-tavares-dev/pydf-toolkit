import sys
import os
import time
from pypdf import PdfReader
from motor import MotorExtracao # Seu novo motor V4 (camuflado)
from biblioteca_logs import configurar_logger

# Configura o logger
log = configurar_logger("renomear")

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def formatar_data_iso(data_str):
    """Transforma DD/MM/AAAA em AAAA-MM-DD para ordenação correta no Windows"""
    try:
        if not data_str or len(data_str) != 10: return "0000-00-00"
        d, m, y = data_str.split('/')
        return f"{y}-{m}-{d}"
    except:
        return data_str.replace("/", "-")

def main():
    inputs = sys.argv[1:]
    arquivos = []
    
    # Se nao tiver argumentos, usa a pasta atual
    if not inputs: 
        inputs = [os.getcwd()]
    
    for item in inputs:
        if os.path.isdir(item):
            for f in os.listdir(item):
                if f.lower().endswith('.pdf'): 
                    arquivos.append(os.path.join(item, f))
        elif os.path.isfile(item) and item.lower().endswith('.pdf'):
            arquivos.append(item)
    
    arquivos.sort()

    if not arquivos: 
        print("Nenhum arquivo PDF encontrado.")
        return

    limpar_tela()
    print(f"=== 🏷️  RENOMEAR MASTER ({len(arquivos)} ARQUIVOS) ===")
    print("=========================================")
    
    print("--- 💰 FOCO EM VALOR ---")
    print("1  - Valor_Favorecido          (150,00_AMAZON)")
    print("2  - Valor_Data_Favorecido     (150,00_2025-12-17_AMAZON)")
    print("3  - Valor_Tipo                (150,00_PIX)")
    print("4  - Apenas Valor              (150,00)")

    print("\n--- 👤 FOCO EM FAVORECIDO ---")
    print("5  - Favorecido_Valor          (AMAZON_150,00)")
    print("6  - Favorecido_Data_Valor     (AMAZON_2025-12-17_150,00)")
    print("7  - Favorecido_Tipo_Valor     (AMAZON_PIX_150,00)")
    
    print("\n--- 📅 FOCO EM DATA (ORDENAÇÃO PERFEITA) ---")
    print("8  - DataISO_Favorecido_Valor  (2025-12-17_AMAZON_150,00)")
    print("9  - DataISO_Valor_Favorecido  (2025-12-17_150,00_AMAZON)")
    print("10 - DataISO_Tipo_Valor        (2025-12-17_PIX_150,00)")
    print("11 - Ano_Mes_Favorecido        (2025-12_AMAZON)")

    print("\n--- 📂 FOCO TÉCNICO/CONTÁBIL ---")
    print("12 - Tipo_Valor_Data           (PIX_150,00_17-12-2025)")
    print("13 - Tipo_Favorecido_Valor     (PIX_AMAZON_150,00)")
    print("14 - Conta_Tipo_Data           (12345_EXTRATO_2025...)")
    print("15 - Tipo_Conta_Data           (EXTRATO_12345_2025...)")
    
    print("\n--- 🚀 COMBINAÇÕES COMPLETAS ---")
    print("16 - DataISO_Tipo_Fav_Valor    (2025-12-17_PIX_AMAZON_150,00)")
    print("17 - Favorecido_Tipo_Data_Val  (AMAZON_PIX_17-12-2025_150,00)")
    print("18 - [CONTABIL] Data_Val_Tipo  (2025-12-17_150,00_PIX)")
    print("19 - [BANCARIO] Conta_Val_Dat  (12345_150,00_2025-12-17)")
    print("20 - Automático (EXT+REN)      (EXT+REN_12345_2025...)")
    print("=========================================")
    print("0 - Sair")
    
    opt = input("\nEscolha uma opção (1-20) >> ")
    
    # Valida se é um numero entre 1 e 20
    if opt.isdigit() and 1 <= int(opt) <= 20:
        processar(arquivos, opt)

def processar(arquivos, opcao):
    log.info(f"Iniciando processo de renomeacao. Modo: {opcao}")
    
    for pdf_path in arquivos:
        try:
            pasta = os.path.dirname(pdf_path)
            ext = os.path.splitext(pdf_path)[1]
            nome_original = os.path.basename(pdf_path)
            
            # --- LEITURA DO PDF ---
            leitor = PdfReader(pdf_path)
            texto = ""
            # Lê até 3 páginas para garantir
            for i in range(min(3, len(leitor.pages))): 
                try:
                    texto += leitor.pages[i].extract_text() + "\n"
                except: pass
            
            # --- MOTOR V4 EM AÇÃO ---
            motor = MotorExtracao(texto)
            
            # Extração dos dados
            fav = motor.get_favorecido()
            tipo = motor.get_tipo()
            conta = motor.get_conta()
            
            # Tratamento de DATA
            data_raw = motor.get_data() # DD/MM/AAAA
            data_iso = formatar_data_iso(data_raw) # AAAA-MM-DD (Para ordenar)
            data_pt = data_raw.replace("/", "-")   # DD-MM-AAAA (Para ler)
            
            # Tratamento de VALOR
            raw_val = motor.get_valor() 
            val = raw_val.replace('.', '') if raw_val else "0,00" 
            
            # Log
            log.info(f"'{nome_original}' -> {tipo} | R$ {val} | {fav} | {data_iso}")

            novo = ""
            
            # === SUPER MENU DE OPÇÕES ===
            
            # --- VALOR ---
            if opcao == '1':   novo = f"{val}_{fav}"
            elif opcao == '2': novo = f"{val}_{data_iso}_{fav}"
            elif opcao == '3': novo = f"{val}_{tipo}"
            elif opcao == '4': novo = f"{val}"
            
            # --- FAVORECIDO ---
            elif opcao == '5': novo = f"{fav}_{val}"
            elif opcao == '6': novo = f"{fav}_{data_iso}_{val}"
            elif opcao == '7': novo = f"{fav}_{tipo}_{val}"
            
            # --- DATA (ISO) ---
            elif opcao == '8':  novo = f"{data_iso}_{fav}_{val}"
            elif opcao == '9':  novo = f"{data_iso}_{val}_{fav}"
            elif opcao == '10': novo = f"{data_iso}_{tipo}_{val}"
            elif opcao == '11': novo = f"{data_iso[:7]}_{fav}" # Apenas Ano-Mes
            
            # --- TÉCNICO ---
            elif opcao == '12': novo = f"{tipo}_{val}_{data_pt}"
            elif opcao == '13': novo = f"{tipo}_{fav}_{val}"
            elif opcao == '14': novo = f"{conta}_{tipo}_{data_pt}"
            elif opcao == '15': novo = f"{tipo}_{conta}_{data_pt}"
            
            # --- COMPLETOS ---
            elif opcao == '16': novo = f"{data_iso}_{tipo}_{fav}_{val}"
            elif opcao == '17': novo = f"{fav}_{tipo}_{data_pt}_{val}"
            elif opcao == '18': novo = f"{data_iso}_{val}_{tipo}"
            elif opcao == '19': novo = f"{conta}_{val}_{data_iso}"
            elif opcao == '20': novo = f"EXT+REN_{conta}_{data_pt}"

            # === LIMPEZA FINAL DO NOME ===
            # Remove caracteres proibidos no Windows e deixa bonito
            novo = novo.replace("__", "_").replace(" ", "_")
            novo = novo.replace(":", "").replace("\\", "").replace("/", "-")
            novo = novo.replace("<", "").replace(">", "").replace("|", "")
            novo = novo.replace("*", "").replace("?", "").replace('"', "")
            
            caminho_novo = os.path.join(pasta, f"{novo}{ext}")
            
            # Evita sobrescrever (Incrementa _1, _2, etc)
            c = 1
            while os.path.exists(caminho_novo):
                if os.path.abspath(caminho_novo) == os.path.abspath(pdf_path):
                    break
                caminho_novo = os.path.join(pasta, f"{novo}_{c}{ext}")
                c += 1
            
            # Executa
            if os.path.abspath(caminho_novo) != os.path.abspath(pdf_path):
                os.rename(pdf_path, caminho_novo)
                print(f"✅ {nome_original} -> {os.path.basename(caminho_novo)}")
            else:
                print(f"⚠️  {nome_original} (Mantido)")
            
        except Exception as e:
            log.error(f"Erro ao processar {nome_original}: {e}")
            print(f"❌ Erro em {nome_original}: {e}")
    
    log.info("Processo finalizado.")
    print("\n✨ Tudo pronto, Chefe! ✨")
    time.sleep(2)

if __name__ == "__main__":
    main()