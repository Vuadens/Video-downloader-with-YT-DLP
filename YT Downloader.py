import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

DEFAULT_AUDIO_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "YT-DLP", "Audio")
DEFAULT_VIDEO_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "YT-DLP", "Video")
DEFAULT_FFMPEG_PATH = ""
DEFAULT_COOKIES_PATH = ""
DEFAULT_BROWSER_COOKIES = "none"
DEFAULT_PREFER_PROGRESSIVE = True


def check_yt_dlp():
    """Check if yt-dlp is installed."""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_yt_dlp():
    """Install yt-dlp using pip."""
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def create_directories(audio_path, video_path):
    """Create download directories if they don't exist."""
    os.makedirs(audio_path, exist_ok=True)
    os.makedirs(video_path, exist_ok=True)


def build_video_command(
    url,
    video_path,
    ffmpeg_path,
    player_client,
    cookies_path,
    browser_cookies,
    prefer_progressive,
):
    if prefer_progressive:
        format_selector = "best[ext=mp4]/best"
    elif ffmpeg_path:
        format_selector = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else:
        format_selector = "best[ext=mp4]/best"

    command = [
        "yt-dlp",
        "-f",
        format_selector,
        "-o",
        os.path.join(video_path, "%(title)s.%(ext)s"),
    ]
    if ffmpeg_path:
        command.extend(["--merge-output-format", "mp4", "--recode-video", "mp4"])
        command.extend(["--ffmpeg-location", ffmpeg_path])
    if player_client:
        command.extend(["--extractor-args", f"youtube:player_client={player_client}"])
    if cookies_path:
        command.extend(["--cookies", cookies_path])
    if browser_cookies and browser_cookies != "none":
        command.extend(["--cookies-from-browser", browser_cookies])
    command.append(url)
    return command


def build_audio_command(
    url,
    audio_path,
    ffmpeg_path,
    player_client,
    cookies_path,
    browser_cookies,
):
    command = [
        "yt-dlp",
        "-f",
        "bestaudio/best",
        "-x",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "-o",
        os.path.join(audio_path, "%(title)s.%(ext)s"),
    ]
    if ffmpeg_path:
        command.extend(["--ffmpeg-location", ffmpeg_path])
    if player_client:
        command.extend(["--extractor-args", f"youtube:player_client={player_client}"])
    if cookies_path:
        command.extend(["--cookies", cookies_path])
    if browser_cookies and browser_cookies != "none":
        command.extend(["--cookies-from-browser", browser_cookies])
    command.append(url)
    return command


class DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YT-DLP Video/Audio Downloader")
        self.root.geometry("760x520")

        self.url_var = tk.StringVar()
        self.audio_path_var = tk.StringVar(value=DEFAULT_AUDIO_PATH)
        self.video_path_var = tk.StringVar(value=DEFAULT_VIDEO_PATH)
        self.ffmpeg_path_var = tk.StringVar(value=DEFAULT_FFMPEG_PATH)
        self.cookies_path_var = tk.StringVar(value=DEFAULT_COOKIES_PATH)
        self.status_var = tk.StringVar(value="Ready. Check yt-dlp status before downloading.")
        self.player_client_var = tk.StringVar(value="android")
        self.browser_cookies_var = tk.StringVar(value=DEFAULT_BROWSER_COOKIES)
        self.prefer_progressive_var = tk.BooleanVar(value=DEFAULT_PREFER_PROGRESSIVE)

        self.log_queue = queue.Queue()
        self.worker_thread = None

        self._build_ui()
        self._update_yt_dlp_status()
        self._poll_log_queue()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=16)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(
            main_frame,
            text="YouTube Video/Audio Downloader",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w", pady=(0, 12))

        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", pady=(0, 12))

        self._add_form_row(form_frame, "Video URL:", self.url_var)
        self._add_browse_row(
            form_frame,
            "Audio download folder:",
            self.audio_path_var,
            is_directory=True,
        )
        self._add_browse_row(
            form_frame,
            "Video download folder:",
            self.video_path_var,
            is_directory=True,
        )
        self._add_browse_row(
            form_frame,
            "FFmpeg location (optional):",
            self.ffmpeg_path_var,
            is_directory=True,
        )
        self._add_browse_row(
            form_frame,
            "Cookies file (optional):",
            self.cookies_path_var,
            is_directory=False,
        )
        self._add_client_row(form_frame)
        self._add_browser_cookies_row(form_frame)
        self._add_progressive_row(form_frame)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 12))

        self.check_button = ttk.Button(
            button_frame,
            text="Check/Install yt-dlp",
            command=self._handle_check_install,
        )
        self.check_button.pack(side="left")

        self.video_button = ttk.Button(
            button_frame,
            text="Download Video",
            command=self._handle_download_video,
        )
        self.video_button.pack(side="left", padx=8)

        self.audio_button = ttk.Button(
            button_frame,
            text="Download Audio",
            command=self._handle_download_audio,
        )
        self.audio_button.pack(side="left")

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(status_frame, text="Status:").pack(side="left")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side="left", padx=8)

        log_frame = ttk.LabelFrame(main_frame, text="Download log")
        log_frame.pack(fill="both", expand=True)

        self.log_text = tk.Text(log_frame, height=12, wrap="word", state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True)

        log_scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=log_scroll.set)

    def _add_form_row(self, parent, label, variable):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=24).pack(side="left")
        entry = ttk.Entry(row, textvariable=variable)
        entry.pack(side="left", fill="x", expand=True)
        return entry

    def _add_browse_row(self, parent, label, variable, is_directory=False):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text=label, width=24).pack(side="left")
        entry = ttk.Entry(row, textvariable=variable)
        entry.pack(side="left", fill="x", expand=True)
        ttk.Button(
            row,
            text="Browse",
            command=lambda: self._browse_path(variable, is_directory),
        ).pack(side="left", padx=8)
        return entry

    def _add_client_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="YouTube player client:", width=24).pack(side="left")
        client_options = ["android", "web", "ios", "tv", "default"]
        combo = ttk.Combobox(
            row,
            textvariable=self.player_client_var,
            values=client_options,
            state="readonly",
        )
        combo.pack(side="left", fill="x", expand=True)
        combo.current(0)
        return combo

    def _add_browser_cookies_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Use browser cookies:", width=24).pack(side="left")
        options = ["none", "chrome", "edge", "firefox", "brave", "opera"]
        combo = ttk.Combobox(
            row,
            textvariable=self.browser_cookies_var,
            values=options,
            state="readonly",
        )
        combo.pack(side="left", fill="x", expand=True)
        combo.current(0)
        return combo

    def _add_progressive_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Prefer single-file MP4:", width=24).pack(side="left")
        ttk.Checkbutton(
            row,
            variable=self.prefer_progressive_var,
            text="Avoid DASH fragments (fewer 403 errors)",
        ).pack(side="left")
        return row

    def _browse_path(self, variable, is_directory):
        if is_directory:
            selected = filedialog.askdirectory()
        else:
            selected = filedialog.askopenfilename()
        if selected:
            variable.set(selected)

    def _append_log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _update_yt_dlp_status(self):
        if check_yt_dlp():
            self.status_var.set("yt-dlp found. Ready to download.")
        else:
            self.status_var.set("yt-dlp not installed. Click Check/Install.")

    def _handle_check_install(self):
        if check_yt_dlp():
            messagebox.showinfo("yt-dlp", "yt-dlp is already installed.")
            self._update_yt_dlp_status()
            return

        confirm = messagebox.askyesno(
            "Install yt-dlp",
            "yt-dlp is not installed. Install it now?",
        )
        if not confirm:
            return

        self.status_var.set("Installing yt-dlp...")
        success = install_yt_dlp()
        if success:
            messagebox.showinfo("yt-dlp", "yt-dlp installed successfully!")
        else:
            messagebox.showerror(
                "yt-dlp",
                "Installation failed. Run: pip install yt-dlp",
            )
        self._update_yt_dlp_status()

    def _handle_download_video(self):
        self._start_download(mode="video")

    def _handle_download_audio(self):
        self._start_download(mode="audio")

    def _start_download(self, mode):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
            return

        if not check_yt_dlp():
            messagebox.showwarning(
                "yt-dlp missing",
                "yt-dlp is not installed. Click Check/Install first.",
            )
            return

        audio_path = self.audio_path_var.get().strip()
        video_path = self.video_path_var.get().strip()
        ffmpeg_path = self.ffmpeg_path_var.get().strip()
        cookies_path = self.cookies_path_var.get().strip()
        player_client = self.player_client_var.get().strip()
        browser_cookies = self.browser_cookies_var.get().strip()
        prefer_progressive = self.prefer_progressive_var.get()
        create_directories(audio_path, video_path)

        if mode == "video":
            command = build_video_command(
                url,
                video_path,
                ffmpeg_path,
                player_client,
                cookies_path,
                browser_cookies,
                prefer_progressive,
            )
            action = "Downloading video"
        else:
            if not ffmpeg_path:
                messagebox.showwarning(
                    "FFmpeg required",
                    "Audio extraction needs FFmpeg. Please set the FFmpeg location.",
                )
                return
            command = build_audio_command(
                url,
                audio_path,
                ffmpeg_path,
                player_client,
                cookies_path,
                browser_cookies,
            )
            action = "Downloading audio"

        self._append_log(f"{action}: {url}")
        self._set_controls_state(tk.DISABLED)
        self.status_var.set(f"{action}...")

        self.worker_thread = threading.Thread(
            target=self._run_download,
            args=(command, action),
            daemon=True,
        )
        self.worker_thread.start()

    def _run_download(self, command, action):
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except FileNotFoundError:
            self.log_queue.put("yt-dlp was not found. Please install it.")
            self.log_queue.put(("status", "yt-dlp missing."))
            self.log_queue.put(("controls", "enable"))
            return

        for line in process.stdout or []:
            self.log_queue.put(line.rstrip())
        return_code = process.wait()

        if return_code == 0:
            self.log_queue.put(f"{action} completed successfully.")
            self.log_queue.put(("status", "Download completed."))
        else:
            self.log_queue.put(f"{action} failed. Please check the log above.")
            self.log_queue.put(("status", "Download failed."))
        self.log_queue.put(("controls", "enable"))

    def _poll_log_queue(self):
        while True:
            try:
                item = self.log_queue.get_nowait()
            except queue.Empty:
                break

            if isinstance(item, tuple):
                if item[0] == "status":
                    self.status_var.set(item[1])
                elif item[0] == "controls":
                    self._set_controls_state(tk.NORMAL)
            else:
                self._append_log(item)

        self.root.after(200, self._poll_log_queue)

    def _set_controls_state(self, state):
        self.video_button.configure(state=state)
        self.audio_button.configure(state=state)
        self.check_button.configure(state=state)


def main():
    root = tk.Tk()
    app = DownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
