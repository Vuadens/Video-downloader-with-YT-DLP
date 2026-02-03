# YouTube Video/Audio Downloader (GUI)

This project provides a simple desktop GUI for downloading YouTube videos or extracting audio using `yt-dlp`.

## Requirements

- Python 3.9+ with Tkinter (included with most Python distributions)
- `yt-dlp` (the app can install this for you)
- Optional: `ffmpeg` if you want audio extraction or video merge support
- Optional: cookies file or browser cookies if a video requires authentication

## How to run

```bash
python "YT Downloader.py"
```

## How to visualize the GUI

1. Run the command above.
2. A window titled **"YT-DLP Video/Audio Downloader"** will open.
3. Paste a YouTube URL.
4. Choose download folders (optional) and set FFmpeg if you want MP3 audio.
5. Optionally choose a cookies file or browser cookies (Chrome/Edge/Firefox) and a YouTube player client.
6. Click **Download Video** or **Download Audio**.

If `yt-dlp` is not installed, click **Check/Install yt-dlp** in the GUI to install it automatically.
