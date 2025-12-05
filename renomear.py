import sys
import os
import time
import re
from pypdf import PdfReader
from motor import MotorExtracao
from biblioteca_logs import configurar_logger

# Configura o logger
log = configurar_logger("renomear")

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

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
    print(f"=== 🏷️  RENOMEAR ({len(arquivos)} ARQUIVOS) ===")
    print("1 - Favorecido_Valor")
    print("2 - Tipo_Valor")
    print("3 - Valor_Tipo")  # <--- NOVA OPÇÃO
    print("6 - Tipo_Conta_Data (Extratos)")
    print("7 - Conta_Tipo_Data (Investimentos)")
    print("9 - EXT+REN_Conta_Data (Automático)")
    print("0 - Sair")
    
    opt = input("Opção >> ")
    
    if opt in ['1', '2', '3', '6', '7', '9']:
        processar(arquivos, opt)

def processar(arquivos, opcao):
    log.info(f"Iniciando processo de renomeacao. Modo: {opcao}")
    
    for pdf_path in arquivos:
        try:
            pasta = os.path.dirname(pdf_path)
            ext = os.path.splitext(pdf_path)[1]
            nome_original = os.path.basename(pdf_path)
            
            leitor = PdfReader(pdf_path)
            
            # Le ate 3 paginas para o motor buscar
            texto = ""
            for i in range(min(3, len(leitor.pages))): 
                try:
                    texto += leitor.pages[i].extract_text() + "\n"
                except: 
                    pass
            
            motor = MotorExtracao(texto)
            
            # Extração dos dados
            fav = motor.get_favorecido()
            tipo = motor.get_tipo()
            conta = motor.get_conta()
            data = motor.get_data()
            
            # --- TRATAMENTO DO VALOR (Retirar pontos de milhar) ---
            raw_val = motor.get_valor() # Ex: 1.500,00
            val = raw_val.replace('.', '') if raw_val else "0,00" # Ex: 1500,00
            # ------------------------------------------------------

            # Log de auditoria
            log.info(f"Analisando '{nome_original}': Tipo={tipo}, Conta={conta}, Data={data}, Valor={raw_val} -> {val}")

            novo = ""
            
            # Lógica de Montagem do Nome
            if opcao == '1': 
                novo = f"{fav}_{val}"
            elif opcao == '2': 
                novo = f"{tipo}_{val}"
            elif opcao == '3':
                novo = f"{val}_{tipo}"
            elif opcao == '6': 
                novo = f"{tipo}_{conta}_{data}"
            elif opcao == '7': 
                novo = f"{conta}_{tipo}_{data}"
            elif opcao == '9': 
                novo = f"EXT+REN_{conta}_{data}"

            # Limpeza final do nome do arquivo
            # Remove __ duplicados e troca espaços por _
            novo = novo.replace("__", "_").replace(" ", "_")
            
            caminho_novo = os.path.join(pasta, f"{novo}{ext}")
            
            # Evita sobrescrever arquivos existentes (adiciona _1, _2...)
            c = 1
            while os.path.exists(caminho_novo):
                # Se o arquivo for o mesmo (já renomeado), para.
                if os.path.abspath(caminho_novo) == os.path.abspath(pdf_path):
                    break
                caminho_novo = os.path.join(pasta, f"{novo}_{c}{ext}")
                c += 1
            
            # Executa o rename
            if os.path.abspath(caminho_novo) != os.path.abspath(pdf_path):
                os.rename(pdf_path, caminho_novo)
                log.info(f" -> Renomeado para: {os.path.basename(caminho_novo)}")
                print(f" > {os.path.basename(caminho_novo)}")
            else:
                log.info(f" -> Arquivo ja estava com o nome correto ou ignorado.")
            
        except Exception as e:
            log.error(f"Erro ao processar {nome_original}: {e}")
            print(f"Erro no arquivo {nome_original}: {e}")
    
    log.info("Processo finalizado.")
    time.sleep(1)

if __name__ == "__main__":
    main()