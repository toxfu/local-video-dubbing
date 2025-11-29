import subprocess
import os
from resources import SR
from pathlib import Path
from typing import List, Tuple

def adjust_the_audio(translate_segments_path, i, audio_file, target_duration, audio_duration):
    output_file = translate_segments_path / f"output_accelerate_{i}.wav"
    factor = audio_duration / target_duration

    if 0 < abs(target_duration - audio_duration) <= 0.5:
        return str(audio_file), audio_duration

    if 0.8 <= factor:
        atempo = f"atempo={factor:.2f}"
        adjusted_duration = audio_duration / factor
    else:
        atempo = f"atempo=0.8"
        adjusted_duration = audio_duration / 0.8
    
    command = [
        "ffmpeg",
        "-y",
        "-i", audio_file,
        "-filter:a",
        f"{atempo}",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_file
    ]
    subprocess.run(command, check=True)
    return output_file, adjusted_duration

def silence_audio(translate_segments_path, i, duration):
    output_file = translate_segments_path / f"silence_{i}.wav"
    command = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r={SR}:cl=mono",  # Frecuencia estándar
        "-t", str(duration),
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_file
    ]
    subprocess.run(command, check=True)
    return output_file

def concatenate_audios(translate_segments_path, file_list, output_file):
    # Crear archivo de lista para ffmpeg
    list_file = translate_segments_path / "file_list.txt"
    with open(list_file, "w") as f:
        for file in file_list:
            # ruta absoluta para evitar problemas de ruta
            f.write(f"file '{os.path.abspath(file)}'\n")
    
    # Ejecutar ffmpeg
    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-ac", "2",
        "-c:a", "pcm_s16le",
        output_file
    ]
    subprocess.run(command, check=True)
    
    
def join_audios(translate_segments_path: Path,
                audio_durations: List[float], # only audios
                logs: List[Tuple[float, float, str]] # include start and end silence
    ):
    start_silence = logs.pop(0)
    start_silence_duration = start_silence[1] - start_silence[0]
    target_duration = [logs[i][1] - logs[i][0] for i in range(len(logs))]    # audios + end silence
    # listar todos los archivos de audio
    audio_files = [translate_segments_path / f"audio{i+1}.wav" for i in range(len(audio_durations))]

    concat_files = []
    
    if start_silence_duration > 0:
        silence_file = silence_audio(translate_segments_path, 0, start_silence_duration)
        concat_files.append(silence_file)
    
    for i, audio_file in enumerate(audio_files):
        file_name, adjust_duration = adjust_the_audio(translate_segments_path, i+1, audio_file, target_duration[i], audio_durations[i])
        concat_files.append(file_name)
        # add silence segments
        if i == len(audio_files) - 1:
            silence_duration = logs[i+1][1] - (logs[i][0] + adjust_duration)
        else:
            silence_duration = logs[i+1][0] - (logs[i][0] + adjust_duration)

        if silence_duration > 0:
            silence_file = silence_audio(translate_segments_path, i+1, silence_duration)
            concat_files.append(silence_file) 

    # Concatenar todos los archivos de audio en la ruta padre de translate_segments_path
    output_file = translate_segments_path.parent / "audio_translated.wav"
    concatenate_audios(translate_segments_path, concat_files, output_file)

    return output_file