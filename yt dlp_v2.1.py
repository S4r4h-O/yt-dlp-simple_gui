import re
import os
import yt_dlp
from tkinter import Tk, filedialog
from colorama import init, Fore, Style
from datetime import datetime

# Inicializar colorama para Windows
init(autoreset=True)

# Função para selecionar o diretório de download
def select_download_directory():
    Tk().withdraw()  # Esconde a janela principal do Tkinter
    download_dir = filedialog.askdirectory()
    return download_dir

# Função para selecionar o diretório onde o log será salvo
def select_log_directory():
    Tk().withdraw()  # Esconde a janela principal do Tkinter
    log_dir = filedialog.askdirectory(title="Selecione o diretório para salvar o log")
    if log_dir:
        return log_dir
    else:
        return os.path.expanduser('~')  # Diretório padrão se nenhum for escolhido

# Função para limpar a URL da playlist
def clean_playlist_url(url):
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    if match:
        return f"https://www.youtube.com/playlist?list={match.group(1)}"
    else:
        return None

# Função para salvar o log em um arquivo .txt no diretório escolhido pelo usuário
def save_log(content):
    try:
        # Pergunta ao usuário onde salvar o log
        log_directory = select_log_directory()

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"log_yt_dlp_{timestamp}.txt"
        log_path = os.path.join(log_directory, filename)

        with open(log_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(Fore.GREEN + f"\nLog salvo como {log_path}")
    except PermissionError as e:
        print(Fore.RED + f"Erro de permissão ao salvar o log: {e}")
    except Exception as e:
        print(Fore.RED + f"Erro desconhecido ao salvar o log: {e}")

# Função de progresso personalizada para downloads
def my_hook(d):
    if d['status'] == 'downloading':
        progress = d['_percent_str']
        speed = d['_speed_str']
        eta = d['eta']
        print(f"Progresso: {progress}, Velocidade: {speed}, ETA: {eta}s", end='\r')
    elif d['status'] == 'finished':
        print(Fore.GREEN + "\nDownload concluído!")

# Função para baixar vídeos ou playlists com todas as opções configuráveis
def download_video():
    url = input(Fore.CYAN + "\nInsira a URL do vídeo ou playlist: ")
    if not url:
        print(Fore.RED + "Erro: Nenhuma URL foi fornecida.")
        input(Fore.YELLOW + "Pressione Enter para continuar...")
        return

    download_dir = select_download_directory()

    if not download_dir:
        print(Fore.RED + "Erro: Nenhum diretório selecionado.")
        input(Fore.YELLOW + "Pressione Enter para continuar...")
        return

    clean_url = clean_playlist_url(url) or url  # Limpar se for playlist, ou manter a URL normal

    # Exibir as opções para o usuário selecionar por número
    print(Fore.CYAN + "\nEscolha as opções avançadas (separadas por vírgula):")
    print("[1] Começar transmissões ao vivo do início")
    print("[2] Ignorar restrições geográficas")
    print("[3] Forçar bypass para um país específico")
    print("[4] Aplicar filtros específicos de vídeo")
    print("[5] Registrar vídeos baixados em um arquivo")
    print("[6] Escolher formato de vídeo")

    choices = input("Digite os números das opções desejadas (ex: 1,3,5): ")
    selected_options = choices.split(',')

    # Definir os formatos de vídeo suportados
    print(Fore.CYAN + "\nEscolha o formato de vídeo:")
    print("[1] mp4")
    print("[2] mp3")
    print("[3] webm")
    print("[4] flv")
    print("[5] 3gp")
    print("[6] m4a")
    print("[7] opus")
    
    format_choice = input("Digite o número do formato desejado (ou deixe em branco para a melhor qualidade): ") or '1'
    format_map = {
        '1': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # Melhor qualidade de vídeo com mp4
        '2': 'bestaudio[ext=mp3]/mp3',
        '3': 'bestvideo[ext=webm]+bestaudio[ext=webm]/webm',
        '4': 'bestvideo[ext=flv]+bestaudio[ext=flv]/flv',
        '5': 'bestvideo[ext=3gp]+bestaudio[ext=3gp]/3gp',
        '6': 'bestaudio[ext=m4a]/m4a',
        '7': 'bestaudio[ext=opus]/opus'
    }
    video_format = format_map.get(format_choice, 'best')  # Padrão para 'best' se a escolha for inválida

    # Configuração das opções avançadas com base na escolha do usuário
    advanced_options = {
        'live-from-start': '1' in selected_options,
        'geo_bypass': '2' in selected_options,
        'geo_bypass_country': input("Forçar bypass para um país específico (Deixe em branco para não usar): ") if '3' in selected_options else None,
        'match_filters': input("Aplicar filtros específicos de vídeo (Regex, opcional): ") if '4' in selected_options else None,
        'download_archive': input("Registrar vídeos baixados em um arquivo? (Informe o nome do arquivo ou deixe em branco): ") if '5' in selected_options else None,
        'format': video_format,
    }

    # Configuração das opções de rede
    network_options = {
        'proxy': input("Digite o proxy (URL) ou deixe em branco para nenhum: ") or None,
        'socket_timeout': int(input("Tempo de espera do socket (em segundos) ou deixe em branco para padrão: ") or 15),
    }

    # Verificar se o usuário deseja usar cookies
    use_cookies = input("Deseja usar um arquivo de cookies (para acessar vídeos privados)? (S/N): ").lower() == 's'
    cookies_file = input("Insira o caminho para o arquivo de cookies (ou deixe em branco se não for usar): ") if use_cookies else None

    # Configuração das opções gerais do yt-dlp
    options = {
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),  # Local de saída
        'progress_hooks': [my_hook],  # Função de progresso
        'cookiefile': cookies_file if cookies_file else None,  # Usar arquivo de cookies se fornecido
        'format': video_format,  # Sempre baixar na melhor qualidade disponível para o formato selecionado
        **advanced_options,
        **network_options
    }

    # Variável para armazenar o log
    log_content = f"Baixando de: {clean_url}\n"

    # Usando yt-dlp para baixar o vídeo/playlist
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(clean_url, download=True)
            log_content += f"Download concluído: {info['title']}\n"
            print(Fore.GREEN + f"\nDownload do vídeo '{info['title']}' concluído.")
            
            # Pergunta se deseja baixar o log
            download_log = input("Deseja salvar um log da operação? (S/N): ").lower() == 's'
            if download_log:
                save_log(log_content)

    except Exception as e:
        error_message = f"Erro ao baixar vídeo/playlist: {e}"
        log_content += error_message
        print(Fore.RED + error_message)
        input(Fore.YELLOW + "Pressione Enter para continuar...")  # Manter a janela aberta após erro

    input(Fore.YELLOW + "\nPressione Enter para continuar...")
    main_menu()

