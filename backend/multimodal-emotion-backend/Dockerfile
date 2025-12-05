# =============================
#   Multimodal Emotion Backend
#   Hugging Face Spaces (Docker)
# =============================

FROM python:3.10-slim

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && \
    apt-get install -y ffmpeg git-lfs build-essential && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------
# Work directory setup
# -----------------------------
WORKDIR /app

# -----------------------------
# Install Python dependencies first (layer caching)
# -----------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# Copy project files
# -----------------------------
COPY . /app

# -----------------------------
# Environment setup
# -----------------------------
ENV PYTHONUNBUFFERED=1
# Hugging Face Spaces sets $PORT automatically (usually 7860)
ENV PORT=7860
# Optional: HF Hub model repo env var (set via Space Secrets)
ENV HF_MODEL_REPO="your-username/best-multimodal-model"

# -----------------------------
# Startup log info
# -----------------------------
RUN echo "🎬 Docker image for Multimodal Emotion Backend built successfully!"

# -----------------------------
# Expose and Run
# -----------------------------
EXPOSE ${PORT}
CMD ["bash", "-lc", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
