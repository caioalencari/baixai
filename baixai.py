import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import baixai_nucleo as nucleo

if getattr(sys, "frozen", False):
    PASTA_APP = os.path.dirname(sys.executable)
else:
    PASTA_APP = os.path.dirname(os.path.abspath(__file__))

YTDLP = os.path.join(PASTA_APP, f"yt-dlp{nucleo.EXE}")
PASTA_PADRAO = os.path.join(os.path.expanduser("~"), "Music")
CONTATO = "Caio Alencar"
TITULO = "Baixaí"
NUCLEO_ESPERADO = 7

COR = {
    "fundo": "#F4F3FA", "card": "#FFFFFF", "texto": "#1F1B2E", "suave": "#6B6680",
    "borda": "#DCD9EA", "trilho": "#ECEAF5", "desligado": "#B5B1C7",
    "roxo": "#5B4BDB", "roxo_escuro": "#4636C2", "roxo_apagado": "#B4ACEB",
    "lilas": "#D9D3FF", "lilas_claro": "#EFEDFC",
    "ok": "#1F9D63", "erro": "#C7364A", "aviso": "#B7791F",
}

ICONE_PNG = "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"

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(TITULO)
        self.geometry("620x600")
        self.minsize(540, 560)

        self.processo = None
        self.incompleto = None
        self.tipo_link = None
        self.animando = False
        self.ocupado = False
        self.parado = False
        self.erros = 0
        self.bloqueio = None
        self.item_atual = ""
        self.pasta = tk.StringVar(value=PASTA_PADRAO)
        self.tipo = tk.StringVar(value="mp3")
        self.status = tk.StringVar(value="Cole o link de um vídeo ou de uma playlist.")

        self._montar_tela()
        self.protocol("WM_DELETE_WINDOW", self.fechar)
        if self._deve_oferecer_instalacao():
            self.after(400, self._oferecer_instalacao)

    # ---------- Interface ----------
    def _estilos(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        self.configure(bg=COR["fundo"])
        fonte = "Segoe UI"
        st.configure(".", background=COR["fundo"], foreground=COR["texto"], font=(fonte, 10))
        st.configure("Topo.TFrame", background=COR["roxo"])
        st.configure("Titulo.TLabel", background=COR["roxo"], foreground="white", font=(fonte + " Semibold", 24))
        st.configure("Sub.TLabel", background=COR["roxo"], foreground=COR["lilas"], font=(fonte, 10))
        st.configure("Card.TFrame", background=COR["card"])
        st.configure("Card.TLabel", background=COR["card"], foreground=COR["texto"], font=(fonte + " Semibold", 10))
        st.configure("Dica.TLabel", background=COR["card"], foreground=COR["suave"], font=(fonte, 9))
        st.configure("Rodape.TLabel", background=COR["fundo"], foreground=COR["suave"], font=(fonte, 9))
        st.configure("TEntry", fieldbackground="white", foreground=COR["texto"], padding=7,
                     bordercolor=COR["borda"], lightcolor=COR["borda"], darkcolor=COR["borda"])
        st.map("TEntry", bordercolor=[("focus", COR["roxo"])], lightcolor=[("focus", COR["roxo"])])
        st.configure("Primario.TButton", background=COR["roxo"], foreground="white", borderwidth=0,
                     focuscolor=COR["roxo"], padding=(26, 9), font=(fonte + " Semibold", 11))
        st.map("Primario.TButton",
               background=[("disabled", COR["roxo_apagado"]), ("pressed", COR["roxo_escuro"]),
                           ("active", COR["roxo_escuro"])],
               foreground=[("disabled", "white")])
        st.configure("Secundario.TButton", background=COR["card"], foreground=COR["roxo"],
                     bordercolor=COR["borda"], lightcolor=COR["card"], darkcolor=COR["card"],
                     focuscolor=COR["card"], padding=(14, 8))
        st.map("Secundario.TButton", background=[("active", COR["lilas_claro"])],
               foreground=[("disabled", COR["desligado"])])
        st.configure("Link.TButton", background=COR["fundo"], foreground=COR["suave"], borderwidth=0,
                     focuscolor=COR["fundo"], padding=(2, 2), font=(fonte, 9, "underline"))
        st.map("Link.TButton", background=[("active", COR["fundo"])],
               foreground=[("active", COR["roxo"]), ("disabled", COR["desligado"])])
        st.configure("Pilula.Toolbutton", background=COR["lilas_claro"], foreground=COR["roxo"],
                     borderwidth=0, focuscolor=COR["lilas_claro"], padding=(18, 7), font=(fonte, 10))
        st.map("Pilula.Toolbutton",
               background=[("selected", COR["roxo"]), ("active", COR["lilas"])],
               foreground=[("selected", "white")])
        st.configure("Roxo.Horizontal.TProgressbar", troughcolor=COR["trilho"], background=COR["roxo"],
                     bordercolor=COR["trilho"], lightcolor=COR["roxo"], darkcolor=COR["roxo"], thickness=8)

    def _montar_tela(self):
        self._estilos()
        try:
            self.icone = tk.PhotoImage(data=ICONE_PNG)
            self.iconphoto(True, self.icone)
        except tk.TclError:
            pass

        topo = ttk.Frame(self, style="Topo.TFrame", padding=(28, 20, 28, 20))
        topo.pack(fill="x")
        ttk.Label(topo, text=TITULO, style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(topo, text="Cole o link, escolha o formato e pronto.", style="Sub.TLabel").pack(anchor="w")

        corpo = ttk.Frame(self, padding=(20, 18, 20, 10))
        corpo.pack(fill="both", expand=True)

        card = ttk.Frame(corpo, style="Card.TFrame", padding=(22, 18))
        card.pack(fill="x")

        ttk.Label(card, text="Link do vídeo ou da playlist", style="Card.TLabel").pack(anchor="w")
        self.url = ttk.Entry(card, font=("Segoe UI", 11))
        self.url.pack(fill="x", pady=(6, 4))
        self.url.focus()
        self.url.bind("<Button-3>", self._colar)
        self.url.bind("<Return>", lambda e: self.baixar())
        ttk.Label(card, text="Funciona com links do YouTube. Clique com o botão direito para colar.",
                  style="Dica.TLabel").pack(anchor="w", pady=(0, 14))

        formato = ttk.Frame(card, style="Card.TFrame")
        formato.pack(fill="x", pady=(0, 14))
        ttk.Label(formato, text="Formato", style="Card.TLabel").pack(side="left", padx=(0, 12))
        ttk.Radiobutton(formato, text="Música (MP3)", value="mp3", variable=self.tipo,
                        style="Pilula.Toolbutton").pack(side="left")
        ttk.Radiobutton(formato, text="Vídeo (MP4)", value="mp4", variable=self.tipo,
                        style="Pilula.Toolbutton").pack(side="left", padx=(8, 0))

        ttk.Label(card, text="Salvar em", style="Card.TLabel").pack(anchor="w")
        linha_pasta = ttk.Frame(card, style="Card.TFrame")
        linha_pasta.pack(fill="x", pady=(6, 18))
        ttk.Entry(linha_pasta, textvariable=self.pasta).pack(side="left", fill="x", expand=True)
        ttk.Button(linha_pasta, text="Escolher", style="Secundario.TButton",
                   command=self.escolher_pasta).pack(side="left", padx=(8, 0))

        botoes = ttk.Frame(card, style="Card.TFrame")
        botoes.pack(fill="x")
        self.btn_baixar = ttk.Button(botoes, text="Baixar", style="Primario.TButton", command=self.baixar)
        self.btn_baixar.pack(side="left")
        self.btn_parar = ttk.Button(botoes, text="Parar", style="Secundario.TButton",
                                    command=self.parar, state="disabled")
        self.btn_parar.pack(side="left", padx=(10, 0))
        ttk.Button(botoes, text="Abrir pasta", style="Secundario.TButton",
                   command=self.abrir_pasta).pack(side="right")

        self.barra = ttk.Progressbar(card, maximum=100, style="Roxo.Horizontal.TProgressbar")
        self.barra.pack(fill="x", pady=(20, 8))
        self.lbl_status = tk.Label(card, textvariable=self.status, bg=COR["card"], fg=COR["texto"],
                                   font=("Segoe UI", 10), anchor="w", justify="left", wraplength=540)
        self.lbl_status.pack(fill="x")

        extras = ttk.Frame(corpo)
        extras.pack(fill="x", pady=(10, 0))
        self.btn_detalhes = ttk.Button(extras, text="Mostrar detalhes", style="Link.TButton",
                                       command=self.alternar_detalhes)
        self.btn_detalhes.pack(side="left")
        self.btn_atualizar = ttk.Button(extras, text="Atualizar yt-dlp", style="Link.TButton",
                                        command=self.atualizar)
        self.btn_atualizar.pack(side="right")

        self.caixa_log = ttk.Frame(corpo)
        self.log = tk.Text(self.caixa_log, height=8, state="disabled", wrap="none",
                           font=("Consolas", 9), relief="flat", bg=COR["trilho"], fg=COR["suave"],
                           padx=10, pady=8, highlightthickness=0)
        rolagem = ttk.Scrollbar(self.caixa_log, command=self.log.yview)
        self.log.configure(yscrollcommand=rolagem.set)
        rolagem.pack(side="right", fill="y")
        self.log.pack(side="left", fill="both", expand=True)
        self.detalhes_visiveis = False

        ttk.Label(self, text=f"Em caso de erro ou dúvidas, fale com {CONTATO}",
                  style="Rodape.TLabel").pack(side="bottom", pady=(0, 12))

    def alternar_detalhes(self, mostrar=None):
        mostrar = (not self.detalhes_visiveis) if mostrar is None else mostrar
        if mostrar and not self.detalhes_visiveis:
            self.caixa_log.pack(fill="both", expand=True, pady=(8, 0))
            self.geometry(f"{self.winfo_width()}x{max(self.winfo_height(), 760)}")
        elif not mostrar and self.detalhes_visiveis:
            self.caixa_log.pack_forget()
        self.detalhes_visiveis = mostrar
        self.btn_detalhes.configure(text="Esconder detalhes" if mostrar else "Mostrar detalhes")

    def _colar(self, _evento):
        try:
            self.url.delete(0, "end")
            self.url.insert(0, self.clipboard_get().strip())
        except tk.TclError:
            pass

    def escolher_pasta(self):
        escolhida = filedialog.askdirectory(initialdir=self.pasta.get())
        if escolhida:
            self.pasta.set(escolhida)

    def abrir_pasta(self):
        ok, msg, _ = nucleo.checar_destino(self.pasta.get())
        if not ok:
            messagebox.showerror(TITULO, msg)
            return
        os.startfile(self.pasta.get())

    def _escrever(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", texto + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _limpar_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _set_ocupado(self, sim):
        self.ocupado = sim
        self.btn_baixar.configure(state="disabled" if sim else "normal")
        self.btn_atualizar.configure(state="disabled" if sim else "normal")
        self.btn_parar.configure(state="normal" if sim else "disabled")

    # ---------- Verificações antes de baixar ----------
    def _pode_comecar(self):
        faltando = nucleo.arquivos_faltando(PASTA_APP)
        if faltando:
            messagebox.showerror(TITULO, "Estes arquivos precisam estar na mesma pasta do Baixaí:\n\n"
                                 + "\n".join(faltando)
                                 + f"\n\nEm caso de dúvidas, fale com {CONTATO}.")
            return False
        return True

    def baixar(self):
        if self.ocupado:          # evita dois downloads ao mesmo tempo (ex.: Enter apertado)
            return
        url = self.url.get().strip()
        tipo_link = nucleo.classificar_link(url)
        if tipo_link == "vazio":
            messagebox.showinfo(TITULO, "Cole um link antes de baixar.")
            return
        if tipo_link == "invalido":
            messagebox.showerror(TITULO, "Esse texto não parece um link. Copie o endereço "
                                 "completo da barra do navegador, começando com https://")
            return
        if tipo_link == "spotify":
            messagebox.showinfo(TITULO, "O Baixaí funciona só com links do YouTube.\n\n"
                                "As músicas do Spotify são protegidas e só podem ser ouvidas "
                                "pelo próprio app do Spotify.")
            return
        if tipo_link == "outro_site":
            messagebox.showerror(TITULO, "O Baixaí aceita apenas links do YouTube "
                                 "(youtube.com, youtu.be ou music.youtube.com).")
            return
        if not self._pode_comecar():
            return

        so_este = tipo_link == "video"
        if tipo_link in ("video_em_lista", "mix"):
            if tipo_link == "mix":
                aviso = ("Esse link é de um Mix do YouTube, uma lista automática "
                         "que pode ter centenas de vídeos.")
            else:
                aviso = "Esse link é de um vídeo que está dentro de uma playlist."
            resposta = messagebox.askyesnocancel(
                TITULO, aviso + "\n\nSim: baixar só este vídeo\nNão: baixar a lista inteira")
            if resposta is None:
                return
            so_este = resposta

        destino = self.pasta.get()
        ok, msg, livre = nucleo.checar_destino(destino)
        if not ok:
            messagebox.showerror(TITULO, msg)
            return
        if livre < nucleo.ESPACO_MINIMO_GB and not messagebox.askyesno(
                TITULO, f"Só restam {livre:.1f} GB livres nesse disco. Continuar mesmo assim?"):
            return

        self._preparar_execucao()
        self.tipo_link = tipo_link
        if so_este:
            self.status.set("Verificando o vídeo...")
            self._em_segundo_plano(self._verificar_video, url, destino)
        else:
            self.status.set("Verificando o tamanho da lista...")
            self._em_segundo_plano(self._contar, url, destino)

    def _registrar_processo(self, proc):
        self.processo = proc
        if self.parado:
            nucleo.encerrar_arvore(proc)

    # ---------- Instalação no computador ----------
    def _deve_oferecer_instalacao(self):
        return (getattr(sys, "frozen", False) and not nucleo.esta_instalado(PASTA_APP)
                and not os.path.exists(os.path.join(PASTA_APP, nucleo.MARCA_NAO_PERGUNTAR)))

    def _oferecer_instalacao(self):
        if not messagebox.askyesno(
                TITULO, "Quer instalar o Baixaí neste computador?\n\n"
                "Ele vai ganhar um atalho na Área de Trabalho e no menu Iniciar. "
                "Depois disso, o zip e esta pasta baixada podem ser apagados."):
            try:
                open(os.path.join(PASTA_APP, nucleo.MARCA_NAO_PERGUNTAR), "w").close()
            except OSError:
                pass
            return
        self._set_ocupado(True)
        self.status.set("Instalando...")
        self._barra_animada(True)
        self._em_segundo_plano(self._instalar)

    def _instalar(self):
        exe = nucleo.instalar(PASTA_APP)
        atalhos = nucleo.criar_atalhos(exe)
        self.after(0, self._instalado, exe, atalhos)

    def _instalado(self, exe, atalhos):
        self._finalizar_interface("Baixaí instalado!", "ok", valor=100)
        if atalhos:
            msg = ("Pronto! O Baixaí está instalado e tem um atalho na Área de Trabalho.\n\n"
                   "Pode apagar o zip e esta pasta baixada. Daqui pra frente, abra pelo atalho.")
        else:
            msg = ("O Baixaí foi instalado, mas não consegui criar o atalho.\n\n"
                   "Procure por Baixaí no menu Iniciar ou fale com " + CONTATO + ".")
        messagebox.showinfo(TITULO, msg)
        try:
            subprocess.Popen([exe], cwd=os.path.dirname(exe))
            self.destroy()
        except OSError:
            pass

    def _em_segundo_plano(self, tarefa, *args):
        """Roda uma tarefa em segundo plano; se ela falhar, a tela não fica travada."""
        def executar():
            try:
                tarefa(*args)
            except Exception as erro:
                self.after(0, self._falhou, erro)
        threading.Thread(target=executar, daemon=True).start()

    def _falhou(self, erro):
        self._escrever(f"Erro inesperado: {type(erro).__name__}: {erro}")
        self._finalizar_interface(f"Algo deu errado. Fale com {CONTATO} e mande um print dos detalhes.", "erro")

    def _verificar_video(self, url, destino):
        info = nucleo.info_video(YTDLP, url, ao_iniciar=self._registrar_processo)
        self.after(0, self._depois_de_verificar, url, destino, info)

    def _depois_de_verificar(self, url, destino, info):
        self.processo = None
        if self.parado:
            self._finalizar_interface("Download cancelado.")
            return
        if info:
            duracao, ao_vivo = info
            if ao_vivo:
                self._finalizar_interface("Transmissões ao vivo não podem ser baixadas.", "aviso")
                messagebox.showwarning(TITULO, "Esse link é de uma transmissão ao vivo, que não tem fim "
                                       "definido. Espere a live acabar e tente de novo.")
                return
            if duracao > nucleo.LIMITE_HORAS * 3600:
                if not messagebox.askyesno(
                        TITULO, f"Esse vídeo tem {nucleo.formatar_duracao(duracao)}. O arquivo pode ficar "
                        f"muito grande e demorar para baixar e converter.\n\nBaixar mesmo assim?"):
                    self._finalizar_interface("Download cancelado.")
                    return
        self._iniciar_download(url, destino, so_este=True, limite=None)

    def _contar(self, url, destino):
        total = nucleo.contar_itens(YTDLP, url, ao_iniciar=self._registrar_processo)
        self.after(0, self._depois_de_contar, url, destino, total)

    def _depois_de_contar(self, url, destino, total):
        if self.parado:
            self._finalizar_interface("Download cancelado.")
            return
        self.processo = None
        limite = None
        if total is None and self.tipo_link == "mix":
            resposta = messagebox.askyesnocancel(
                TITULO,
                "O YouTube não informou quantos vídeos esse Mix tem, e ele pode ter centenas.\n\n"
                "Sim: baixar todos\n"
                f"Não: baixar só os primeiros {nucleo.LIMITE_AVISO}\n"
                "Cancelar: desistir")
            if resposta is None:
                self._finalizar_interface("Download cancelado.")
                return
            if resposta is False:
                limite = nucleo.LIMITE_AVISO
        elif total and total > nucleo.LIMITE_AVISO:
            resposta = messagebox.askyesnocancel(
                TITULO,
                f"Essa lista tem {total} vídeos. Baixar tudo pode levar horas e fazer "
                f"o YouTube bloquear temporariamente os downloads.\n\n"
                f"Sim: baixar todos os {total}\n"
                f"Não: baixar só os primeiros {nucleo.LIMITE_AVISO}\n"
                f"Cancelar: desistir")
            if resposta is None:
                self._finalizar_interface("Download cancelado.")
                return
            if resposta is False:
                limite = nucleo.LIMITE_AVISO
        self._iniciar_download(url, destino, so_este=False, limite=limite)

    # ---------- Execução ----------
    def _barra_animada(self, sim):
        # Guarda o estado aqui em vez de perguntar à barra: o Tkinter devolve
        # o "mode" num formato que não pode ser comparado com texto.
        if sim and not self.animando:
            self.animando = True
            self.barra.configure(mode="indeterminate")
            self.barra.start(12)
        elif not sim and self.animando:
            self.animando = False
            self.barra.stop()
            self.barra.configure(mode="determinate")

    def _cor_status(self, tipo=None):
        self.lbl_status.configure(fg=COR.get(tipo, COR["texto"]) if tipo else COR["texto"],
                                  font=("Segoe UI Semibold", 11) if tipo else ("Segoe UI", 10))
        if tipo == "erro":
            self.alternar_detalhes(True)   # em caso de erro, mostra o log para facilitar a ajuda

    def _preparar_execucao(self):
        self.prontos = 0
        self.pulados = 0
        self.incompleto = None
        self._cor_status()
        self._barra_animada(False)
        self.erros = 0
        self.bloqueio = None
        self.parado = False
        self.item_atual = ""
        self.barra["value"] = 0
        self._limpar_log()
        self._set_ocupado(True)

    def _iniciar_download(self, url, destino, so_este, limite):
        filtro = nucleo.FILTRO_VIDEO if so_este else nucleo.FILTRO_LISTA
        cmd = nucleo.montar_comando(YTDLP, PASTA_APP, destino, self.tipo.get(),
                                    url, so_este=so_este, limite=limite, filtro=filtro)
        self.status.set("Preparando...")
        threading.Thread(target=self._rodar, args=(cmd, "Download"), daemon=True).start()

    def atualizar(self):
        if self.ocupado or not self._pode_comecar():
            return
        self._preparar_execucao()
        self.status.set("Procurando atualização do yt-dlp...")
        threading.Thread(target=self._rodar, args=([YTDLP, "-U"], "Atualização"), daemon=True).start()

    def _rodar(self, cmd, nome):
        codigo = -1
        try:
            self.processo = nucleo.iniciar(cmd)
            if self.parado:        # Parar clicado enquanto o processo abria
                nucleo.encerrar_arvore(self.processo)
            for linha in self.processo.stdout:
                self.after(0, self._ler_linha, linha.rstrip())
            codigo = self.processo.wait()
        except Exception as erro:
            self.after(0, self._escrever, f"Erro ao iniciar: {erro}")
        self.after(0, self._terminou, codigo, nome)

    def _ler_linha(self, linha):
        info = nucleo.interpretar_linha(linha)
        if "pct" not in info:
            self._escrever(linha)
        if "item" in info or "pct" in info:
            self._barra_animada(False)
        if "item" in info:
            atual, total = info["item"]
            self.item_atual = f"{atual} de {total}"
            self.status.set(f"Baixando {self.item_atual}")
            self.barra["value"] = 0
        if "nome" in info:
            prefixo = f"{self.item_atual}: " if self.item_atual else ""
            if info.get("fase") == "convertendo":
                self.incompleto = info.get("caminho")
                formato = "MP3" if self.tipo.get() == "mp3" else "MP4"
                self.status.set(f"{prefixo}Convertendo para {formato}, aguarde... {info['nome']}")
                self._barra_animada(True)
            else:
                self.status.set(prefixo + info["nome"])
        if info.get("fase") == "pronto":
            self.prontos += 1
            self.incompleto = None
        if "pct" in info:
            self.barra["value"] = info["pct"]
        if info.get("erro"):
            self.erros += 1
        if info.get("pulado"):
            self.pulados += 1
        if info.get("bloqueio"):
            self.bloqueio = info["bloqueio"]

    def parar(self):
        if self.ocupado and not self.parado:
            self.parado = True
            self.status.set("Parando...")
            nucleo.encerrar_arvore(self.processo)

    def fechar(self):
        self.parado = True
        nucleo.encerrar_arvore(self.processo)
        self._apagar_incompleto()
        self.destroy()

    def _finalizar_interface(self, mensagem, tipo=None, valor=None):
        self._barra_animada(False)
        if valor is not None:
            self.barra["value"] = valor
        self._cor_status(tipo)
        self.processo = None
        self.item_atual = ""
        self._set_ocupado(False)
        self.status.set(mensagem)

    def _apagar_incompleto(self):
        """Um MP3/MP4 interrompido no meio da conversão fica corrompido e seria pulado
        no próximo download por já existir, então ele é apagado."""
        if self.incompleto and os.path.exists(self.incompleto):
            try:
                os.remove(self.incompleto)
            except OSError:
                pass
        self.incompleto = None

    def _terminou(self, codigo, nome):
        if self.parado:
            self._apagar_incompleto()
            self._finalizar_interface(f"{nome} interrompido. O que já foi baixado continua na pasta.",
                                      "aviso", valor=0)
            return
        tipo = "aviso"
        if nome == "Atualização":
            msg, tipo = "Atualização concluída. Veja os detalhes abaixo.", "ok"
        elif self.bloqueio == "limite":
            msg = ("O YouTube limitou os downloads por excesso de pedidos. Espere uns 30 minutos "
                   "e baixe a mesma lista de novo: o que já foi baixado é pulado.")
        elif self.bloqueio == "robo":
            msg = ("O YouTube pediu confirmação de que não é um robô. Espere algumas horas, "
                   f"clique em Atualizar yt-dlp e tente de novo. Se continuar, fale com {CONTATO}.")
        elif self.erros and self.prontos:
            msg = (f"Download concluído: {self.prontos} arquivo(s) salvos. "
                   f"{self.erros} item(ns) não puderam ser baixados (removidos ou bloqueados).")
        elif codigo == 0:
            msg, tipo = "Download concluído!", "ok"
        else:
            msg, tipo = f"Algo deu errado. Tente Atualizar yt-dlp ou fale com {CONTATO}.", "erro"
        if self.pulados and nome == "Download":
            msg += (f" {self.pulados} vídeo(s) com mais de {nucleo.LIMITE_HORAS} horas ou ao vivo "
                    f"foram pulados; se quiser, baixe cada um pelo próprio link.")
            if tipo == "ok":
                tipo = "aviso"
        self._finalizar_interface(msg, tipo, valor=100)

        if nome != "Download":
            return
        self.bell()
        if tipo == "erro":
            messagebox.showerror(TITULO, msg)
        elif self.prontos and messagebox.askyesno(TITULO, msg + "\n\nAbrir a pasta agora?"):
            self.abrir_pasta()
        elif not self.prontos:
            messagebox.showwarning(TITULO, msg)


def nucleo_compativel():
    return getattr(nucleo, "VERSAO", 0) == NUCLEO_ESPERADO


if __name__ == "__main__":
    if not nucleo_compativel():
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror(TITULO, "Os arquivos baixai.py e baixai_nucleo.py são de versões "
                             "diferentes.\n\nBaixe os dois de novo e coloque juntos na mesma pasta.")
        raiz.destroy()
    else:
        App().mainloop()
