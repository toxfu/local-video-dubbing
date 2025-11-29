import streamlit as st
import tempfile
import shutil
import os
import json


def main():
    with st.container():
        st.title('Spanish video dubbing')

    # Cargar un archivo de video
    uploaded_video = st.file_uploader(
        "Arrastra y suelta videos aquí o haz clic para seleccionarlos",
        # accept_multiple_files="directory",
        type=["mp4", "avi", "mkv", "mov", "webm", "webp"],
    )
    
    if uploaded_video is not None:
        with tempfile.TemporaryDirectory(delete=False) as tmp_dir:
            tmp_original_video_path = os.path.join(tmp_dir, uploaded_video.name)
            with open(tmp_original_video_path, "wb") as tmp_file:
                tmp_file.write(uploaded_video.read())
        # Guardar el archivo cargado en session_state si no está ya almacenado

        st.write(f"✅ Video cargado: {uploaded_video.name}")

        st.write(f"Dispositivo seleccionado: {DEVICE}")
            
        # Extraer audio y convertir a texto al hacer clic en un botón
        if st.button("Procesar video"):
            st.write("Extrayendo audio...")
            # Extraer audio y video
            audio_file, video_file = extract_audio_video(tmp_original_video_path)
            st.audio(audio_file, format='audio/wav')
            st.write(f"Audio extraído: {audio_file}")
            # Separate voice and background
            st.write("Separando voz y fondo...")
            voice_file_path, background_file, total_video_duration = voice_background(
                tmp_dir,
                audio_file
            )
            # Cortando los silencios
            st.write(f"Cortando silencios...")
            logs= split_silence(tmp_dir, voice_file_path, total_video_duration)
            # speech recognition
            st.write("Convirtiendo audio a texto...")
            texts = speech_recognition(logs)
            # download texts
            st.write("Descargando textos...")
            st.download_button(
                label="Descargar logs como JSON",
                data=json.dumps(logs, ensure_ascii=False, indent=2),
                file_name="logs.json",
                mime="application/json",
                on_click= "ignore"
            )
            st.download_button(
                label="Descargar text como JSON",
                data=json.dumps(texts, ensure_ascii=False, indent=2),
                file_name="texts.json",
                mime="application/json",
                on_click= "ignore"
            )
            # Translate
            st.write("Traduciendo...")
            translated_texts, audio_durations, translate_segments_path = translate(tmp_dir, texts)
            st.download_button(
                label="Descargar text translation como JSON",
                data=json.dumps(translated_texts, ensure_ascii=False, indent=2),
                file_name="translate_texts.json",
                mime="application/json",
                on_click= "ignore"
            )
            # join audio segments
            st.write("Unificando segmentos de audio...")
            joined_audio = join_audios(translate_segments_path, audio_durations, logs)
            # Combinar audio y video
            st.write("Combinando audio y video...")
            output_file, output_file_name = combine_audio_and_video(video_file, joined_audio, background_file, tmp_original_video_path)

            # Abrir el archivo en modo binario
            with open(output_file, "rb") as f:
                contenido = f.read()

            # Crear el botón de descarga
            st.download_button(
                label="Descargar video traducido",
                data=contenido,
                file_name= output_file_name,
                mime="video/webm",  # Tipo MIME apropiado
                on_click= "ignore"
            )
            
        # clean up
        if st.button("Clean and Restart App"):
            shutil.rmtree(tmp_dir)
            st.cache_data.clear()  # Limpia la memoria caché de Streamlit
            st.cache_resource.clear()  # Limpia recursos en caché
            st.rerun()  # Reinicia la aplicación
            
            
if __name__ == '__main__':
    st.set_page_config(
        page_title='Spanish video dubbing',
        page_icon='📹'
    )
    from tools.speech_recognition import speech_recognition
    from tools.voice_background import voice_background
    from tools.extract_audio_video import extract_audio_video
    from tools.translate import translate
    from tools.combining import combine_audio_and_video
    from tools.split_silence import split_silence
    from tools.join_audios import join_audios
    from resources import DEVICE
    main()