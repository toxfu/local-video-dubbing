import torch
from typing import List
import soundfile as sf
from pathlib import Path
from resources import TRANSLATION, VOICE_PIPELINE, SR
import gc


def translate(tmp_path:str, original_texts: List[str]):
    tmp_path = Path(tmp_path)
    translate_segments_path = tmp_path / "translate_segments"
    translate_segments_path.mkdir(parents=True, exist_ok=True)
    #! cuando hay puntos en el texto, la traducción puede fallar porque los interpreta como final de oración
    
    replaced_original_texts = []
    strip_text = [text.strip() for text in original_texts]
    # reemplazar los puntos en todos los textos excepto el último
    for text in strip_text:
        new_text = text[:-1].replace('.', ',') + text[-1]
        replaced_original_texts.append(new_text)
    
    ##### batch processing #####
    text_translate = TRANSLATION(
        replaced_original_texts,
        batch_size= 64,
    )
    texts = [t['translation_text'] for t in text_translate]
    
    audios = []
    voice_generator = VOICE_PIPELINE(
        texts, voice='ef_dora',  # <= change voice here
        speed=1
    )

    for _, _, audio in voice_generator:
        audios.append(audio)
            
    ##### Ordered translated texts and audios #####
    if len(texts) != len(audios):
        raise ValueError(f"El número de textos traducidos no coincide con el número de audios generados.")
    for i, audio in enumerate(audios):
        filename = translate_segments_path / f"audio{i+1}.wav"
        sf.write(filename, audio.cpu().numpy(), SR)
    
    audio_durations = [len(audio) / SR for audio in audios]
    
    # Liberar memoria intermedia
    del text_translate, voice_generator, audios
    torch.cuda.empty_cache()
    gc.collect()

    return texts, audio_durations, translate_segments_path