# 🎬 Local Video Dubbing

Sistema automatizado de doblaje de videos usando IA que traduce y sincroniza el audio de videos. Sólo acepta un locutor por video.

| Video Original | Video Doblado |
|----------------|---------------|
| <video src="https://github.com/user-attachments/assets/e51a4941-af2e-4135-9cde-4124a381eacd"> | <video src="https://github.com/user-attachments/assets/1460799a-a5c7-4c5f-8563-9bdc9368fa1e"> |



## 📦 Instalación

### Requisitos previos

- Python 3.12
- FFmpeg instalado en el sistema
- GPU compatible con CUDA (recomendado) o CPU

### Con UV (recomendado)

```bash
# Instalar uv si no lo tienes
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clonar el repositorio
git clone <tu-repo-url>
cd local-video-dubbing

# Instalar dependencias
uv sync
```

### Con Docker

```bash
# Construir la imagen
docker compose build

# Ejecutar el contenedor
docker compose up
```

## 🔩 Ajustes opcionales

Si necesitas subir archivos más grandes, ajusta los siguientes parámetros en `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 1024  # en megas → 1 GB
```

## 💻 Uso

### Interfaz gráfica (Streamlit)

```bash
# Activar entorno virtual si es necesario
source .venv/bin/activate

# Ejecutar la aplicación
streamlit run src/gui.py
```

Luego abre tu navegador en `http://localhost:8501` y:

1. Arrastra o selecciona un video
2. Haz clic en "Procesar video"
3. Espera a que se complete el procesamiento
4. Descarga el video doblado

## ⚙️ Modelos utilizados

- **Separación de audio**: `sigsep/open-unmix-pytorch` (umxl)
- **Transcripción**: `distil-whisper/distil-large-v3.5`
- **Traducción**: `facebook/nllb-200-distilled-600M`
- **Síntesis de voz**: Kokoro TTS (múltiples voces disponibles)

## 🎯 Casos de uso

- Doblaje de contenido educativo
- Traducción de tutoriales en video
- Localización de presentaciones

## 📝 Licencia

Este proyecto está bajo la licencia especificada en el archivo `LICENCE`.

## 📧 Contacto

Para preguntas, sugerencias o reportar problemas, por favor abre un issue en GitHub.