from resources import TRANSCRIBER
import torch
import gc
from typing import List, Tuple


def speech_recognition(logs: List[Tuple[float, float, str]]) -> List[str]:
    audio_files = [log[2] for log in logs[1:-1]]  # Excluir los segmentos de inicio y fin    
            
    batch_results = TRANSCRIBER(
        audio_files,
        batch_size=64,
        generate_kwargs={"max_new_tokens": 256}
    )
    texts = [res['text'] for res in batch_results]
        
    # Liberar variables intermedias y memoria GPU/CPU
    del audio_files, batch_results
    torch.cuda.empty_cache()
    gc.collect()
    
    return texts