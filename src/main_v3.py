import os
import pandas as pd
from pydub import AudioSegment
import yt_dlp

# Config
BASE_DIR = os.path.expanduser("musicas")
EXCEL_FILE = "test.xlsx"


# Create directories from Excel file, to save each file separately
def createDirectory(folder_name):
    directory = os.path.join(BASE_DIR, folder_name)
    os.makedirs(directory, exist_ok=True)
    return directory


# Download as audio files from Youtube URLs
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
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Return the path of the downloaded mp3 file
            filename = os.path.join(output_path, f"{info['title']}.mp3")
            return filename

    except Exception as e:
        print(f"Erro ao baixar {url}: {e}\n")
        return None


# Parse timestamps and convert them to seconds
def parseTimestamp(timestamp):
    try:
        start, end = timestamp.split(' - ')
        start_sec = int(start.split(":")[0]) * 60 + int(start.split(":")[1])
        end_sec = int(end.split(":")[0]) * 60 + int(end.split(":")[1])
        return start_sec, end_sec
    except Exception as e:
        raise ValueError(f"Erro ao processar timestamp '{timestamp}': {e}")


# Trim audio file based on timestamps
def trimAudio(input_path, output_path=None, timestamp=None):
    try:
        start_sec, end_sec = parseTimestamp(timestamp)
        audio = AudioSegment.from_file(input_path)

        trimmed_audio = audio[start_sec * 1000:end_sec * 1000]

        # Default output_path to input_path (replace file) or append "_trimmed"
        if output_path is None:
            output_path = input_path.replace(".mp3", "_trimmed.mp3")

        trimmed_audio.export(output_path, format="mp3")
        print(f"Áudio cortado salvo em: {output_path}\n")

    except Exception as e:
        print(f"Erro ao cortar áudio: {e}\n")


# Process each task from the Excel file
def processTask(file_data):
    folder_name = file_data['Nome do Aluno']
    url = file_data['Link da música']
    timestamp = file_data['Período da música (2min)']

    try:
        directory = createDirectory(folder_name)
        audio_path = downloadAudio(url, directory)

        if audio_path and os.path.exists(audio_path):
            trimAudio(audio_path, timestamp=timestamp)
        else:
            print(f"Skipping {folder_name}: Failed to download or locate audio.")
    except Exception as e:
        print(f"Error processing {folder_name}: {e}")


# Main function
def main():
    df = pd.read_excel(EXCEL_FILE)

    for _, row in df.iterrows():
        processTask(row)


if __name__ == "__main__":
    main()

