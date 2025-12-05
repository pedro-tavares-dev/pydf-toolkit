import sys
import os
from pikepdf import Pdf
from biblioteca_logs import configurar_logger

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

log = configurar_logger("dividir")

def main():
    inputs = sys.argv[1:]
    if not inputs: 
        inputs = [os.getcwd()]
    
    arquivos = []
    for item in inputs:
        if os.path.isdir(item):
            for f in os.listdir(item):
                if f.lower().endswith('.pdf'): 
                    arquivos.append(os.path.join(item, f))
        elif os.path.isfile(item) and item.lower().endswith('.pdf'):
            arquivos.append(item)

    if not arquivos:
        sys.exit(0) # Sai imediatamente se não tiver nada

    log.info(f"--- ✂️ FATIADOR TURBO ---")

    for caminho in arquivos:
        try:
            # 1. Identifica origem
            pasta_origem = os.path.dirname(caminho)
            nome_base = os.path.splitext(os.path.basename(caminho))[0]
            
            # log.info(f"Abrindo: {nome_base}...") # Comentado para velocidade visual
            pdf = Pdf.open(caminho)
            
            # 2. Cria pasta
            nome_pasta_saida = f"{nome_base}_fatiado"
            caminho_pasta_saida = os.path.join(pasta_origem, nome_pasta_saida)
            os.makedirs(caminho_pasta_saida, exist_ok=True)

            # 3. Salva as páginas
            total = len(pdf.pages)
            for i, pagina in enumerate(pdf.pages):
                novo_pdf = Pdf.new()
                novo_pdf.pages.append(pagina)
                
                nome_saida = f"{nome_base}_{i+1:02d}.pdf"
                caminho_final = os.path.join(caminho_pasta_saida, nome_saida)
                
                novo_pdf.save(caminho_final)
            
            # Log único de sucesso por arquivo
            log.info(f"✅ {nome_base}: {total} páginas extraídas em /{nome_pasta_saida}")
            
        except Exception as e:
            log.error(f"Erro em {os.path.basename(caminho)}: {e}")

if __name__ == "__main__":
    main()
    sys.exit(0) # Encerramento imediato