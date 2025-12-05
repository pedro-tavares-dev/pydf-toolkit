import sys
import os
from pikepdf import Pdf  # A Turbina C++
from biblioteca_logs import configurar_logger

# Configura o log
log = configurar_logger("juntar")

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
    
    arquivos.sort()
    
    if not arquivos:
        # Encerramento forçado imediato
        os._exit(0)

    pasta_base = os.path.dirname(arquivos[0])
    nome_saida = "Unificados.pdf"
    caminho_saida = os.path.join(pasta_base, nome_saida)
    
    try:
        log.info(f"--- 🔗 JUNTAR TURBO ({len(arquivos)} arquivos) ---")
        
        pdf_novo = Pdf.new()
        
        count = 0
        for arq in arquivos:
            if os.path.basename(arq) == nome_saida:
                continue

            try:
                src = Pdf.open(arq)
                pdf_novo.pages.extend(src.pages)
                count += 1
            except Exception as e:
                log.error(f"Erro ao ler {os.path.basename(arq)}: {e}")

        if count > 0:
            pdf_novo.save(caminho_saida)
            log.info(f"✅ SUCESSO! {count} arquivos unidos.")
        else:
            log.warning("Nenhum arquivo válido.")
        
    except Exception as e:
        log.critical(f"Erro fatal: {e}")
        os._exit(1)

if __name__ == "__main__":
    main()
    # os._exit(0) não espera nada, ele mata o processo na hora.
    os._exit(0)