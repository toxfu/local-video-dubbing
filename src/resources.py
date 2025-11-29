from kokoro import KPipeline
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import streamlit as st

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@st.cache_resource
def load_base_resources():
    voice_separator = torch.hub.load('sigsep/open-unmix-pytorch', 'umxl').to(DEVICE)
    # transcription model
    model_id = "distil-whisper/distil-large-v3.5"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, dtype=torch.float16, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(DEVICE)

    processor = AutoProcessor.from_pretrained(model_id)
    return {
        "voice_separator": voice_separator,
        "transcriber": pipeline(
            task="automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            dtype=torch.float16,
            device=DEVICE,
            return_timestamps=True,
        ),
        "translation": pipeline(
            task="translation",
            model="facebook/nllb-200-distilled-600M",
            src_lang="eng_Latn",
            tgt_lang="spa_Latn",
            dtype=torch.float16,
            device=DEVICE
        ),
        "voice_pipeline": KPipeline(lang_code='e', device=DEVICE)
    }

_resources = load_base_resources()

# Sidebar resources
VOICE_SEPARATOR = _resources["voice_separator"]
TRANSCRIBER = _resources["transcriber"]
TRANSLATION = _resources["translation"]
VOICE_PIPELINE = _resources["voice_pipeline"]
SR = 25_000