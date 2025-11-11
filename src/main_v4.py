import os
import re
import openpyxl
import yt_dlp
from moviepy.audio.io.AudioFileClip import AudioFileClip
from queue import Queue
from threading import Thread

# Globals
A, B, C, D, E = 0, 1, 2, 3, 4
download_queue = Queue()


def downloadAudio(yt_url, download_dir, new_folder, timestamps):

    try:
        new_folder_path = os.path.join(download_dir, str(new_folder))
        os.makedirs(new_folder_path, exist_ok=True)

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(new_folder_path, '%(title)s.%(ext)s'),
            'postprocessors': [
                {'key': 'FFmpegExtractAudio',
                 'preferredcodec': 'mp3', 
                 'preferredquality': '192'}],
         }

        # Download audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(yt_url, download=True)
            mp3_file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

            if timestamps:
                trimmed_output_path = os.path.join(new_folder_path, f"{info_dict['title']}_trim.mp3")
                trimAudio(mp3_file_path, trimmed_output_path, timestamps)
                os.remove(mp3_file_path)
            else:
                print(f"Download completed: {mp3_file_path}\n")

    except Exception as error:
        print(f"Error processing {yt_url}: {error}")


def timestampToSeconds(timestamp):

    match = re.match(r'(\d+):(\d+)', timestamp)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    return 0


def trimAudio(file_path, output_path, timestamps):

    audio = AudioFileClip(file_path)
    start, end = re.findall(r'\d+:\d+', timestamps)

    start_sec = timestampToSeconds(start)
    end_sec = min(timestampToSeconds(end), audio.duration)

    trimmed_audio = audio.subclip(start_sec, end_sec)
    trimmed_audio.write_audiofile(output_path, codec="libmp3lame")
    trimmed_audio.close()
    audio.close()


def processQueue():

    while True:
        task = download_queue.get()
        if task is None:
            break

        yt_url, download_dir, new_folder, timestamps = task
        
        print(f"Processing task: {yt_url} in {new_folder}")
        
        downloadAudio(yt_url, download_dir, new_folder, timestamps)
        download_queue.task_done()


def enqueueTasks(class_dir, worksheet, start_row, end_row):

    for row in worksheet.iter_rows(min_row=start_row, max_row=end_row, values_only=True):
        new_folder = row[C]
        yt_url = row[D]
        timestamps = row[E]

        if yt_url:
            download_queue.put((yt_url, class_dir, new_folder, timestamps))
        else:
            print("Skipping empty URL")


def main():

	# Match row numbers with directories
    download_dirs = ["musicas"]
    start_rows = [2]
    end_rows = [3]

    workbook = openpyxl.load_workbook("url-input4.xlsx")
    worksheet = workbook.active

    # Start the worker threads
    worker_threads = []
    for _ in range(4):  # Adjust the number of threads as needed
        worker = Thread(target=processQueue)
        worker.start()
        worker_threads.append(worker)

    # Enqueue tasks
    for i in range(len(download_dirs)):
        enqueueTasks(download_dirs[i], worksheet, start_rows[i], end_rows[i])

    # Signal end of queue
    for _ in worker_threads:
        download_queue.put(None)

    # Wait for all threads to finish
    for worker in worker_threads:
        worker.join()


if __name__ == "__main__":
    main()

