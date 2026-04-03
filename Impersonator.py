import os
import subprocess
import sys

# Configuration
FFMPEG_PATH = r"C:\ffmpeg\bin"
AUDIO_PATH = r"G:\Formateo Ryzen 7\Programacion\yt-dlp\Descargas\Audio"
VIDEO_PATH = r"G:\Formateo Ryzen 7\Programacion\yt-dlp\Descargas\Video"

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
        print("yt-dlp installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Error installing yt-dlp. Please install manually: pip install yt-dlp")
        return False

def check_dependencies():
    """Check and install optional dependencies for better compatibility"""
    print("\nChecking additional dependencies...")
    
    # Try to install curl-cffi with proper version for impersonation
    try:
        from curl_cffi import requests
        print("✓ curl_cffi is already installed and working")
    except ImportError:
        print("Installing curl-cffi for Cloudflare protection bypass...")
        print("This may take a moment...")
        try:
            # Install with version that supports impersonation
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "curl-cffi>=0.5.10"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✓ curl-cffi installed successfully!")
            print("  Please restart the program for changes to take effect.")
        except subprocess.CalledProcessError as e:
            print(f"⚠ Warning: Could not install curl-cffi")
            print("Some sites with Cloudflare protection may not work.")
            print("\nTo install manually, run:")
            print("  pip uninstall curl-cffi")
            print("  pip install --upgrade curl-cffi>=0.5.10")
    
    # Install brotli
    try:
        import brotli
        print("✓ brotli is already installed")
    except ImportError:
        print("Installing brotli...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "brotli"], 
                         capture_output=True, check=True)
            print("✓ brotli installed successfully!")
        except subprocess.CalledProcessError:
            print("⚠ Could not install brotli, but continuing anyway...")

def create_directories():
    """Create download directories if they don't exist"""
    os.makedirs(AUDIO_PATH, exist_ok=True)
    os.makedirs(VIDEO_PATH, exist_ok=True)

def download_video(url):
    """Download video with best quality"""
    print(f"\nDownloading video from: {url}")
    print(f"Saving to: {VIDEO_PATH}")
    
    # Base command
    command = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--ffmpeg-location", FFMPEG_PATH,
        "--extractor-args", "youtube:player_client=default",
        "-o", os.path.join(VIDEO_PATH, "%(title)s.%(ext)s"),
    ]
    
    # Check if curl_cffi is available for impersonation
    try:
        from curl_cffi import requests
        command.extend(["--extractor-args", "generic:impersonate=chrome"])
        print("Using Chrome impersonation for Cloudflare bypass...")
    except ImportError:
        print("Note: curl_cffi not available or outdated")
        print("To enable Cloudflare bypass, run: pip install --upgrade curl-cffi>=0.5.10")
    
    command.append(url)
    
    try:
        subprocess.run(command, check=True)
        print("\n✓ Video downloaded successfully!")
    except subprocess.CalledProcessError:
        print("\n✗ Error downloading video.")
        print("\nTroubleshooting:")
        print("1. Make sure curl-cffi is properly installed:")
        print("   pip uninstall curl-cffi")
        print("   pip install --upgrade curl-cffi>=0.5.10")
        print("2. Then restart this program")
        print("3. If still failing, the site may not be supported")

def download_audio(url):
    """Download audio only in MP3 format"""
    print(f"\nDownloading audio from: {url}")
    print(f"Saving to: {AUDIO_PATH}")
    
    # Base command
    command = [
        "yt-dlp",
        "-f", "bestaudio/best",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--ffmpeg-location", FFMPEG_PATH,
        "--extractor-args", "youtube:player_client=default",
        "-o", os.path.join(AUDIO_PATH, "%(title)s.%(ext)s"),
    ]
    
    # Check if curl_cffi is available for impersonation
    try:
        from curl_cffi import requests
        command.extend(["--extractor-args", "generic:impersonate=chrome"])
        print("Using Chrome impersonation for Cloudflare bypass...")
    except ImportError:
        print("Note: curl_cffi not available or outdated")
        print("To enable Cloudflare bypass, run: pip install --upgrade curl-cffi>=0.5.10")
    
    command.append(url)
    
    try:
        subprocess.run(command, check=True)
        print("\n✓ Audio downloaded successfully!")
    except subprocess.CalledProcessError:
        print("\n✗ Error downloading audio.")
        print("\nTroubleshooting:")
        print("1. Make sure curl-cffi is properly installed:")
        print("   pip uninstall curl-cffi")
        print("   pip install --upgrade curl-cffi>=0.5.10")
        print("2. Then restart this program")
        print("3. If still failing, the site may not be supported")

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
    
    # Check and install dependencies for Cloudflare bypass
    check_dependencies()
    
    # Create download directories
    create_directories()
    
    print("\n✓ Setup complete!")
    print("Supported platforms: YouTube, Twitter/X, Instagram, TikTok, Facebook, and many more!")
    
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
        print("\n\nProgram interrupted by user. Goodbye!")
        sys.exit(0)