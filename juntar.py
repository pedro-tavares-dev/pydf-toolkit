import sys
import os
import tkinter as tk
from tkinter import ttk
from pikepdf import Pdf  # A Turbina C++
from biblioteca_logs import configurar_logger

# Importações para o Preview (Visualização)
try:
    import fitz  # PyMuPDF
    from PIL import Image, ImageTk
    TEM_PREVIEW = True
except ImportError:
    TEM_PREVIEW = False

log = configurar_logger("juntar")

class OrganizadorVisual:
    """
    Interface gráfica com PREVIEW e RENOMEAÇÃO.
    """
    def __init__(self, arquivos):
        self.arquivos_completos = arquivos 
        self.ordem_final = []
        self.nome_escolhido = "Unificados" # Nome padrão
        self.cancelado = True

        self.root = tk.Tk()
        self.root.title("Juntar PDF - Defina Ordem e Nome")
        
        # Centraliza e define tamanho
        largura_janela, altura_janela = 900, 600
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        style = ttk.Style()
        style.theme_use('clam')

        # === CONTAINER PRINCIPAL ===
        container = ttk.Frame(self.root, padding="10")
        container.pack(fill=tk.BOTH, expand=True)

        # Lado Esquerdo: Lista e Controles
        left_frame = ttk.Frame(container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Lado Direito: Preview
        right_frame = ttk.Frame(container, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        # --- LISTA ---
        ttk.Label(left_frame, text="1. Organize a Ordem", font=("Segoe UI", 11, "bold")).pack(pady=(0, 5), anchor="w")
        
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
        
        self.listbox.bind('<<ListboxSelect>>', self.mostrar_preview)

        # --- BOTÕES DE MOVER ---
        move_frame = ttk.Frame(left_frame)
        move_frame.pack(fill=tk.X, pady=5)
        
        self.btn_subir = ttk.Button(move_frame, text="▲ Subir", command=self.mover_cima)
        self.btn_subir.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.btn_descer = ttk.Button(move_frame, text="▼ Descer", command=self.mover_baixo)
        self.btn_descer.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # --- ÁREA DE RENOMEAR (NOVIDADE) ---
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        ttk.Label(left_frame, text="2. Nome do Novo Arquivo (sem .pdf):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        
        self.entry_nome = ttk.Entry(left_frame, font=("Segoe UI", 11))
        self.entry_nome.insert(0, "Unificados") # Valor padrão
        self.entry_nome.pack(fill=tk.X, pady=(5, 10))

        # --- BOTÃO CONFIRMAR ---
        self.btn_confirmar = ttk.Button(left_frame, text="✅ JUNTAR AGORA", command=self.confirmar)
        self.btn_confirmar.pack(fill=tk.X, ipady=5)

        # --- PREVIEW (DIREITA) ---
        ttk.Label(right_frame, text="Pré-visualização (Capa)", font=("Segoe UI", 11, "bold")).pack(pady=(0, 5))
        self.preview_container = ttk.LabelFrame(right_frame, text=" 1ª Página ", padding=10)
        self.preview_container.pack(fill=tk.BOTH, expand=True)
        self.lbl_preview_img = ttk.Label(self.preview_container, text="Selecione um arquivo...", anchor="center")
        self.lbl_preview_img.pack(fill=tk.BOTH, expand=True)

        # Popula lista
        for arq in self.arquivos_completos:
            self.listbox.insert(tk.END, os.path.basename(arq))

    def mostrar_preview(self, event=None):
        if not TEM_PREVIEW:
            self.lbl_preview_img.config(text="Instale 'pymupdf' e 'pillow'\npara ver preview.")
            return

        idxs = self.listbox.curselection()
        if not idxs: return
        
        idx = idxs[0]
        caminho_arq = self.arquivos_completos[idx]

        try:
            doc = fitz.open(caminho_arq)
            page = doc.load_page(0)
            pix = page.get_pixmap()
            modo = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(modo, [pix.width, pix.height], pix.samples)
            img.thumbnail((300, 450))
            img_tk = ImageTk.PhotoImage(img)
            self.lbl_preview_img.config(image=img_tk, text="")
            self.lbl_preview_img.image = img_tk
            doc.close()
        except Exception:
            self.lbl_preview_img.config(image="", text="Pré-visualização indisponível.")

    def mover_cima(self):
        idxs = self.listbox.curselection()
        if not idxs: return
        idx = idxs[0]
        if idx > 0:
            self.trocar_posicao(idx, idx-1)

    def mover_baixo(self):
        idxs = self.listbox.curselection()
        if not idxs: return
        idx = idxs[0]
        if idx < self.listbox.size() - 1:
            self.trocar_posicao(idx, idx+1)
            
    def trocar_posicao(self, atual, novo):
        texto = self.listbox.get(atual)
        self.listbox.delete(atual)
        self.listbox.insert(novo, texto)
        self.listbox.selection_set(novo)
        item = self.arquivos_completos.pop(atual)
        self.arquivos_completos.insert(novo, item)
        self.mostrar_preview()

    def confirmar(self):
        # Captura o nome digitado
        nome = self.entry_nome.get().strip()
        if nome:
            self.nome_escolhido = nome
        self.cancelado = False
        self.ordem_final = self.arquivos_completos
        self.root.destroy()

def main():
    inputs = sys.argv[1:]
    if not inputs: inputs = [os.getcwd()]
    
    arquivos = []
    for item in inputs:
        if os.path.isdir(item):
            for f in os.listdir(item):
                if f.lower().endswith('.pdf'): 
                    arquivos.append(os.path.abspath(os.path.join(item, f)))
        elif os.path.isfile(item) and item.lower().endswith('.pdf'):
            arquivos.append(os.path.abspath(item))
    
    arquivos = sorted(list(set(arquivos)))
    
    if not arquivos:
        log.warning("Nenhum arquivo PDF encontrado.")
        os._exit(0)

    # Variável para guardar o nome escolhido
    nome_final_usuario = "Unificados"

    if len(arquivos) > 1:
        app = OrganizadorVisual(arquivos)
        app.root.mainloop()
        
        if app.cancelado:
            os._exit(0)
            
        arquivos = app.ordem_final
        nome_final_usuario = app.nome_escolhido # Pega o nome da classe
    
    # --- LÓGICA DE SALVAMENTO ---
    pasta_base = os.path.dirname(arquivos[0])
    
    # Remove .pdf se o usuário tiver digitado, para não ficar .pdf.pdf
    nome_limpo = nome_final_usuario.replace(".pdf", "")
    nome_saida = f"{nome_limpo}.pdf"
    caminho_saida = os.path.join(pasta_base, nome_saida)
    
    # Se já existir, adiciona número (Unificados_1.pdf)
    contador = 1
    while os.path.exists(caminho_saida):
        nome_saida = f"{nome_limpo}_{contador}.pdf"
        caminho_saida = os.path.join(pasta_base, nome_saida)
        contador += 1
    
    try:
        log.info(f"--- 🔗 JUNTAR: Criando '{nome_saida}' ---")
        pdf_novo = Pdf.new()
        
        for arq in arquivos:
            # Evita juntar o próprio arquivo de saída se ele já existir na pasta
            if os.path.abspath(arq) == os.path.abspath(caminho_saida): continue
            
            with Pdf.open(arq) as src:
                pdf_novo.pages.extend(src.pages)

        pdf_novo.save(caminho_saida)
        log.info(f"✅ SUCESSO! Salvo em: {caminho_saida}")
        
    except Exception as e:
        log.critical(f"Erro fatal: {e}")
        os._exit(1)

if __name__ == "__main__":
    main()
    os._exit(0)