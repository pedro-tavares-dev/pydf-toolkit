import sys
import os
from pypdf import PdfReader, PdfWriter

# Tenta importar o motor
try:
    from motor import MotorExtracao
except ImportError:
    # Para evitar travar se rodar isolado sem o motor, criamos um mock simples
    print("⚠️ Motor não encontrado. Usando modo fallback (sem detecção de valor).")
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
            sys.exit(0) # Sai rápido se não tiver nada

        print(f"\nIniciando Divisão Smart ({len(arquivos_para_processar)} arquivos)...")
        print("Padrão: [VALOR].pdf (Sem data, sem pontos)")
        
        for pdf_path in arquivos_para_processar:
            try:
                leitor = PdfReader(pdf_path)
                
                # --- LÓGICA DE PASTAS ---
                pasta_origem = os.path.dirname(pdf_path)
                nome_base_orig = os.path.splitext(os.path.basename(pdf_path))[0]
                
                # Define e cria a pasta _SMART
                nome_pasta_smart = f"{nome_base_orig}_SMART"
                caminho_pasta_smart = os.path.join(pasta_origem, nome_pasta_smart)
                os.makedirs(caminho_pasta_smart, exist_ok=True)
                # -------------------------
                
                print(f"\n > Processando: {os.path.basename(pdf_path)}")
                print(f"   📂 Salvando em: {nome_pasta_smart}")

                for i, pagina in enumerate(leitor.pages):
                    texto_pagina = pagina.extract_text() or "" # Garante string
                    
                    motor = MotorExtracao(texto_pagina)
                    valor = motor.get_valor()
                    
                    # Remove o ponto de milhar para ordenação correta
                    valor_ordenavel = valor.replace('.', '') 
                    
                    if valor != "0,00":
                        nome_novo_base = f"{valor_ordenavel}"
                        print(f"   💰 Pág {i+1}: {nome_novo_base}")
                    else:
                        nome_novo_base = f"{nome_base_orig}_Pag{i+1:02d}"
                        print(f"   ⚠️ Pág {i+1}: Sem valor detectado -> {nome_novo_base}")

                    escritor = PdfWriter()
                    escritor.add_page(pagina)
                    
                    # Limpeza básica e montagem do caminho
                    nome_limpo = nome_novo_base.replace("/", "-").replace(":", "")
                    nome_final = f"{nome_limpo}.pdf"
                    caminho_final = os.path.join(caminho_pasta_smart, nome_final)
                    
                    # Resolve duplicatas
                    contador = 1
                    while os.path.exists(caminho_final):
                        caminho_final = os.path.join(caminho_pasta_smart, f"{nome_limpo}_{contador}.pdf")
                        contador += 1
                    
                    with open(caminho_final, "wb") as f_saida:
                        escritor.write(f_saida)

            except Exception as e_interno:
                print(f"   ❌ Erro ao ler arquivo {os.path.basename(pdf_path)}: {e_interno}")

        print("\n✅ CONCLUÍDO!")

    except Exception as e:
        print(f"\n⛔ ERRO CRÍTICO GLOBAL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    sys.exit(0) # Fecha a janela imediatamente