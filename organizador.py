import shutil
import tkinter as tk
from tkinter import filedialog, Toplevel, ttk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pywinstyles
import os
import sys
import threading
import datetime
import send2trash  

COR_FUNDO = "#050a0e"
COR_NEON_AZUL = "#00aeff"
COR_NEON_HOVER = "#122a36"
COR_TEXTO = "#ffffff"
COR_TEXTO_DIM = "#5a7b8c"
COR_BORDA_BOTAO = "#00454a"
COR_BOTAO_BG = "#0a1921"
COR_DISABLED_BG = "#070d12"
COR_DISABLED_BORDA = "#1a1a1a"
COR_DISABLED_TEXTO = "#2a3f4a"

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

TIPOS_ARQUIVOS = {
    "PDFs": [".pdf"],
    "Imagens": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".jfif"],
    "Videos": [".mp4", ".webm", ".mkv", ".avi", ".mov", ".flv"],
    "Musicas": [".mp3", ".wav", ".ogg", ".flac", ".m4a"],
    "Documentos": [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Instaladores": [".exe", ".msi", ".apk", ".dmg"]
}

ICONES_CATEGORIAS = {
    "PDFs": "📕", "Imagens": "🖼️", "Videos": "🎬", "Musicas": "🎵",
    "Documentos": "📄", "Compactados": "📦", "Instaladores": "⚙️", "Outros": "📁",
    "Word": "📝", "Excel": "📊", "PowerPoint": "📺", "Arquivos de Texto": "🗒️",
    "PDFs Pesados": "📕", "Imagens Pesadas": "🖼️", "Videos Pesados": "🎬", 
    "Musicas Pesadas": "🎵", "Documentos Pesados": "📄", "Compactados Pesados": "📦", 
    "Instaladores Pesados": "⚙️", "Outros Pesados": "📁",
    "Word Pesados": "📝", "Excel Pesados": "📊", "PowerPoint Pesados": "📺", "Arquivos de Texto Pesados": "🗒️"
}

historico_sessao = []

def definir_icone_padrao(janela):
    try:
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        try: font = ImageFont.truetype("seguiemj.ttf", 50)
        except: font = ImageFont.load_default()
        draw.text((32, 32), "📂", font=font, fill=(0, 242, 255), anchor="mm")
        icon_img = ImageTk.PhotoImage(img)
        janela.iconphoto(True, icon_img)
        janela._icon = icon_img
    except Exception as e: print(f"Erro ícone: {e}")

def aplicar_tema_janela(janela):
    try:
        pywinstyles.apply_style(janela, "dark")
        pywinstyles.change_header_color(janela, COR_FUNDO)
    except: pass

