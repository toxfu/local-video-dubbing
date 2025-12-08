import torch
from typing import List
import soundfile as sf
from pathlib import Path
from resources import TRANSLATION_MODEL, TRANSLATION_TOKENIZER,\
VOICE_PIPELINE, SR, DEVICE, TARGET_LANGUAGES
import gc


def translate(tmp_path:str, original_texts: List[str], output_language: str, gender: str):
    tmp_path = Path(tmp_path)
    translate_segments_path = tmp_path / "translate_segments"
    translate_segments_path.mkdir(parents=True, exist_ok=True)
    #! cuando hay puntos en el texto, la traducción puede fallar porque los interpreta como final de oración
    
    fix_text = []
    strip_text = [text.strip() for text in original_texts]
    # reemplazar los puntos en todos los textos excepto el último
    for text in strip_text:
        new_text = text[:-1].replace('.', ',') + "."
        fix_text.append(new_text)
    
    ##### batch processing #####
    tokenizer = TRANSLATION_TOKENIZER
    model = TRANSLATION_MODEL
    
    language = TARGET_LANGUAGES[output_language]
    inputs = tokenizer(fix_text, return_tensors="pt", padding=True).to(DEVICE)
    translated_tokens = model.generate(
        **inputs, forced_bos_token_id=tokenizer.convert_tokens_to_ids(language[0]))
    texts = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
    voice = language[1] if gender == "Female" else language[2]
    
    audios = []
    voice_generator = VOICE_PIPELINE(texts, voice=voice,speed=1)

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
    del voice_generator, audios
    torch.cuda.empty_cache()
    gc.collect()

    return texts, audio_durations, translate_segments_path