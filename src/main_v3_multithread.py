import os
import pandas as pd
from pydub import AudioSegment
import yt_dlp
from concurrent.futures import ThreadPoolExecutor

# Config
BASE_DIR = os.path.expanduser("musicas")
EXCEL_FILE = "test2.xlsx"
MAX_WORKERS = 4  # Adjust this based on your system capabilities


# Create directories from Excel file, to save each file separately
def createDirectory(folder_name):
    directory = os.path.join(BASE_DIR, folder_name)
    os.makedirs(directory, exist_ok=True)
    return directory


# Download as audio files from YouTube URLs
def downloadAudio(url, output_path):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return ydl.prepare_filename({'url': url})
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}\n")
        return None


# Parse timestamps and convert them to seconds for trimming
def parseTimestamp(timestamp):
    start, end = timestamp.split(' - ')
    start_sec = int(start.split(":")[0]) * 60 + int(start.split(":")[1])
    end_sec = int(end.split(":")[0]) * 60 + int(end.split(":")[1])
    return start_sec, end_sec


# Uses processed timestamps to trim audio files in an interval
def trimAudio(input_path, output_path=None, timestamp=None):
    try:
        start_sec, end_sec = parseTimestamp(timestamp)
        audio = AudioSegment.from_file(input_path)

        trimmed_audio = audio[start_sec * 1000:end_sec * 1000]

        # Default to overwriting the input file
        if output_path is None:
            output_path = input_path

        trimmed_audio.export(output_path, format="mp3")
        print(f"Áudio cortado salvo em: {output_path}\n")

    except Exception as e:
        print(f"Erro ao cortar áudio: {e}\n")


# Process each task: download and trim
def processTask(file_data):
    folder_name = file_data['Nome do Aluno']
    url = file_data['Link da música']
    timestamp = file_data['Período da música (2min)']

    try:
        # Create directory for the student
        directory = createDirectory(folder_name)

        # Download audio
        audio_path = downloadAudio(url, directory)

        # Trim audio
        if audio_path:
            trimAudio(audio_path, timestamp=timestamp)
        else:
            print(f"Skipping {folder_name}: Failed to download audio.")

    except Exception as e:
        print(f"Error processing {folder_name}: {e}")


# Main function to process tasks concurrently
def main():
    # Read Excel file
    df = pd.read_excel(EXCEL_FILE)

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(processTask, [row for _, row in df.iterrows()])

    print("All tasks completed.")


if __name__ == "__main__":
    main()

