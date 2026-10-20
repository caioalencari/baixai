"""Regras do Baixaí que não dependem da janela (testáveis separadamente)."""
import os
import re
import shutil
import signal
import subprocess
from urllib.parse import urlparse, parse_qs

VERSAO = 7   # precisa ser igual ao NUCLEO_ESPERADO do baixai.py

SEM_JANELA = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
EXE = ".exe" if os.name == "nt" else ""

LIMITE_AVISO = 100          # listas maiores que isso pedem confirmação
LIMITE_HORAS = 3            # vídeos mais longos que isso pedem confirmação
FILTRO_LISTA = f"!is_live & duration<?{LIMITE_HORAS * 3600}"   # em listas, pula lives e vídeos longos
FILTRO_VIDEO = "!is_live"
ESPACO_MINIMO_GB = 2        # abaixo disso, avisa antes de começar

RE_ITEM = re.compile(r"Downloading item (\d+) of (\d+)")
RE_PCT = re.compile(r"^\[download\]\s+([\d.]+)%")
RE_DEST = re.compile(r"^\[download\] Destination: (.+)$")
RE_CONV = re.compile(r'^\[(?:ExtractAudio|Merger)\] (?:Destination: |Merging formats into ")(.+?)"?$')


# ---------- Link ----------
DOMINIOS_YOUTUBE = ("youtube.com", "youtu.be")


def _do_dominio(host, dominio):
    return host == dominio or host.endswith("." + dominio)


def classificar_link(url):
    """Retorna: vazio, invalido, outro_site, spotify, video, playlist, video_em_lista ou mix."""
    url = (url or "").strip()
    if not url:
        return "vazio"
    partes = urlparse(url)
    if partes.scheme not in ("http", "https") or not partes.netloc or " " in url:
        return "invalido"
    # hostname ignora truques como https://youtube.com@site-falso.com
    host = (partes.hostname or "").lower()
    if _do_dominio(host, "spotify.com") or host == "spotify.link":
        return "spotify"
    if not any(_do_dominio(host, d) for d in DOMINIOS_YOUTUBE):
        return "outro_site"
    q = parse_qs(partes.query)
    lista = q.get("list", [""])[0]
    tem_video = "v" in q or host == "youtu.be" or "/shorts/" in partes.path
    if lista:
        if lista.startswith("RD") or "start_radio" in q:
            return "mix"
        return "video_em_lista" if tem_video else "playlist"
    return "video"


# ---------- Instalação ----------
MARCA_NAO_PERGUNTAR = ".nao_perguntar_instalar"


def pasta_instalacao():
    base = os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")
    return os.path.join(base, "Programs", "Baixai")


def esta_instalado(pasta_app):
    return os.path.normcase(os.path.abspath(pasta_app)) == os.path.normcase(os.path.abspath(pasta_instalacao()))


def instalar(origem, destino=None):
    """Copia a pasta do app para o computador. Retorna o caminho do Baixai.exe instalado."""
    destino = destino or pasta_instalacao()
    shutil.copytree(origem, destino, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(MARCA_NAO_PERGUNTAR, "__pycache__"))
    return os.path.join(destino, f"Baixai{EXE}")


SCRIPT_ATALHO = r"""
$s = New-Object -ComObject WScript.Shell
foreach ($p in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {
  $l = $s.CreateShortcut((Join-Path $p ($env:BAIXAI_NOME + '.lnk')))
  $l.TargetPath = $env:BAIXAI_EXE
  $l.WorkingDirectory = $env:BAIXAI_PASTA
  $l.IconLocation = $env:BAIXAI_EXE
  $l.Save()
}
"""


def criar_atalhos(exe, nome="Baixaí"):
    """Cria atalhos na Área de Trabalho (mesmo se ela estiver no OneDrive) e no menu Iniciar."""
    if os.name != "nt":
        return False
    # Os caminhos vão por variáveis de ambiente, nunca dentro do comando, para não haver
    # problema com acentos, espaços ou aspas nos nomes das pastas.
    ambiente = dict(os.environ, BAIXAI_EXE=exe, BAIXAI_PASTA=os.path.dirname(exe), BAIXAI_NOME=nome)
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", SCRIPT_ATALHO],
                           env=ambiente, capture_output=True, timeout=60, creationflags=SEM_JANELA)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


# ---------- Arquivos e pasta ----------
def arquivos_faltando(pasta_app):
    nomes = [f"yt-dlp{EXE}", f"ffmpeg{EXE}", f"ffprobe{EXE}"]
    return [n for n in nomes if not os.path.exists(os.path.join(pasta_app, n))]


def checar_destino(pasta):
    """Retorna (ok, mensagem_de_erro, gb_livres)."""
    try:
        os.makedirs(pasta, exist_ok=True)
        teste = os.path.join(pasta, ".baixai_teste")
        with open(teste, "w") as f:
            f.write("ok")
        os.remove(teste)
    except OSError:
        return False, "Não dá para salvar nessa pasta. Escolha outra.", 0
    livre = shutil.disk_usage(pasta).free / 1024 ** 3
    return True, "", livre


