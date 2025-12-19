import sys
import os
import logging
from pikepdf import Pdf 

# --- CONFIGURAÇÃO DE LOGS ---
# Ajustei para usar o logging nativo para garantir que funcione sozinho
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s', # Formato limpo apenas com a mensagem
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("juntar")

def main():
    inputs = sys.argv[1:]
    
    # Se não tiver argumentos, usa a pasta atual para teste
    if not inputs: 
        inputs = [os.getcwd()]
    
    arquivos = []
    
    # Varre as entradas (arquivos ou pastas)
    for item in inputs:
        if os.path.isdir(item):
            for f in os.listdir(item):
                if f.lower().endswith('.pdf'): 
                    arquivos.append(os.path.join(item, f))
        elif os.path.isfile(item) and item.lower().endswith('.pdf'):
            arquivos.append(item)
    
    # Ordena alfabeticamente para manter coerência
    arquivos.sort()
    
    if not arquivos:
        log.warning("⚠️  Nenhum arquivo PDF encontrado.")
        return

    pasta_base = os.path.dirname(arquivos[0])
    
    # --- CONFIGURAÇÃO DE SAÍDA ---
    nome_saida = "Unificados_CMD.pdf"
    caminho_saida = os.path.join(pasta_base, nome_saida)
    
    # Evita sobrescrever se já existir
    contador = 1
    while os.path.exists(caminho_saida):
        caminho_saida = os.path.join(pasta_base, f"Unificados{contador}.pdf")
        contador += 1
    
    try:
        log.info(f"\n🚀 INICIANDO MODO TURBO CMD...")
        log.info(f"📂 Processando {len(arquivos)} arquivos...")
        
        pdf_novo = Pdf.new()
        count = 0
        
        for arq in arquivos:
            # Pula o próprio arquivo de saída se ele estiver na lista
            if os.path.abspath(arq) == os.path.abspath(caminho_saida):
                continue

            try:
                src = Pdf.open(arq)
                pdf_novo.pages.extend(src.pages)
                count += 1
                print(f"  OK: {os.path.basename(arq)}") # Print simples para feedback rápido
            except Exception as e:
                log.error(f"❌ Erro em {os.path.basename(arq)}: {e}")

        if count > 0:
            pdf_novo.save(caminho_saida)
            log.info(f"\n✅ SUCESSO! Arquivo gerado:")
            log.info(f"📄 {caminho_saida}\n")
        else:
            log.warning("⚠️  Nenhum arquivo válido processado.")
        
    except Exception as e:
        log.critical(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    main()