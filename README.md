# PT-BR
 
 Soon

# EN

This repository contains a Python script that:
- Download audio from YouTube URLs provided in XLSX file.
- Create audio clips using timestamps provided in XLSX file.
- Organize the output into specified folders.

#  VERSION 1

## Features

- Download audio clips from YouTube URLs in MP3 format.
- Organize downloads into folders specified in XLSX file.
- Automated batch processing of tasks defined in XLSX file.

## Dependencies

- `os` (built-in)
- `re` (built-in)
- `openpyxl`: XLSX file handling
- `yt_dlp`: YouTube video/audio downloading
- `moviepy`: Audio processing and trimming

To install the required external libraries, run:
```bash
pip install openpyxl yt-dlp moviepy
```

or
```bash
pip install -r requirements.txt
```

## File Structure

- **`main_v1.py`**: The main script for executing the tasks.
- **`test.xlsx`**: An XLSX file used to configure download tasks.
- **`DOWNLOADS`**: Default directory where output files are saved.

## XLSX Sheet Configuration

This program processes tasks from an XLSX file. I choose to get data as following:

| Column | Description                    |
| ------ | ------------------------------ |
| C      | Folder Name                    |
| D      | YouTube URL                    |
| E      | Timestamps (e.g., `1:00-2:30`) |

### Example:

| Task ID | Reg | Folder Name | YouTube URL            | Timestamps |
|---------|------------------|-------------|------------------------|------------|
| 1       | 8282828202     | Dummy-1     | https://youtu.be/xyz123 | 0:30-1:00  |

## Functions Overview

- **`downloadAudio(yt_url, download_dir, new_folder, timestamps)`**: Downloads and optionally trims audio from a YouTube video.

- **`timestampToSeconds(timestamp)`**: Converts a timestamp string to seconds.

- **`trimAudio(file_path, output_path, timestamps)`**: Trims an audio file based on provided timestamps.

- **`processTasks(dl_directory, worksheet, start_row, end_row)`**: Processes a range of tasks defined in the XLSX file.

- **`main()`**: Entry point of the script; handles the overall workflow.

## Notes
- Ensure `FFmpeg` is installed and accessible in your system's PATH for audio processing.
- Tasks with empty YouTube URLs will be skipped.
- If no timestamps are provided, the entire audio file will be downloaded without trimming.

---

# VERSION 2

## Overview
This script, `main_v2.py`, is an enhancement of version 1, introducing multithreading using a queue to manage tasks. While it provides better scalability and modularity, it includes some bugs and limitations that need attention.

## Improvements from Version 1
- **Multithreading**: Version 2 introduces multithreading for improved scalability, allowing the script to handle multiple tasks concurrently. The `Queue` module and `Thread` class are used to manage task execution.
- **Worker Threads**: A configurable number of threads (default: 4) can be spawned to process tasks from the queue.
- **Task Queue**: Tasks are added to a queue and processed independently by each thread.
- **Error Handling**: Includes basic error handling mechanisms for downloads and audio processing.
- **Improved Modularity**: Functions like `processQueue` and `main` are structured for better readability and reusability.


## Limitations and Known Issues
- **Task Counter**: The "Processing task" counter is not thread-safe, leading to possible misreporting of task indices.
- **Error with `None` Task**: Threads log errors when encountering the termination signal (`None`) due to attempting to process it as a task. This does not impact functionality but generates unnecessary log messages.
- **Sequential Downloads Per Thread**: While multithreading improves concurrency, each thread still processes tasks sequentially, limiting full parallel download performance.


## Installation and Usage

### Dependencies
Ensure the following Python libraries are installed:
- `os`
- `openpyxl`
- `re`
- `moviepy`
- `queue`
- `threading`
- `yt_dlp`

Install dependencies using pip:
```bash
pip install openpyxl moviepy yt-dlp
```

### Configuration
**Thread Count**:
   - Adjust the `num_threads` variable in the `main` function based on your system's capability.

## Notes
This version works for small-scale tasks but may require further refinements for production use or high-concurrency scenarios.

---

## Version History
- **Version 1.0**: Initial implementation with sequential task execution.
- **Version 2.0**: Added multithreading and queue-based task management.