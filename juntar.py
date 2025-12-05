import sys
import os
import tkinter as tk
from tkinter import ttk
from pikepdf import Pdf  # A Turbina C++
from biblioteca_logs import configurar_logger

# Importações para o Preview (Visualização)
try:
    import fitz  # PyMuPDF: Para renderizar o PDF como imagem
    from PIL import Image, ImageTk  # Pillow: Para manipular a imagem no Tkinter
    TEM_PREVIEW = True
except ImportError:
    TEM_PREVIEW = False
    print("⚠️ AVISO: Para ver o preview, instale: pip install pymupdf pillow")

# Configura o log
log = configurar_logger("juntar")

class OrganizadorVisual:
    """
    Interface gráfica com PREVIEW para garantir a ordem exata.
    """
    def __init__(self, arquivos):
        self.arquivos_completos = arquivos 
        self.ordem_final = []
        self.cancelado = True

        self.root = tk.Tk()
        self.root.title("Definir Ordem - Juntar PDF")
        
        # Aumentei a janela para caber o preview
        self.root.geometry("900x550")
        
        # Centraliza
        largura_janela = 900
        altura_janela = 550
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        style = ttk.Style()
        style.theme_use('clam')

        # === LAYOUT PRINCIPAL (DIVIDIDO EM DOIS LADOS) ===
        container = ttk.Frame(self.root, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # Lado Esquerdo: Lista e Controles
        left_frame = ttk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Lado Direito: Preview
        right_frame = ttk.Frame(container, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        # --- CONTEÚDO ESQUERDO ---
        ttk.Label(left_frame, text="Ordem das Páginas", font=("Segoe UI", 11, "bold")).pack(pady=(0, 5))
        
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame, 
            selectmode=tk.SINGLE, 
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set,
            activestyle='none',
            height=20
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Evento: Quando selecionar um item, mostra o preview
        self.listbox.bind('<<ListboxSelect>>', self.mostrar_preview)

        # Botões
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.btn_subir = ttk.Button(btn_frame, text="▲ Subir", command=self.mover_cima)
        self.btn_subir.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.btn_descer = ttk.Button(btn_frame, text="▼ Descer", command=self.mover_baixo)
        self.btn_descer.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)

        self.btn_confirmar = ttk.Button(btn_frame, text="✅ JUNTAR AGORA", command=self.confirmar)
        self.btn_confirmar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- CONTEÚDO DIREITO (PREVIEW) ---
        ttk.Label(right_frame, text="Pré-visualização (Capa)", font=("Segoe UI", 11, "bold")).pack(pady=(0, 5))
        
        # Frame para a imagem (com borda para ficar bonito)
        self.preview_container = ttk.LabelFrame(right_frame, text=" 1ª Página ", padding=10)
        self.preview_container.pack(fill=tk.BOTH, expand=True)

        self.lbl_preview_img = ttk.Label(self.preview_container, text="Selecione um arquivo\npara ver a capa.", anchor="center")
        self.lbl_preview_img.pack(fill=tk.BOTH, expand=True)

        # Popula a lista
        for arq in self.arquivos_completos:
            self.listbox.insert(tk.END, os.path.basename(arq))

        # Atalhos de teclado
        self.root.bind('<Up>', lambda e: self.mover_cima())
        self.root.bind('<Down>', lambda e: self.mover_baixo())
        self.root.bind('<Return>', lambda e: self.confirmar())

    def mostrar_preview(self, event=None):
        """Renderiza a primeira página do PDF selecionado como imagem."""
        if not TEM_PREVIEW:
            self.lbl_preview_img.config(text="Instale 'pymupdf' e 'pillow'\npara ver o preview.")
            return

        idxs = self.listbox.curselection()
        if not idxs: return
        
        # Pega o caminho real do arquivo baseado no índice visual
        idx = idxs[0]
        caminho_arq = self.arquivos_completos[idx]

        try:
            # 1. Abre o PDF com PyMuPDF (fitz)
            doc = fitz.open(caminho_arq)
            
            # 2. Carrega a primeira página (índice 0)
            page = doc.load_page(0)
            
            # 3. Converte para Pixmap (Imagem bruta)
            pix = page.get_pixmap()
            
            # 4. Converte para formato PIL (Pillow) para manipular
            modo = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(modo, [pix.width, pix.height], pix.samples)
            
            # 5. Redimensiona para caber na interface (Thumbnail)
            # Mantém a proporção (aspect ratio)
            img.thumbnail((300, 450))
            
            # 6. Converte para formato Tkinter
            img_tk = ImageTk.PhotoImage(img)
            
            # 7. Atualiza o Label
            self.lbl_preview_img.config(image=img_tk, text="")
            self.lbl_preview_img.image = img_tk  # Necessário manter referência para não ser limpo da memória!
            
            doc.close()

        except Exception as e:
            self.lbl_preview_img.config(image="", text=f"Não foi possível visualizar.\nErro: {str(e)[:50]}...")

    def mover_cima(self):
        idxs = self.listbox.curselection()
        if not idxs: return
        idx = idxs[0]
        
        if idx > 0:
            texto = self.listbox.get(idx)
            self.listbox.delete(idx)
            self.listbox.insert(idx-1, texto)
            self.listbox.selection_set(idx-1)
            
            item = self.arquivos_completos.pop(idx)
            self.arquivos_completos.insert(idx-1, item)
            # Atualiza o preview após mover (opcional, mas bom pra UX)
            self.mostrar_preview()

    def mover_baixo(self):
        idxs = self.listbox.curselection()
        if not idxs: return
        idx = idxs[0]
        
        if idx < self.listbox.size() - 1:
            texto = self.listbox.get(idx)
            self.listbox.delete(idx)
            self.listbox.insert(idx+1, texto)
            self.listbox.selection_set(idx+1)
            
            item = self.arquivos_completos.pop(idx)
            self.arquivos_completos.insert(idx+1, item)
            self.mostrar_preview()

    def confirmar(self):
        self.cancelado = False
        self.ordem_final = self.arquivos_completos
        self.root.destroy()

def main():
    inputs = sys.argv[1:]
    
    # Se não houver input, usa a pasta atual
    if not inputs: 
        inputs = [os.getcwd()]
    
    arquivos = []
    
    # Coleta todos os arquivos
    for item in inputs:
        if os.path.isdir(item):
            for f in os.listdir(item):
                if f.lower().endswith('.pdf'): 
                    caminho_completo = os.path.abspath(os.path.join(item, f))
                    arquivos.append(caminho_completo)
        elif os.path.isfile(item) and item.lower().endswith('.pdf'):
            arquivos.append(os.path.abspath(item))
    
    # Remove duplicatas e ordena alfabeticamente como base inicial
    arquivos = sorted(list(set(arquivos)))
    
    if not arquivos:
        log.warning("Nenhum arquivo PDF encontrado.")
        os._exit(0)

    # --- ABRE O ORGANIZADOR VISUAL ---
    if len(arquivos) > 1:
        log.info("Abrindo interface de organização visual...")
        app = OrganizadorVisual(arquivos)
        app.root.mainloop()
        
        if app.cancelado:
            log.warning("Operação cancelada pelo usuário.")
            os._exit(0)
            
        arquivos = app.ordem_final
    else:
        log.info("Apenas 1 arquivo detectado, pulando organização visual.")

    pasta_base = os.path.dirname(arquivos[0])
    
    # --- GERADOR DE NOME ÚNICO ---
    nome_base = "Unificados"
    extensao = ".pdf"
    nome_saida = f"{nome_base}{extensao}"
    caminho_saida = os.path.join(pasta_base, nome_saida)
    
    contador = 1
    while os.path.exists(caminho_saida):
        nome_saida = f"{nome_base}_{contador}{extensao}"
        caminho_saida = os.path.join(pasta_base, nome_saida)
        contador += 1
    
    try:
        log.info(f"--- 🔗 JUNTAR TURBO ({len(arquivos)} arquivos) ---")
        
        pdf_novo = Pdf.new()
        
        count = 0
        for arq in arquivos:
            if os.path.abspath(arq) == os.path.abspath(caminho_saida):
                continue

            try:
                src = Pdf.open(arq)
                pdf_novo.pages.extend(src.pages)
                count += 1
            except Exception as e:
                log.error(f"Erro ao ler {os.path.basename(arq)}: {e}")

        if count > 0:
            pdf_novo.save(caminho_saida)
            log.info(f"✅ SUCESSO! Arquivo criado: {nome_saida}")
        else:
            log.warning("Nenhum arquivo válido processado.")
        
    except Exception as e:
        log.critical(f"Erro fatal: {e}")
        os._exit(1)

if __name__ == "__main__":
    main()
    os._exit(0)