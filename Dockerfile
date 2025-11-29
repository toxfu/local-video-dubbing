# Usa PyTorch 2.8 con soporte GPU (CUDA 12.8)
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para algunas librerías Python
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de configuración del proyecto
COPY pyproject.toml .

# Instala uv para gestión de dependencias más rápida
RUN pip install --no-cache-dir uv

# Instala las dependencias del proyecto
RUN uv pip install --system -r pyproject.toml

# Copia el código fuente
COPY src/ ./src/

# Expone el puerto de Streamlit
EXPOSE 8501

# Agrega src al PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Comando para ejecutar la aplicación
CMD ["streamlit", "run", "src/gui.py", "--server.port=8501", "--server.address=0.0.0.0"]