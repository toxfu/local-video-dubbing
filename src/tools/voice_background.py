import torchaudio
import torchaudio.transforms as T
import torch
import gc
import soundfile as sf
from pathlib import Path

from resources import VOICE_SEPARATOR, DEVICE


def voice_background(dir: str, audio_file: str, chunk_duration: float = 540.0):
    waveform, sr = torchaudio.load(audio_file)

    # Resamplear si es necesario
    if sr != 44100:
        resampler = T.Resample(orig_freq=sr, new_freq=44100)
        waveform = resampler(waveform)
        sr = 44100

    total_duration = waveform.shape[1] / sr

    # Asegurar 2 canales
    if waveform.shape[0] == 1:
        waveform = waveform.repeat(2, 1)
    elif waveform.shape[0] > 2:
        waveform = waveform[:2, :]

    chunk_samples = int(chunk_duration * sr)
    total_samples = waveform.shape[1]
    num_chunks = (total_samples + chunk_samples - 1) // chunk_samples

    voice_chunks = []
    background_chunks = []

    for i in range(num_chunks):
        start = i * chunk_samples
        end = min((i + 1) * chunk_samples, total_samples)
        chunk = waveform[:, start:end]

        with torch.inference_mode():
            input_tensor = chunk.unsqueeze(0).to(DEVICE)
            est_sources = VOICE_SEPARATOR(input_tensor).squeeze(0)

        voice_chunks.append(est_sources[0].cpu())
        background_chunks.append((est_sources[1] + est_sources[2] + est_sources[3]).cpu())

        del input_tensor, est_sources
        torch.cuda.empty_cache()
        gc.collect()

    # Concatenar los resultados
    voice_result = torch.cat(voice_chunks, dim=1)
    background_result = torch.cat(background_chunks, dim=1)

    voice_path = Path(dir) / "voice.wav"
    background_path = Path(dir) / "background.wav"

    sf.write(voice_path, voice_result.T.numpy(), sr)
    sf.write(background_path, background_result.T.numpy(), sr)

    del waveform, voice_result, background_result, voice_chunks, background_chunks
    gc.collect()
    torch.cuda.empty_cache()

    return voice_path, background_path, total_duration