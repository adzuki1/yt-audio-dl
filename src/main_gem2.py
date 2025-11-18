import os
import re
import openpyxl
import yt_dlp
import threading
# from moviepy.audio.io.AudioFileClip import AudioFileClip # [REMOVIDO] Não é mais necessário
from queue import Queue
from threading import Thread, Lock # Adicionado Lock
from datetime import datetime


# Globals
A, B, C, D, E = 0, 1, 2, 3, 4
download_queue = Queue()
log_entries = []
log_lock = Lock() # [NOVO] Lock para proteger a lista de log


def writeLog():
    """Escreve o log de execução em um arquivo."""
    log_file = "execution_log.txt"
    
    with open(log_file, "w") as log:
        log.write("Execution Log\n")
        log.write("=" * 50 + "\n")

        # Não precisamos de lock aqui, pois as threads já terminaram
        for entry in log_entries:
            log.write(entry + "\n")

    print(f"Log file created: {log_file}")


def timestampToSeconds(timestamp):
    """Converte 'MM:SS' para segundos totais."""
    match = re.match(r'(\d+):(\d+)', timestamp)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    return 0


def downloadAudio(yt_url, download_dir, new_folder, timestamps):
    """
    [FUNÇÃO OTIMIZADA]
    Baixa o áudio e o corta usando apenas yt-dlp e ffmpeg, em uma única etapa.
    """
    try:
        new_folder_path = os.path.join(download_dir, str(new_folder))
        os.makedirs(new_folder_path, exist_ok=True)

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            # O 'outtmpl' agora é o nome final do arquivo
            'outtmpl': os.path.join(new_folder_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                # [NOVO] Argumentos de pós-processamento
                'postprocessor_args': [] 
            }],
            'quiet': True, # Suprime a saída do yt-dlp no console
            'noplaylist': True,
        }

        # [MELHORIA] Lógica de corte movida para dentro do yt-dlp
        if timestamps:
            try:
                start, end = re.findall(r'\d+:\d+', timestamps)
                start_sec = timestampToSeconds(start)
                end_sec = timestampToSeconds(end)
                
                if end_sec <= start_sec:
                    raise ValueError("Timestamp final é menor ou igual ao inicial.")

                # Duração a ser cortada
                duration = end_sec - start_sec 
                
                # Modifica o postprocessor para incluir os comandos de corte do ffmpeg
                # -ss [start] = Seek (pular) para o tempo de início
                # -t [duration] = Gravar pela duração especificada
                ydl_opts['postprocessors'][0]['postprocessor_args'] = [
                    '-ss', str(start_sec),
                    '-t', str(duration)
                ]
                
                # Ajusta o nome do arquivo final para indicar o corte
                ydl_opts['outtmpl'] = os.path.join(new_folder_path, '%(title)s_trim.%(ext)s')
            
            except Exception as e:
                # Se houver erro nos timestamps, baixa o áudio completo
                with log_lock:
                    log_entries.append(f"WARNING: Invalid timestamp '{timestamps}' for {yt_url}. Downloading full audio. Error: {e}")
                timestamps = None # Força o download completo

        # Download e processamento
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(yt_url, download=True)
            
            # O yt-dlp não retorna o nome final pós-processado de forma confiável
            # Então, temos que "adivinhar" o nome final com base no 'outtmpl'
            
            # 1. Prepara o nome do arquivo como o yt-dlp faria
            base_path = ydl.prepare_filename(info_dict)
            
            # 2. Troca a extensão original (webm, m4a) pela extensão final (mp3)
            # Esta é a parte "frágil", mas necessária
            final_mp3_path = base_path.replace('.webm', '.mp3').replace('.m4a', '.mp3').replace('.opus', '.mp3')

            # Verifica se o arquivo final realmente existe após a "adivinhação"
            if not os.path.exists(final_mp3_path):
                 # Tenta uma adivinhação mais simples (trocando apenas a extensão)
                 base_name, _ = os.path.splitext(base_path)
                 final_mp3_path = base_name + ".mp3"
                 if not os.path.exists(final_mp3_path):
                    with log_lock:
                        log_entries.append(f"ERROR: Post-processed file not found for {yt_url}. Expected: {final_mp3_path}")
                    return

            log_msg = f"SUCCESS: Trimmed audio saved: {final_mp3_path}" if timestamps else f"SUCCESS: Download completed: {final_mp3_path}"
            with log_lock:
                log_entries.append(log_msg)

    except Exception as error:
        with log_lock:
            log_entries.append(f"ERROR: {yt_url} - {error}")


