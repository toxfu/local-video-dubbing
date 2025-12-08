from resources import TRANSCRIBER
import torch
import gc
from typing import List, Tuple

import librosa
import numpy as np

def estimate_gender(audio):
    y, sr = librosa.load(audio)
    # Extraer frecuencia fundamental
    f0, _, _ = librosa.pyin(
        y, 
        fmin=50, 
        fmax=300,
        sr=sr
    )
    f0 = f0[~np.isnan(f0)]  # Eliminar valores NaN
    mean_f0 = np.mean(f0)
    threshold = 165  # Hz
    if mean_f0 < threshold:
        gender = "Male"
    else:
        gender = "Female"
    return gender


def speech_recognition(logs: List[Tuple[float, float, str]], gender_option: str) -> List[str]:
    audio_files = [log[2] for log in logs[1:-1]]  # Excluir los segmentos de inicio y fin    
    
    if gender_option == "Auto":
        gender = estimate_gender(audio_files[0])
    else:
        gender = gender_option
    
    batch_results = TRANSCRIBER(
        audio_files,
        batch_size=64,
        generate_kwargs={"max_new_tokens": 256}
    )
    texts = [res['text'] for res in batch_results]
        
    del audio_files, batch_results
    torch.cuda.empty_cache()
    gc.collect()
    
    return texts, gender