# Função para baixar apenas os títulos de uma playlist
def download_titles():
    url = input(Fore.CYAN + "\nInsira a URL da playlist: ")
    if not url:
        print(Fore.RED + "Erro: Nenhuma URL foi fornecida.")
        input(Fore.YELLOW + "Pressione Enter para continuar...")
        return

    clean_url = clean_playlist_url(url)

    if not clean_url:
        print(Fore.RED + "Erro: URL da playlist inválida.")
        input(Fore.YELLOW + "Pressione Enter para continuar...")  # Manter a janela aberta após erro
        return

    # Verificar se o usuário deseja usar cookies
    use_cookies = input("Deseja usar um arquivo de cookies (para acessar playlists privadas)? (S/N): ").lower() == 's'
    cookies_file = input("Insira o caminho para o arquivo de cookies (ou deixe em branco se não for usar): ") if use_cookies else None

    # Configuração das opções para o yt-dlp
    options = {
        'quiet': True,  # Reduz a saída desnecessária
        'extract_flat': True,  # Extrai apenas os metadados (sem baixar vídeos)
        'skip_download': True,  # Pular o download
        'print': 'title',  # Imprimir apenas os títulos
        'flat-playlist': True,  # Garantir que apenas metadados da playlist sejam extraídos
        'cookiefile': cookies_file if cookies_file else None  # Usar arquivo de cookies se fornecido
    }

    # Variável para armazenar o log
    log_content = ""

    # Usando yt-dlp para listar títulos
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            result = ydl.extract_info(clean_url, download=False)
            for entry in result.get('entries', []):
                title = entry.get('title')
                if title:
                    log_content += f"{title}\n"
            print(Fore.GREEN + "\nTítulos extraídos com sucesso!")
            save_log(log_content)

    except Exception as e:
        error_message = f"Erro ao obter títulos: {e}"
        log_content += error_message
        print(Fore.RED + error_message)
        input(Fore.YELLOW + "Pressione Enter para continuar...")  # Manter a janela aberta após erro

    input(Fore.YELLOW + "\nPressione Enter para continuar...")
    main_menu()

# Função para exibir o menu principal
def main_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + "YT-DLP Interface - Menu Principal\n")
    print(Fore.YELLOW + "[1] Baixar Vídeo/Playlist")
    print("[2] Baixar apenas títulos da Playlist")
    print(Fore.RED + "[3] Sair")

    choice = input(Fore.CYAN + "\nEscolha uma opção: ")

    if choice == '1':
        download_video()
    elif choice == '2':
        download_titles()
    elif choice == '3':
        exit()
    else:
        print(Fore.RED + "\nOpção Inválida!")
        input(Fore.YELLOW + "Pressione Enter para continuar...")
        main_menu()

# Ponto de entrada
if __name__ == '__main__':
    main_menu()
