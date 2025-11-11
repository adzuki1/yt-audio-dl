
PROJECT STILL IN PRODUCTION
# PT-BR
 
 Soon

# EN
#  VERSION 1

This repository contains `main_v1.py`, a Python script for downloading audio from YouTube videos, trimming it based on timestamps, and organizing the output into specified folders. This script relies on an Excel sheet for task configuration and provides basic functionality for audio processing.

## Features
- Download audio files from YouTube videos in MP3 format.
- Trim audio files based on user-provided timestamps.
- Organize downloads into folders specified in an Excel sheet.
- Automated batch processing of tasks defined in the Excel file.

## Dependencies
The following libraries are required to run the script:
- `os` (built-in)
- `re` (built-in)
- `openpyxl`: Excel file handling
- `yt_dlp`: YouTube video/audio downloading
- `moviepy`: Audio processing and trimming

To install the required external libraries, run:
```bash
pip install openpyxl yt-dlp moviepy
```

or
```bash
pip install -r requirements_v1_v2.txt
```

## File Structure
- **`main_v1.py`**: The main script for executing the tasks.
- **`test.xlsx`**: An Excel file used to configure download tasks.
- **`DOWNLOADS`**: Default directory where output files are saved.

## Excel Sheet Configuration
The script processes tasks from an Excel file. The columns in the sheet should be structured as follows:

| Column | Description                    |
| ------ | ------------------------------ |
| A      | Task ID (optional)             |
| B      | Task Description (optional)    |
| C      | Folder Name                    |
| D      | YouTube URL                    |
| E      | Timestamps (e.g., `1:00-2:30`) |

### Example:
| Task ID | Task Description | Folder Name | YouTube URL            | Timestamps |
|---------|------------------|-------------|------------------------|------------|
| 1       | Example Task     | Folder1     | https://youtu.be/xyz123 | 0:30-1:00  |

## Usage
1. Prepare an Excel file (`test.xlsx`) with tasks following the structure described above.
2. Place the script (`main_v1.py`) and the Excel file in the same directory.
3. Run the script:
   ```bash
   python3 main_v1.py
   ```
4. Processed audio files will be saved in the specified folders under the `DOWNLOADS` directory.

## Functions Overview

- **`downloadAudio(yt_url, download_dir, new_folder, timestamps)`**: Downloads and optionally trims audio from a YouTube video.

- **`timestampToSeconds(timestamp)`**: Converts a timestamp string to seconds.

- **`trimAudio(file_path, output_path, timestamps)`**: Trims an audio file based on provided timestamps.

- **`processTasks(dl_directory, worksheet, start_row, end_row)`**: Processes a range of tasks defined in the Excel file.

- **`main()`**: Entry point of the script; handles the overall workflow.

## Notes
- Ensure `FFmpeg` is installed and accessible in your system's PATH for audio processing.
- Tasks with empty YouTube URLs will be skipped.
- If no timestamps are provided, the entire audio file will be downloaded without trimming.

---

# VERSION 2

## Overview
This script, `main_v2.py`, is an enhancement of version 1, introducing multithreading using a queue to manage tasks. While it provides better scalability and modularity, it includes some bugs and limitations that need attention.

### Key Features in Version 2:
- **Multithreading**: Uses a worker thread pool to process tasks concurrently.
- **Queue-Based Task Management**: Tasks are added to a queue and processed sequentially by worker threads.
- **Error Handling**: Includes basic error handling mechanisms for downloads and audio processing.

---

## Changes from Version 1
- **Multithreading**: Version 2 introduces multithreading for improved scalability, allowing the script to handle multiple tasks concurrently. The `Queue` module and `Thread` class are used to manage task execution.
- **Worker Threads**: A configurable number of threads (default: 4) can be spawned to process tasks from the queue.
- **Task Queue**: Tasks are added to a queue and processed independently by each thread.
- **Improved Modularity**: Functions like `processQueue` and `main` are structured for better readability and reusability.

---

## Limitations and Known Issues
- **Task Counter**: The "Processing task" counter is not thread-safe, leading to possible misreporting of task indices.
- **Error with `None` Task**: Threads log errors when encountering the termination signal (`None`) due to attempting to process it as a task. This does not impact functionality but generates unnecessary log messages.
- **Sequential Downloads Per Thread**: While multithreading improves concurrency, each thread still processes tasks sequentially, limiting full parallel download performance.

---

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
1. **Thread Count**:
   - Adjust the `num_threads` variable in the `main` function based on your system's capability.


---

## Output
- **Console Logs**:
  - Task processing status for each thread.
  - Errors (e.g., download failures, trimming issues).
- **Downloaded Files**:
  - Saved in respective folders inside `DOWNLOADS`.
  - Trimmed files (if timestamps are provided).

---

## Known Bugs
1. **Termination Signal Handling**:
   - Threads attempt to process `None` and log unnecessary errors.
   - Fix: Add a check to skip `None` in `processQueue`.
2. **Task Counter Misalignment**:
   - Task counter (`Processing task X`) is shared among threads, leading to inaccurate indices.
   - Fix: Use a thread-safe counter mechanism.

---

## Planned Improvements
- Refactor `processQueue` to properly handle termination signals.
- Introduce logging instead of print statements for better debugging and tracking.
- Implement thread-safe counters.
- Optimize task concurrency for higher parallelism in downloads.

---

## Version History
- **Version 1.0**: Initial implementation with sequential task execution.
- **Version 2.0**: Added multithreading and queue-based task management.

---

## Notes
This version works for small-scale tasks but may require further refinements for production use or high-concurrency scenarios.