# ---------- Comandos ----------
def comando_contar(ytdlp, url):
    return [ytdlp, "--flat-playlist", "--playlist-items", "1",
            "--print", "playlist_count", "--encoding", "utf-8", "--", url]


def _rodar_rapido(cmd, timeout, ao_iniciar=None):
    """Roda uma verificação curta. ao_iniciar recebe o processo, para o Parar poder encerrá-lo."""
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                text=True, encoding="utf-8", errors="replace",
                                creationflags=SEM_JANELA, start_new_session=(os.name != "nt"))
    except OSError:
        return ""
    if ao_iniciar:
        ao_iniciar(proc)
    try:
        saida, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        encerrar_arvore(proc)
        return ""
    return saida or ""


def contar_itens(ytdlp, url, timeout=45, ao_iniciar=None):
    """Pergunta ao yt-dlp quantos itens a lista tem. None se não souber."""
    for linha in _rodar_rapido(comando_contar(ytdlp, url), timeout, ao_iniciar).splitlines():
        if linha.strip().isdigit():
            return int(linha.strip())
    return None


def comando_info(ytdlp, url):
    return [ytdlp, "--no-playlist", "--print", "%(duration|0)s|%(is_live)s",
            "--encoding", "utf-8", "--", url]


def info_video(ytdlp, url, timeout=45, ao_iniciar=None):
    """Retorna (duração em segundos, ao_vivo) ou None se não conseguir descobrir."""
    for linha in _rodar_rapido(comando_info(ytdlp, url), timeout, ao_iniciar).splitlines():
        partes = linha.strip().split("|")
        if len(partes) == 2:
            try:
                duracao = int(float(partes[0]))
            except ValueError:
                duracao = 0
            return duracao, partes[1].strip() == "True"
    return None


def formatar_duracao(segundos):
    h, resto = divmod(int(segundos), 3600)
    m = resto // 60
    return f"{h}h{m:02d}min" if h else f"{m}min"


def montar_comando(ytdlp, pasta_app, destino, tipo, url, so_este=False, limite=None, filtro=None):
    modelo = os.path.join(destino, "%(playlist_title|Avulsos)s",
                          "%(playlist_index&{:03d} - |)s%(title)s.%(ext)s")
    cmd = [ytdlp, "--newline", "--encoding", "utf-8", "-i",
           "--no-playlist" if so_este else "--yes-playlist",
           "--ffmpeg-location", pasta_app,
           "--sleep-requests", "1", "--sleep-interval", "2", "--max-sleep-interval", "5",
           "--trim-filenames", "150", "--no-overwrites",
           "-o", modelo]
    if filtro:
        cmd += ["--match-filters", filtro]
    if limite and not so_este:
        cmd += ["--playlist-items", f"1:{int(limite)}"]
    deno = os.path.join(pasta_app, f"deno{EXE}")
    if os.path.exists(deno):
        cmd += ["--js-runtimes", f"deno:{deno}"]
    if tipo == "mp3":
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    else:
        cmd += ["-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b", "--merge-output-format", "mp4"]
    # "--" impede que um link começando com "-" seja lido como opção do yt-dlp
    return cmd + ["--", url]


# ---------- Leitura da saída ----------
def interpretar_linha(linha):
    """Extrai o que interessa para a tela a partir de uma linha do yt-dlp."""
    r = {}
    m = RE_ITEM.search(linha)
    if m:
        r["item"] = (int(m.group(1)), int(m.group(2)))
    m = RE_PCT.match(linha)
    if m:
        r["pct"] = float(m.group(1))
    m = RE_DEST.match(linha) or RE_CONV.match(linha)
    if m:
        nome = os.path.splitext(os.path.basename(m.group(1).replace("\\", "/")))[0]
        r["nome"] = re.sub(r"\.f\d+$", "", nome)
        if RE_CONV.match(linha):
            r["fase"] = "convertendo"
            r["caminho"] = m.group(1)
    if linha.startswith("Deleting original file") or "has already been downloaded" in linha:
        r["fase"] = "pronto"
    if "does not pass filter" in linha:
        r["pulado"] = True
    if linha.startswith("ERROR:"):
        r["erro"] = True
        if "429" in linha or "Too Many Requests" in linha:
            r["bloqueio"] = "limite"
        elif "confirm you" in linha and "bot" in linha:
            r["bloqueio"] = "robo"
    return r


# ---------- Processos ----------
def iniciar(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace",
                            creationflags=SEM_JANELA,
                            start_new_session=(os.name != "nt"))


def encerrar_arvore(proc):
    """Encerra o processo e todos os que ele abriu (yt-dlp e ffmpeg)."""
    if proc is None or proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       capture_output=True, creationflags=SEM_JANELA)
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
