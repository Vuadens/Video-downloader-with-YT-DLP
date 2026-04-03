import os
import subprocess
import sys

# Configuration
FFMPEG_PATH = r"C:\ffmpeg\bin"
AUDIO_PATH = r"G:\Formateo Ryzen 7\Descargas yt-dlp\Audio"
VIDEO_PATH = r"G:\Formateo Ryzen 7\Descargas yt-dlp\Video"

def cls():
    os.system("cls")

def check_yt_dlp():
    """Check if yt-dlp is installed"""
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_yt_dlp():
    """Install yt-dlp using pip"""
    print("\nyt-dlp is not installed. Installing now...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
        cls()
        print("yt-dlp installed successfully!")
        return True
    except subprocess.CalledProcessError:
        os.system("cls")
        print("Error installing yt-dlp. Please install manually: pip install yt-dlp")
        return False

def create_directories():
    """Create download directories if they don't exist"""
    os.makedirs(AUDIO_PATH, exist_ok=True)
    os.makedirs(VIDEO_PATH, exist_ok=True)

def download_video(url):
    """Download video with best quality"""
    print(f"\nDownloading video from: {url}")
    print(f"Saving to: {VIDEO_PATH}")
    
    command = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--ffmpeg-location", FFMPEG_PATH,
        "--recode-video", "mp4",
        "-o", os.path.join(VIDEO_PATH, "%(title)s.%(ext)s"),
        url
    ]
    
    try:
        subprocess.run(command, check=True)
        cls()
        print("\n✓ Video downloaded successfully!")
    except subprocess.CalledProcessError:
        print("\n✗ Error downloading video. Please check the URL and try again.")

def download_audio(url):
    """Download audio only in MP3 format"""
    print(f"\nDownloading audio from: {url}")
    print(f"Saving to: {AUDIO_PATH}")
    
    command = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--ffmpeg-location", FFMPEG_PATH,
        "-o", os.path.join(AUDIO_PATH, "%(title)s.%(ext)s"),
        url
    ]
    
    try:
        subprocess.run(command, check=True)
        print("\n✓ Audio downloaded successfully!")
    except subprocess.CalledProcessError:
        print("\n✗ Error downloading audio. Please check the URL and try again.")

def display_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("  VIDEO/AUDIO DOWNLOADER")
    print("="*50)
    print("\n1) Download Video")
    print("2) Download Audio Only")
    print("3) Exit")
    print("\n" + "="*50)

def main():
    """Main program loop"""
    # Check if yt-dlp is installed
    if not check_yt_dlp():
        if not install_yt_dlp():
            return
    
    # Create download directories
    create_directories()
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            url = input("\nEnter the video URL: ").strip()
            if url:
                download_video(url)
            else:
                print("Error: URL cannot be empty!")
        
        elif choice == "2":
            url = input("\nEnter the video URL: ").strip()
            if url:
                download_audio(url)
            else:
                os.system("cls")
                print("Error: URL cannot be empty!")
        
        elif choice == "3":
            print("\nThank you for using Video/Audio Downloader. Goodbye!")
            break
        
        else:
            print("\nInvalid choice! Please enter 1, 2, or 3.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system("cls")
        print("\n\nDe nada pa")
        sys.exit(0)