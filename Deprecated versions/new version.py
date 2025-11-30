import yt_dlp
import os

# Ruta fija para guardar las descargas
VIDEO_DOWNLOAD_DIR = "G:\\Formateo Ryzen 7\\Programacion\\yt-dlp\\Descargas\\Video"
AUDIO_DOWNLOAD_DIR = "G:\\Formateo Ryzen 7\\Programacion\\yt-dlp\\Descargas\\Audio"

def progreso_descarga(d):
    if d['status'] == 'downloading':
        print(f"\rDescargando: {d['_percent_str']} - {d['_speed_str']}", end="")
    elif d['status'] == 'finished':
        print(f"\n¡Descarga completada! Guardado en {d['filename']}")

def descargar_video(url):
    """Descarga el video con la mejor calidad disponible, desde el sitio que quieras."""
    try:
        # Obtener información sin descargar
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            height = info.get('height', 0)
            width = info.get("width", 0)
            is_single_stream = 'requested_formats' not in info

            if height > 1080:
                respuesta = input(f"El video tiene una calidad superior a 1080p ({height}p). ¿Deseas descargarlo en su mejor calidad (por ejemplo, 4K)? (s/n): ").strip().lower()
                if respuesta != 's':
                    # Forzar descarga como máximo en 1080p
                    formato = 'best[height<=1080]' if is_single_stream else 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                else:
                    formato = 'best' if is_single_stream else 'bestvideo+bestaudio/best'
            else:
                formato = 'best' if is_single_stream else 'bestvideo+bestaudio/best'

        ydl_opts = {
            'format': formato,
            'outtmpl': f'{VIDEO_DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'ffmpeg_location': r'C:\\ffmpeg',
            'quiet': False,
            'progress_hooks': [progreso_descarga],
        }

        if not is_single_stream:
            ydl_opts['postprocessors'] = [{'key': 'FFmpegMerger'}]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        print(f"Error al descargar: {e}")

def descargar_audio(url):
    """Descarga solo el audio del video."""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{AUDIO_DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'ffmpeg_location': r'C:\\ffmpeg',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'flac',
                'preferredquality': '192',
            }],
            'quiet': False,
            'progress_hooks': [progreso_descarga],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        print(f"Error al descargar: {e}")

def menu():
    while True:
        print("\n--- Descargador de YouTube ---")
        print("1. Descargar video en la mejor calidad")
        print("2. Descargar solo el audio (MP4)")
        print("3. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            url = input("Introduce la URL del video: ").strip()
            descargar_video(url)
        elif opcion == '2':
            url = input("Introduce la URL del video: ").strip()
            descargar_audio(url)
        elif opcion == '3':
            print("¡Gracias por usar el programa!")
            break
        else:
            print("Opción no válida, intenta de nuevo.")

if __name__ == "__main__":
    menu()
