import subprocess
from pathlib import Path

def extract_audio_video(video_file_path):
    """
    Extrae el audio de un archivo de video y lo guarda en un archivo separado.

    :param video_file_path: Ruta del archivo de video de entrada.
    :return: Rutas de los archivos de audio y video extraídos.
    """
    # Validar que el archivo existe
    video_path = Path(video_file_path)
    if not video_path.is_file():
        raise FileNotFoundError(f"El archivo {video_file_path} no existe o no es accesible.")

    # Rutas de salida
    audio_output_path = video_path.with_suffix(".wav")
    video_output_path = video_path.with_name(f"{video_path.stem}_noaudio.webm")
    
    # Determinar si necesitamos recodificar basado en la extensión
    input_ext = video_path.suffix.lower()
    if input_ext == ".webm":
        # Si ya es webm, solo copiar el stream de video
        video_codec_params = ["-c:v", "copy"]
    else:
        # Si es otro formato (mp4, avi, etc.), convertir a VP9
        video_codec_params = ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0"]

    try:
        cmd = [
            "ffmpeg", "-i", str(video_file_path),
            "-map", "0:v", *video_codec_params, str(video_output_path),
            "-map", "0:a", "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(audio_output_path)
        ]
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al procesar el archivo {video_file_path}: {e}")

    return str(audio_output_path), str(video_output_path)