def centralizar_janela(janela, largura, altura):
    sw, sh = janela.winfo_screenwidth(), janela.winfo_screenheight()
    x, y = (sw // 2) - (largura // 2), (sh // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

def gerar_nome_unico(caminho_completo):
    p = Path(caminho_completo)
    if not p.exists(): return p
    contador = 1
    while True:
        novo_caminho = p.parent / f"{p.stem} ({contador}){p.suffix}"
        if not novo_caminho.exists(): return novo_caminho
        contador += 1

def criar_botao_neon(parent, emoji, texto, command, state=tk.NORMAL, destaque=False, cor_icone=COR_NEON_AZUL):
    cor_b_ativa = COR_NEON_AZUL if destaque else COR_BORDA_BOTAO
    f = tk.Frame(parent, bg=cor_b_ativa, padx=1, pady=1)
    i = tk.Frame(f, bg=COR_BOTAO_BG, padx=20, pady=8, cursor="hand2")
    i.pack()
    l_e = tk.Label(i, text=emoji, font=("Segoe UI Emoji", 12), bg=COR_BOTAO_BG, fg=cor_icone)
    l_e.pack(side=tk.LEFT, padx=(0, 8))
    l_t = tk.Label(i, text=texto, font=("Segoe UI", 9, "bold"), bg=COR_BOTAO_BG, fg=COR_TEXTO)
    l_t.pack(side=tk.LEFT)

    def on_enter(e):
        if f.estado == tk.NORMAL:
            for w in [i, l_e, l_t]: w.config(bg=COR_NEON_HOVER)
    def on_leave(e):
        if f.estado == tk.NORMAL:
            for w in [i, l_e, l_t]: w.config(bg=COR_BOTAO_BG)
    def click(e):
        if f.estado == tk.NORMAL: command()

    f.estado = state
    def aplicar_estilo(s):
        f.estado = s
        if s == tk.NORMAL:
            f.config(bg=cor_b_ativa)
            bg, fg, cur, icon_fg = COR_BOTAO_BG, COR_TEXTO, "hand2", cor_icone
        else:
            f.config(bg=COR_DISABLED_BORDA)
            bg, fg, cur, icon_fg = COR_DISABLED_BG, COR_DISABLED_TEXTO, "arrow", COR_DISABLED_TEXTO
        i.config(bg=bg, cursor=cur)
        l_e.config(bg=bg, fg=icon_fg); l_t.config(bg=bg, fg=fg)

    for w in [i, l_e, l_t]:
        w.bind("<Enter>", on_enter); w.bind("<Leave>", on_leave); w.bind("<Button-1>", click)
    f.set_state = aplicar_estilo
    aplicar_estilo(state)
    return f

class JanelaConflito(Toplevel):
    def __init__(self, parent, arquivo_origem, arquivo_destino, pasta_nome):
        super().__init__(parent)
        self.title("Conflito de Arquivo")
        centralizar_janela(self, 700, 500)
        self.configure(bg=COR_FUNDO)
        self.transient(parent); self.grab_set()
        aplicar_tema_janela(self)
        self.decisao = "ignorar"
        self.aplicar_a_todos = False
        self.thumbs_conflito = []

        tk.Label(self, text="⚠️ CONFLITO DE ARQUIVO", font=("Segoe UI", 14, "bold"), bg=COR_FUNDO, fg="#ffcc00").pack(pady=15)
        container_cards = tk.Frame(self, bg=COR_FUNDO); container_cards.pack(expand=True, fill="both", padx=20)

        self.criar_card(container_cards, arquivo_destino, "EXISTENTE NA PASTA", "left")
        tk.Label(container_cards, text="➔", font=("Segoe UI", 20), bg=COR_FUNDO, fg=COR_NEON_AZUL).pack(side="left", padx=10)
        self.criar_card(container_cards, arquivo_origem, "NOVO (SENDO MOVIDO)", "left")

        self.var_todos = tk.BooleanVar(value=False)
        self.cb_todos = tk.Checkbutton(self, text="⬜ Aplicar esta decisão para todos os próximos conflitos", 
                                       variable=self.var_todos, bg=COR_FUNDO, fg=COR_TEXTO_DIM, 
                                       selectcolor=COR_BOTAO_BG, activebackground=COR_FUNDO, 
                                       activeforeground=COR_NEON_AZUL, font=("Segoe UI", 10))
        self.cb_todos.pack(pady=10)

        btn_f = tk.Frame(self, bg=COR_FUNDO); btn_f.pack(pady=(10, 20), fill="x")
        criar_botao_neon(btn_f, "⏭️", "IGNORAR", lambda: self.set_decisao("ignorar")).pack(side="left", expand=True, padx=5)
        criar_botao_neon(btn_f, "♻️", "SUBSTITUIR", lambda: self.set_decisao("substituir")).pack(side="left", expand=True, padx=5)
        criar_botao_neon(btn_f, "📝", "RENOMEAR", lambda: self.set_decisao("renomear")).pack(side="left", expand=True, padx=5)

    def criar_card(self, parent, path, titulo, side):
        card = tk.Frame(parent, bg=COR_BOTAO_BG, highlightbackground=COR_BORDA_BOTAO, highlightthickness=1, padx=10, pady=10)
        card.pack(side=side, expand=True, fill="both", padx=5)
        tk.Label(card, text=titulo, font=("Segoe UI", 8, "bold"), bg=COR_BOTAO_BG, fg=COR_TEXTO_DIM).pack()
        img_frame = tk.Frame(card, width=120, height=120, bg=COR_FUNDO); img_frame.pack_propagate(False); img_frame.pack(pady=10)
        lbl_img = tk.Label(img_frame, bg=COR_FUNDO); lbl_img.pack(expand=True, fill="both")

        exibiu = False
        if path.suffix.lower() in TIPOS_ARQUIVOS["Imagens"]:
            try:
                with Image.open(path) as img:
                    img.thumbnail((110, 110), Image.Resampling.LANCZOS)
                    ph = ImageTk.PhotoImage(img); lbl_img.config(image=ph); self.thumbs_conflito.append(ph)
                    exibiu = True
            except: pass
        if not exibiu:
            ext = path.suffix.lower()
            icone = "📁"
            for cat, exts in TIPOS_ARQUIVOS.items():
                if ext in exts: icone = ICONES_CATEGORIAS.get(cat, "📁"); break
            lbl_img.config(text=icone, fg=COR_NEON_AZUL, font=("Segoe UI Emoji", 40))

        nome_curto = (path.name[:25] + '..') if len(path.name) > 28 else path.name
        tk.Label(card, text=nome_curto, fg=COR_TEXTO, bg=COR_BOTAO_BG, font=("Segoe UI", 9, "bold"), wraplength=150).pack()
        tamanho = f"{os.path.getsize(path) / 1024:.1f} KB"
        tk.Label(card, text=tamanho, fg=COR_TEXTO_DIM, bg=COR_BOTAO_BG, font=("Consolas", 8)).pack()

    def set_decisao(self, d):
        self.decisao = d
        self.aplicar_a_todos = self.var_todos.get()
        self.destroy()

class JanelaConfirmacaoMuitosArquivos(Toplevel):
    def __init__(self, parent, total_arquivos):
        super().__init__(parent)
        self.title("Confirmação de Operação Em Massa")
        centralizar_janela(self, 480, 250)
        self.configure(bg=COR_FUNDO)
        self.confirmado = False
        self.transient(parent); self.grab_set()
        aplicar_tema_janela(self); definir_icone_padrao(self)

        tk.Label(self, text="⚠️ MUITOS ARQUIVOS ENCONTRADOS", font=("Segoe UI", 12, "bold"), bg=COR_FUNDO, fg="#ffcc00").pack(pady=(25, 10))
        
        msg = f"Especificamente {total_arquivos} arquivos.\nOrganizar tudo?"
        tk.Label(self, text=msg, font=("Segoe UI", 10), bg=COR_FUNDO, fg=COR_TEXTO, justify="center").pack(pady=10)

        btn_f = tk.Frame(self, bg=COR_FUNDO)
        btn_f.pack(pady=20)
        criar_botao_neon(btn_f, "✅", "CONFIRMAR", self.confirmar, destaque=True).pack(side="left", padx=10)
        criar_botao_neon(btn_f, "❌", "CANCELAR", self.destroy).pack(side="left", padx=10)

    def confirmar(self):
        self.confirmado = True
        self.destroy()

class JanelaConfirmacao(Toplevel):
    def __init__(self, parent, plano):
        super().__init__(parent)
        self.title("Análise de Arquivos")
        centralizar_janela(self, 650, 650)
        self.configure(bg=COR_FUNDO)
        self.confirmado, self.plano_final, self.thumbnails = False, [], []
        self.itens_selecao = []
        self.transient(parent); self.grab_set()
        aplicar_tema_janela(self); definir_icone_padrao(self)

        tk.Label(self, text="PRÉVIA DA OPERAÇÃO", font=("Segoe UI", 16, "bold"), bg=COR_FUNDO, fg=COR_NEON_AZUL).pack(pady=15)
        container = tk.Frame(self, bg=COR_FUNDO); container.pack(expand=True, fill="both", padx=20)
        
        self.canvas = tk.Canvas(container, bg=COR_FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COR_FUNDO)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", expand=True, fill="both"); scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            try:
                if getattr(event, 'delta', 0) != 0:
                    self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                elif getattr(event, 'num', 0) == 4:
                    self.canvas.yview_scroll(-1, "units")
                elif getattr(event, 'num', 0) == 5:
                    self.canvas.yview_scroll(1, "units")
            except:
                pass

        self.bind_all("<MouseWheel>", _on_mousewheel)
        self.bind_all("<Button-4>", _on_mousewheel)
        self.bind_all("<Button-5>", _on_mousewheel)

        for arquivo, pasta in plano:
            var = tk.BooleanVar(value=True); self.itens_selecao.append((var, arquivo, pasta))
            item = tk.Frame(self.scrollable_frame, bg=COR_FUNDO, pady=5); item.pack(fill="x", anchor="w")
            tk.Checkbutton(item, variable=var, bg=COR_FUNDO, selectcolor=COR_BOTAO_BG, fg=COR_NEON_AZUL, bd=0).pack(side="left", padx=5)
            ic_cont = tk.Frame(item, width=40, height=40, bg=COR_BOTAO_BG); ic_cont.pack_propagate(False); ic_cont.pack(side="left", padx=5)
            img_l = tk.Label(ic_cont, bg=COR_BOTAO_BG); img_l.pack(expand=True, fill="both")
            
            exibiu = False
            if arquivo.suffix.lower() in TIPOS_ARQUIVOS["Imagens"]:
                try:
                    with Image.open(arquivo) as img:
                        img.thumbnail((35, 35), Image.Resampling.LANCZOS)
                        ph = ImageTk.PhotoImage(img); img_l.config(image=ph); self.thumbnails.append(ph)
                        exibiu = True
                except: pass
            if not exibiu: img_l.config(text=ICONES_CATEGORIAS.get(pasta, "📁"), fg=COR_NEON_AZUL, font=("Segoe UI Emoji", 18))

            info = tk.Frame(item, bg=COR_FUNDO); info.pack(side="left", padx=10)
            nome = (arquivo.name[:42] + '..') if len(arquivo.name) > 45 else arquivo.name
            tk.Label(info, text=nome, fg=COR_TEXTO, bg=COR_FUNDO, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tk.Label(info, text=f"➔ {pasta}", fg=COR_TEXTO_DIM, bg=COR_FUNDO, font=("Consolas", 8)).pack(anchor="w")

        btn_sel_f = tk.Frame(self, bg=COR_FUNDO); btn_sel_f.pack(pady=10)
        tk.Button(btn_sel_f, text="Marcar Todos", command=lambda: self.set_selecao(True), bg=COR_FUNDO, fg=COR_TEXTO_DIM, bd=0, cursor="hand2", font=("Segoe UI", 10, "bold")).pack(side="left", padx=15)
        tk.Button(btn_sel_f, text="Desmarcar Todos", command=lambda: self.set_selecao(False), bg=COR_FUNDO, fg=COR_TEXTO_DIM, bd=0, cursor="hand2", font=("Segoe UI", 10, "bold")).pack(side="left", padx=15)

        btn_f = tk.Frame(self, bg=COR_FUNDO); btn_f.pack(pady=(5, 25))
        criar_botao_neon(btn_f, "✅", "EXECUTAR SELECIONADOS", self.confirmar, destaque=True).pack(side="left", padx=10)
        criar_botao_neon(btn_f, "❌", "CANCELAR", self.destroy).pack(side="left", padx=10)

    def set_selecao(self, valor):
        for var, _, _ in self.itens_selecao: var.set(valor)

    def confirmar(self):
        self.plano_final = [(arq, pst) for var, arq, pst in self.itens_selecao if var.get()]
        if self.plano_final: self.confirmado = True; self.destroy()

    def destroy(self):
        try:
            self.unbind_all("<MouseWheel>")
            self.unbind_all("<Button-4>")
            self.unbind_all("<Button-5>")
        except:
            pass
        super().destroy()

def obter_plano(caminho, modo="tipo", incluir_subpastas=False, separar_pesados=False, separar_docs=False):
    c = Path(caminho)
    plano = []
    
    meu_arquivo_atual = Path(sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]).name.lower()
    
    try:
        arquivos_alvo = c.rglob('*') if incluir_subpastas else c.iterdir()
        
        for f in arquivos_alvo:
            if f.is_file() and f.name.lower() != meu_arquivo_atual and not f.name.startswith('.'):
                if incluir_subpastas:
                    partes = f.relative_to(c).parts
                    if len(partes) > 1:
                        subpasta_raiz = partes[0]
                        if subpasta_raiz in TIPOS_ARQUIVOS or subpasta_raiz in ["Word", "Excel", "PowerPoint", "Arquivos de Texto", "Outros"] or "Pesados" in subpasta_raiz or "Pesadas" in subpasta_raiz:
                            continue
                            
                mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
                
                if modo == "dia":
                    dest = f"{mtime.day} de {MESES_PT[mtime.month]} de {mtime.year}"
                elif modo == "mes":
                    dest = f"{MESES_PT[mtime.month]} de {mtime.year}"
                elif modo == "ano":
                    dest = f"{mtime.year}"
                else:
                    ext = f.suffix.lower()
                    dest = "Outros"
                    for cat, exts in TIPOS_ARQUIVOS.items():
                        if ext in exts: dest = cat; break
                    
                    if separar_docs and dest == "Documentos":
                        if ext in [".doc", ".docx"]:
                            dest = "Word"
                        elif ext in [".xls", ".xlsx", ".csv"]:
                            dest = "Excel"
                        elif ext in [".ppt", ".pptx"]:
                            dest = "PowerPoint"
                        elif ext in [".txt"]:
                            dest = "Arquivos de Texto"

                if separar_pesados:
                    try:
                        tamanho_mb = f.stat().st_size / (1024 * 1024)
                        if tamanho_mb > 300:
                            if modo == "tipo":
                                nomes_pesados = {
                                    "PDFs": "PDFs Pesados", "Imagens": "Imagens Pesadas",
                                    "Videos": "Videos Pesados", "Musicas": "Musicas Pesadas",
                                    "Documentos": "Documentos Pesados", "Compactados": "Compactados Pesados",
                                    "Instaladores": "Instaladores Pesados", "Outros": "Outros Pesados",
                                    "Word": "Word Pesados", "Excel": "Excel Pesados", 
                                    "PowerPoint": "PowerPoint Pesados", "Arquivos de Texto": "Arquivos de Texto Pesados"
                                }
                                dest = nomes_pesados.get(dest, f"{dest} Pesados")
                            else:
                                dest = f"{dest} (Pesados)"
                    except Exception as e:
                        print(f"Erro ao verificar tamanho: {e}")

                plano.append((f, dest))
    except: pass
    return plano

def selecionar_pasta():
    p = filedialog.askdirectory()
    if p:
        lbl_caminho.config(text=p, fg=COR_NEON_AZUL)
        btn_organizar.set_state(tk.NORMAL)
        btn_limpar_vazias.set_state(tk.NORMAL)

def mostrar_mensagem(parent, titulo, mensagem, tipo="info"):
    m = Toplevel(parent); m.title(titulo); centralizar_janela(m, 400, 220); m.configure(bg=COR_FUNDO)
    m.transient(parent); m.grab_set(); aplicar_tema_janela(m); definir_icone_padrao(m)
    cor = COR_NEON_AZUL if tipo == "info" else "#ff3131"
    tk.Label(m, text=titulo.upper(), font=("Segoe UI", 12, "bold"), bg=COR_FUNDO, fg=cor).pack(pady=(20, 10))
    tk.Label(m, text=mensagem, font=("Segoe UI", 10), bg=COR_FUNDO, fg=COR_TEXTO, wraplength=350).pack(pady=10)
    criar_botao_neon(m, "✖", "FECHAR", m.destroy).pack(pady=20)

def desfazer():
    global historico_sessao
    if not historico_sessao:
        mostrar_mensagem(janela, "Aviso", "Nenhuma operação para desfazer.")
        return
    
    erros = 0
    pastas_vazias = set()
    for orig, dest in historico_sessao:
        try:
            if Path(dest).exists():
                shutil.move(str(dest), str(orig))
                pastas_vazias.add(Path(dest).parent)
        except: erros += 1
    
    for pasta in pastas_vazias:
        try:
            if not any(pasta.iterdir()): os.rmdir(pasta)
        except: pass
            
    historico_sessao = []
    btn_undo.set_state(tk.DISABLED)
    mostrar_mensagem(janela, "Undo", f"Arquivos restaurados. Erros: {erros}")

def apagar_pastas_vazias():
    caminho = lbl_caminho.cget("text")
    if caminho == "Nenhuma pasta selecionada...": return

    apagadas = 0
    for root, dirs, files in os.walk(caminho, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    apagadas += 1
            except: pass
    
    if apagadas > 0:
        mostrar_mensagem(janela, "Limpeza Concluída", f"{apagadas} pastas vazias foram removidas.")
    else:
        mostrar_mensagem(janela, "Status", "Nenhuma pasta vazia encontrada.")

def executar():
    caminho = lbl_caminho.cget("text")
    if caminho == "Nenhuma pasta selecionada...": return
    
    plano = obter_plano(caminho, var_modo.get(), var_subpastas.get(), var_pesados.get(), var_separar_docs.get())
    if not plano:
        mostrar_mensagem(janela, "Status", "Pasta já está organizada ou vazia."); return
    
    confirmado = False
    plano_final_executar = []

    if len(plano) > 300:
        diag_massa = JanelaConfirmacaoMuitosArquivos(janela, len(plano))
        janela.wait_window(diag_massa)
        if diag_massa.confirmado:
            confirmado = True
            plano_final_executar = plano
    else:
        conf = JanelaConfirmacao(janela, plano)
        janela.wait_window(conf)
        if conf.confirmado:
            confirmado = True
            plano_final_executar = conf.plano_final
    
    if confirmado:
        def task():
            global historico_sessao
            btn_organizar.set_state(tk.DISABLED)
            btn_limpar_vazias.set_state(tk.DISABLED)
            btn_undo.set_state(tk.DISABLED)
            progress.pack(pady=10)
            progress['maximum'] = len(plano_final_executar)
            progress['value'] = 0
            
            movidos, erros = 0, 0
            sessao = []
            
            decisao_automatica = None  
            aplicar_em_lote = False
            
            for arq, pasta in plano_final_executar:
                dest_dir = Path(caminho) / pasta
                dest_dir.mkdir(exist_ok=True)
                dest_arq = dest_dir / arq.name
                
                if dest_arq.exists():
                    if arq == dest_arq:
                        progress['value'] += 1; continue
                    
                    if aplicar_em_lote:
                        acao_atual = decisao_automatica
                    else:
                        diag = JanelaConflito(janela, arq, dest_arq, pasta)
                        janela.wait_window(diag)
                        acao_atual = diag.decisao
                        
                        if diag.aplicar_a_todos:
                            decisao_automatica = acao_atual
                            aplicar_em_lote = True
                    
                    if acao_atual == "ignorar": 
                        progress['value'] += 1; continue
                    elif acao_atual == "substituir":
                        try: send2trash.send2trash(str(dest_arq))
                        except: erros += 1; progress['value'] += 1; continue
                    elif acao_atual == "renomear":
                        dest_arq = gerar_nome_unico(dest_arq)

                try:
                    shutil.move(str(arq), str(dest_arq))
                    sessao.append((arq, dest_arq))
                    movidos += 1
                except: erros += 1
                
                progress['value'] += 1
                janela.update_idletasks()

            historico_sessao = sessao
            if movidos > 0: btn_undo.set_state(tk.NORMAL)
            progress.pack_forget()
            mostrar_mensagem(janela, "Sucesso", f"{movidos} movidos, {erros} erros.")
            lbl_caminho.config(text="Nenhuma pasta selecionada...", fg=COR_TEXTO_DIM)
            btn_organizar.set_state(tk.DISABLED)
            btn_limpar_vazias.set_state(tk.DISABLED)

        threading.Thread(target=task, daemon=True).start()

janela = tk.Tk()
janela.title("Organizador de Arquivos")
janela.config(bg=COR_FUNDO)
try: janela.state('zoomed')
except: janela.attributes('-fullscreen', True)

aplicar_tema_janela(janela); definir_icone_padrao(janela)

style = ttk.Style()
style.configure("Neon.Horizontal.TProgressbar", thickness=10, troughcolor=COR_BOTAO_BG, background=COR_NEON_AZUL)

main = tk.Frame(janela, bg=COR_FUNDO); main.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
tk.Label(main, text="📂", font=("Segoe UI Emoji", 50), bg=COR_FUNDO, fg=COR_NEON_AZUL).pack()
tk.Label(main, text="ORGANIZADOR DE ARQUIVOS", font=("Segoe UI", 24, "bold"), bg=COR_FUNDO, fg=COR_TEXTO).pack()
lbl_caminho = tk.Label(main, text="Nenhuma pasta selecionada...", font=("Consolas", 10), bg=COR_FUNDO, fg=COR_TEXTO_DIM, wraplength=500)
lbl_caminho.pack(pady=20)

var_modo = tk.StringVar(value="tipo")
frame_opcoes = tk.Frame(main, bg=COR_FUNDO)
frame_opcoes.pack(pady=10)

opcoes = [("📁 Por Tipo", "tipo"), ("📅 Por Dia", "dia"), ("🗓️ Por Mês", "mes"), ("⏳ Por Ano", "ano")]

for txt, val in opcoes:
    rb = tk.Radiobutton(frame_opcoes, text=txt, variable=var_modo, value=val, 
                        bg=COR_FUNDO, fg=COR_TEXTO_DIM, selectcolor=COR_BOTAO_BG,
                        activebackground=COR_FUNDO, activeforeground=COR_NEON_AZUL,
                        font=("Segoe UI", 10))
    rb.pack(side="left", padx=10)

var_subpastas = tk.BooleanVar(value=False)
var_pesados = tk.BooleanVar(value=False)
var_separar_docs = tk.BooleanVar(value=False) 

frame_subpastas = tk.Frame(main, bg=COR_FUNDO)
frame_subpastas.pack(pady=5)

cb_subpastas = tk.Checkbutton(frame_subpastas, text="🔍 Incluir subpastas", variable=var_subpastas,
                              bg=COR_FUNDO, fg=COR_TEXTO_DIM, selectcolor=COR_BOTAO_BG,
                              activebackground=COR_FUNDO, activeforeground=COR_NEON_AZUL,
                              font=("Segoe UI", 10))
cb_subpastas.pack(side="left", padx=10)

cb_pesados = tk.Checkbutton(frame_subpastas, text="🐘 Separar arquivos > 300MB", variable=var_pesados,
                            bg=COR_FUNDO, fg=COR_TEXTO_DIM, selectcolor=COR_BOTAO_BG,
                            activebackground=COR_FUNDO, activeforeground=COR_NEON_AZUL,
                            font=("Segoe UI", 10))
cb_pesados.pack(side="left", padx=10)

cb_separar_docs = tk.Checkbutton(frame_subpastas, text="📑 Separar Documentos", variable=var_separar_docs,
                                 bg=COR_FUNDO, fg=COR_TEXTO_DIM, selectcolor=COR_BOTAO_BG,
                                 activebackground=COR_FUNDO, activeforeground=COR_NEON_AZUL,
                                 font=("Segoe UI", 10))
cb_separar_docs.pack(side="left", padx=10)

progress = ttk.Progressbar(main, length=400, mode="determinate", style="Neon.Horizontal.TProgressbar")

btn_f = tk.Frame(main, bg=COR_FUNDO); btn_f.pack(pady=10)
criar_botao_neon(btn_f, "🔍", "SELECIONAR PASTA", selecionar_pasta).pack(side="left", padx=5)

btn_limpar_vazias = criar_botao_neon(btn_f, "🧹", "LIMPAR PASTAS VAZIAS", apagar_pastas_vazias, state=tk.DISABLED)
btn_limpar_vazias.pack(side="left", padx=5)

btn_undo = criar_botao_neon(btn_f, "↩️", "DESFAZER", desfazer, state=tk.DISABLED)
btn_undo.pack(side="left", padx=5)

tk.Frame(main, height=1, width=300, bg=COR_BORDA_BOTAO).pack(pady=20)
btn_organizar = criar_botao_neon(main, "⚡", "ORGANIZAR AGORA", executar, state=tk.DISABLED, destaque=True, cor_icone="#ffa500")
btn_organizar.pack()

if __name__ == "__main__":
    janela.mainloop()