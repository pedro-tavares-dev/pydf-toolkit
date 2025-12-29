import sys
import os
import gc # Garbage Collector para limpar memória entre lotes
from pikepdf import Pdf
from biblioteca_logs import configurar_logger

# Configuração para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

log = configurar_logger("dividir")

def processar_lote(arquivos_lote, numero_lote):
    """Processa um grupo específico de arquivos."""
    log.info(f"--- 🚀 Iniciando Lote {numero_lote} com {len(arquivos_lote)} arquivos ---")
    
    for caminho in arquivos_lote:
        try:
            # 1. Identifica origem
            pasta_origem = os.path.dirname(caminho)
            nome_base = os.path.splitext(os.path.basename(caminho))[0]
            
            # 2. Cria pasta de saída
            nome_pasta_saida = f"{nome_base}_fatiado"
            caminho_pasta_saida = os.path.join(pasta_origem, nome_pasta_saida)
            
            # Verifica se já existe para ganhar tempo (opcional)
            if os.path.exists(caminho_pasta_saida) and os.listdir(caminho_pasta_saida):
                log.warning(f"⚠️ Pulei (já existe): {nome_base}")
                continue

            os.makedirs(caminho_pasta_saida, exist_ok=True)

            # 3. Abre e Fatia
            with Pdf.open(caminho) as pdf: # 'with' garante fechamento automático
                total = len(pdf.pages)
                for i, pagina in enumerate(pdf.pages):
                    novo_pdf = Pdf.new()
                    novo_pdf.pages.append(pagina)
                    
                    nome_saida = f"{nome_base}_{i+1:02d}.pdf"
                    caminho_final = os.path.join(caminho_pasta_saida, nome_saida)
                    
                    novo_pdf.save(caminho_final)
            
            log.info(f"✅ {nome_base}: {total} pgs extraídas.")

        except Exception as e:
            log.error(f"❌ Erro em {os.path.basename(caminho)}: {e}")

def main():
    # Coleta inputs
    inputs = sys.argv[1:]
    
    # SE NÃO HOUVER INPUTS (o usuário apenas clicou no script):
    # Pega todos os PDFs da pasta atual automaticamente
    if not inputs: 
        log.info("📂 Modo Varredura: Processando pasta atual...")
        inputs = [os.getcwd()]
    
    arquivos = []
    
    # Varredura inteligente
    for item in inputs:
        if os.path.isdir(item):
            for f in os.listdir(item):
                if f.lower().endswith('.pdf'): 
                    arquivos.append(os.path.join(item, f))
        elif os.path.isfile(item) and item.lower().endswith('.pdf'):
            arquivos.append(item)

    if not arquivos:
        log.warning("Nenhum PDF encontrado.")
        input("Pressione Enter para sair...") # Pausa para ver o erro
        sys.exit(0)

    # --- LÓGICA DE LOTES (BATCHES) ---
    TAMANHO_DO_LOTE = 50 # Processa de 50 em 50 para não travar
    total_arquivos = len(arquivos)
    
    log.info(f"--- ✂️ FATIADOR TURBO (Total: {total_arquivos} arquivos) ---")

    # Divide a lista gigante em pedaços menores
    for i in range(0, total_arquivos, TAMANHO_DO_LOTE):
        lote_atual = arquivos[i : i + TAMANHO_DO_LOTE]
        numero_lote = (i // TAMANHO_DO_LOTE) + 1
        
        processar_lote(lote_atual, numero_lote)
        
        # Limpeza de memória forçada entre lotes
        gc.collect() 
        log.info(f"🧹 Memória limpa após Lote {numero_lote}")

    log.info("--- ✨ Processo Finalizado com Sucesso ✨ ---")
    # input("Pressione Enter para fechar...") # Opcional: manter janela aberta

if __name__ == "__main__":
    main()