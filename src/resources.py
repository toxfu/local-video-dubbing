from kokoro import KPipeline
import torch
from transformers import AutoModelForSpeechSeq2Seq,\
    AutoModelForSeq2SeqLM, AutoTokenizer,AutoProcessor, pipeline
import streamlit as st

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@st.cache_resource
def load_base_resources():
    voice_separator = torch.hub.load('sigsep/open-unmix-pytorch', 'umxl').to(DEVICE)
    # transcription model
    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, dtype=torch.float16, low_cpu_mem_usage=True, use_safetensors=True
    ).to(DEVICE)

    processor = AutoProcessor.from_pretrained(model_id)
    
    # translation model
    trans_model_id = "facebook/nllb-200-distilled-600M"
    trans_tokenizer = AutoTokenizer.from_pretrained(trans_model_id)
    trans_model = AutoModelForSeq2SeqLM.from_pretrained(trans_model_id, dtype=torch.float16).to(DEVICE)
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
        "translation_model": trans_model,
        "translation_tokenizer": trans_tokenizer,
        "voice_pipeline": KPipeline(lang_code='e', device=DEVICE)
    }

_resources = load_base_resources()

# Sidebar resources
VOICE_SEPARATOR = _resources["voice_separator"]
TRANSCRIBER = _resources["transcriber"]
TRANSLATION_MODEL = _resources["translation_model"]
TRANSLATION_TOKENIZER = _resources["translation_tokenizer"]
VOICE_PIPELINE = _resources["voice_pipeline"]
SR = 25_000

VIDEO_CODEC_PARAMS = {
    'webm': ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0"],
    'mp4': ["-c:v", "libx264", "-crf", "23", "-preset", "medium"],
    'avi': ["-c:v", "mpeg4", "-qscale:v", "5"],
    'mkv': ["-c:v", "libx264", "-crf", "23", "-preset", "medium"],
    'mov': ["-c:v", "libx264", "-crf", "23", "-preset", "medium"],
    'webp': ["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0"],
}

LIST_FORMATS = list(VIDEO_CODEC_PARAMS.keys())

TARGET_LANGUAGES = {
    "Spanish": ["spa_Latn", "ef_dora", "em_alex"],
    "English": ["eng_Latn", "af_heart", "am_fenrir"],
    "Italian": ["ita_Latn", "if_sara", "im_nicola"],
    "Portuguese": ["por_Latn", "pf_dora", "pm_alex"],
    "Japanese": ["jpn_Jpan", "jf_nezumi", "jm_kumo"],
}

TARGET_LANGUAGES_LIST = list(TARGET_LANGUAGES.keys())