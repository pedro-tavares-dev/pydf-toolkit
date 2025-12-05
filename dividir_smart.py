import sys
import os
import time
from pypdf import PdfReader, PdfWriter

# Tenta importar o motor
try:
    from motor import MotorExtracao
except ImportError:
    # Fallback silencioso para evitar crash se o motor não existir
    print("⚠️ Motor não encontrado. Usando modo fallback.")
    class MotorExtracao:
        def __init__(self, texto): pass
        def get_valor(self): return "0,00"
        def get_tipo(self): return "DESCONHECIDO"

def main():
    try:
        inputs = sys.argv[1:]
        if not inputs: 
            inputs = [os.getcwd()]

        arquivos_para_processar = []

        # Varredura de arquivos
        for item in inputs:
            if os.path.isdir(item):
                print(f"📂 Varrendo pasta: {item}...")
                for f in os.listdir(item):
                    if f.lower().endswith('.pdf'):
                        arquivos_para_processar.append(os.path.join(item, f))
            elif os.path.isfile(item) and item.lower().endswith('.pdf'):
                arquivos_para_processar.append(item)

        if not arquivos_para_processar:
            print("❌ Nenhum PDF encontrado.")
            sys.exit(0)

        print(f"\nIniciando Divisão Smart ({len(arquivos_para_processar)} arquivos)...")
        print("Padrão: [VALOR].pdf (Salvo na raiz)")
        
        for pdf_path in arquivos_para_processar:
            try:
                leitor = PdfReader(pdf_path)
                
                # --- MODO FLAT: Usamos a própria pasta de origem ---
                pasta_origem = os.path.dirname(pdf_path)
                nome_base_orig = os.path.splitext(os.path.basename(pdf_path))[0]
                # ---------------------------------------------------
                
                print(f"\n > Processando: {os.path.basename(pdf_path)}")

                for i, pagina in enumerate(leitor.pages):
                    texto_pagina = pagina.extract_text() or ""
                    
                    motor = MotorExtracao(texto_pagina)
                    valor = motor.get_valor()
                    valor_ordenavel = valor.replace('.', '') 
                    
                    if valor != "0,00":
                        nome_novo_base = f"{valor_ordenavel}"
                        print(f"   💰 Pág {i+1}: {nome_novo_base}")
                    else:
                        nome_novo_base = f"{nome_base_orig}_Pag{i+1:02d}"
                        print(f"   ⚠️ Pág {i+1}: Sem valor -> {nome_novo_base}")

                    escritor = PdfWriter()
                    escritor.add_page(pagina)
                    
                    nome_limpo = nome_novo_base.replace("/", "-").replace(":", "")
                    nome_final = f"{nome_limpo}.pdf"
                    
                    # Salva direto na pasta de origem
                    caminho_final = os.path.join(pasta_origem, nome_final)
                    
                    # Resolve duplicatas (ex: se tiver dois boletos com mesmo valor)
                    contador = 1
                    while os.path.exists(caminho_final):
                        caminho_final = os.path.join(pasta_origem, f"{nome_limpo}_{contador}.pdf")
                        contador += 1
                    
                    with open(caminho_final, "wb") as f_saida:
                        escritor.write(f_saida)

            except Exception as e_interno:
                print(f"   ❌ Erro ao ler {os.path.basename(pdf_path)}: {e_interno}")

        print("\n✅ CONCLUÍDO!")
        time.sleep(1.5) # Pausa rápida para ler o log antes de fechar

    except Exception as e:
        print(f"\n⛔ ERRO CRÍTICO GLOBAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0)