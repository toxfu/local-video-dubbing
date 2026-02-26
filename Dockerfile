# Imagen oficial de PyTorch
FROM pytorch/pytorch:2.8.0-cuda12.8-cudnn9-runtime

WORKDIR /app

# 1. Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 2. Instalar uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Instalar dependencias de Python
# Copiamos solo lo necesario para instalar primero (mejor cache)
COPY pyproject.toml . 
# Si tienes un lockfile, inclúyelo: COPY uv.lock . 

# Instalamos en el Python del sistema de la imagen
RUN uv pip install --system .

# 4. Copiar código fuente
COPY src/ ./src/

# Variables de entorno para Streamlit
ENV PYTHONPATH="/app/src" \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Simplificamos el comando ya que usamos variables de entorno
CMD ["streamlit", "run", "src/gui.py"]