# [REMOVIDO] A função trimAudio não é mais necessária
# def trimAudio(file_path, output_path, timestamps):
#     ...


def processQueue():
    """
    [FUNÇÃO ATUALIZADA]
    Pega tarefas da fila e as processa. Inclui logs de thread.
    """
    thread_name = threading.current_thread().name
    print(f"[{thread_name}] Worker iniciado, aguardando tarefas...")

    while True:
        task = download_queue.get()

        if task is None:
            print(f"[{thread_name}] Sinal de 'None' recebido. Encerrando.")
            download_queue.task_done() # Sinaliza que a task 'None' foi concluída
            break

        yt_url, download_dir, new_folder, timestamps = task

        print(f"[{thread_name}] INICIANDO: {new_folder} | {yt_url}")
        
        start_time = datetime.now()
        downloadAudio(yt_url, download_dir, new_folder, timestamps)
        end_time = datetime.now()
        
        print(f"[{thread_name}] CONCLUÍDO: {new_folder} | {yt_url} | Duração: {end_time - start_time}")
        
        download_queue.task_done()


def enqueueTasks(class_dir, worksheet, start_row, end_row):
    """Enfileira tarefas lendo da planilha."""
    for row in worksheet.iter_rows(min_row=start_row, max_row=end_row, values_only=True):
        new_folder = row[C]
        yt_url = row[D]
        timestamps = row[E]

        if yt_url:
            download_queue.put((yt_url, class_dir, new_folder, timestamps))
        else:
            # Protege o log com o lock
            with log_lock:
                log_entries.append(f"WARNING: Skipping empty URL in row {row[A] if row[A] else 'Unknown'}")

def main():
#	download_dirs = ["musicas/3001", "musicas/3002", "musicas/3003"]
#	start_rows = [2, 27, 55]
#	end_rows = [26, 54, 85]
    download_dirs = ["DOWNLOADS"]
    start_rows = [2]
    end_rows = [10]

    try:
        workbook = openpyxl.load_workbook("test.xlsx")
    except FileNotFoundError:
        print("ERRO: Arquivo 'test.xlsx' não encontrado.")
        return
        
    worksheet = workbook.active

    # Define o número de threads (workers)
    # 4-8 é geralmente um bom número para tarefas de I/O (rede)
    num_worker_threads = 4 
    worker_threads = []
    
    print(f"Iniciando {num_worker_threads} worker threads...")
    for _ in range(num_worker_threads):
        worker = Thread(target=processQueue, daemon=True) # daemon=True faz a thread fechar se o script principal morrer
        worker.start()
        worker_threads.append(worker)

    # Enqueue tasks
    print("Enfileirando tarefas...")
    for i in range(len(download_dirs)):
        enqueueTasks(download_dirs[i], worksheet, start_rows[i], end_rows[i])

    # Espera todas as tarefas da fila serem processadas
    print("Todas as tarefas foram enfileiradas. Aguardando conclusão dos downloads...")
    download_queue.join()

    # Sinaliza o fim da fila para todas as threads
    # (Não é mais estritamente necessário se usarmos queue.join(), 
    # mas é uma boa prática para parar as threads 'None')
    print("Enviando sinal de 'None' para workers...")
    for _ in worker_threads:
        download_queue.put(None)

    # Espera todas as threads terminarem
    for worker in worker_threads:
        worker.join()

    print("Processamento concluído. Gerando log...")
    # Write the log file
    writeLog()

if __name__ == "__main__":
    main()
