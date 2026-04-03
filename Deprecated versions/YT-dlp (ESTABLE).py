import yt_dlp
import os

VIDEO_DOWNLOAD_DIR = "G:\\Formateo Ryzen 7\\Programacion\\yt-dlp\\Descargas\\Video"
AUDIO_DOWNLOAD_DIR = "G:\\Formateo Ryzen 7\\Programacion\\yt-dlp\\Descargas\\Audio"


def cls():
    os.system("cls")


def progreso_descarga(d):
    if d["status"] == "downloading":
        print(f"\rDescargando: {d['_percent_str']} - {d['_speed_str']}", end="")
    elif d["status"] == "finished":
        print(f"\n¡Descarga completada! Guardado en {d['filename']}")


def descargar_video(url):
    try:
        # Obtener información sin descargar
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            height = info.get("height", 0)
            width = info.get("width", 0)
            is_single_stream = "requested_formats" not in info

            if height > 1920 and width > 1080:
                respuesta = (
                    input(
                        f"El video tiene una calidad superior a 1080p ({width}p). ¿Deseas descargarlo en su mejor calidad? (s/n): "
                    )
                    .strip()
                    .lower()
                )
                if respuesta != "s":
                    cls()
                    print("Descarga cancelada.")
                    return

        # Elegir formato según el tipo de stream (combinado o separado)
        formato = "best" if is_single_stream else "bestvideo+bestaudio/best"

        ydl_opts = {
            "format": formato,
            "outtmpl": f"{VIDEO_DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "ffmpeg_location": r"C:\ffmpeg\bin",
            "quiet": True,
            "progress_hooks": [progreso_descarga],
            "merge_output_format": "mp4",
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            ],
        }

        # Solo usar FFmpegMerger si hay streams separados
        if not is_single_stream:
            ydl_opts["postprocessors"] = [{"key": "FFmpegMerger"}]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        cls()
        print("Descarga completada")
        print(e)


def descargar_audio(url):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{AUDIO_DOWNLOAD_DIR}/%(title)s.%(ext)s",
            "ffmpeg_location": r"C:\ffmpeg\bin",  # Ruta explícita donde esta instalado el FFmpeg en la pc
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ],
            "quiet": True,
            "progress_hooks": [progreso_descarga],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as e:
        cls()
        print(f"Error al descargar: {e}")


def menu():
    while True:
        print("\n--- Descargador de YouTube ---")
        print("1. Descargar video en la mejor calidad")
        print("2. Descargar solo el audio (MP3)")
        print("3. Salir")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            cls()
            url = input("Introduce la URL del video: ").strip()
            descargar_video(url)
        elif opcion == "2":
            cls()
            url = input("Introduce la URL del video: ").strip()
            descargar_audio(url)
        elif opcion == "3":
            cls()
            print("¡Gracias por usar el programa!")
            break
        else:
            cls()
            print("Opción no válida, intenta de nuevo.")


menu()
