from pydub import AudioSegment, silence
import os
from pathlib import Path
import gc
from typing import List, Tuple

def brute_split(start_ms: int,
                end_ms: int,
                max_segment_duration: float = 23_000
    ):
    segments = []
    current_start = start_ms
    while current_start < end_ms:
        current_end = min(current_start + max_segment_duration, end_ms)
        segments.append((current_start, current_end))
        current_start = current_end
    return segments

def audio_segment_silence(
    audio: AudioSegment,
    min_silence_len: int,
    silence_thresh: float,
    start_in = 0,
    max_segment_duration: int = 23_000,
    ) -> AudioSegment:
    if min_silence_len < 150:
        # Si min_silence_len es muy pequeño, hacer una división bruta
        return brute_split(start_in, start_in + len(audio))
    
    segments = silence.detect_nonsilent(
        audio, 
        min_silence_len,
        silence_thresh
    )
    durations = [(end - start) for start, end in segments]
    all_segments = []
    re_segments = []
    for i, (start, end) in enumerate(segments):
        if durations[i] < max_segment_duration:
            all_segments.append((start_in + start, start_in + end))
        else:
            re_segments.append((start, end))

    if re_segments:
        min_silence_len -= 150
        for start, end in re_segments:
            all_segments += audio_segment_silence(
                audio[start:end],
                min_silence_len,
                silence_thresh,
                start_in + start
            )
    return all_segments


def write_audios(
    audio: AudioSegment,
    segments: List[Tuple[int, int]],
    segments_path: Path
    ) -> List[Tuple[float, float, str]]:
    logs = []
    segment_counter = 1
    for start_ms, end_ms in segments:
        chunk = audio[start_ms:end_ms]
        filename = segments_path / f"audio{segment_counter}.wav"
        chunk.export(str(filename), format="wav")
        logs.append([start_ms / 1000, end_ms / 1000, str(filename)])
        segment_counter += 1
    return logs


def split_silence(
    tempt_file: str,
    voice_file_path: Path,
    audio_total_duration: float,
    ) -> List[Tuple[float, float, str]]:
    
    audio = AudioSegment.from_file(str(voice_file_path))
    silence_thresh = audio.dBFS - 32
    min_silence_len = 700

    # Split audio silence
    segments = audio_segment_silence(
        audio,
        min_silence_len,
        silence_thresh,
    )

    # order segments by start time
    segments = sorted(segments, key=lambda x: x[0])
    
    # save segments
    segments_path = Path(tempt_file) / "segments"
    os.makedirs(segments_path, exist_ok=True)

    logs = write_audios(
        audio,
        segments,
        segments_path
    )
    
    # log start
    logs.insert(0, [0, logs[0][0], "start_segmenting"])
    # log finish
    logs.append([logs[-1][1], audio_total_duration, "finish_segmenting"])
    
    # Liberar memoria del objeto AudioSegment y recolectar basura
    del audio, segments, segments_path
    gc.collect()
    
    return logs