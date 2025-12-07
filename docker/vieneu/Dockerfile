# VieNeu-TTS - Vietnamese Text-to-Speech
# Works on Mac (ARM64) and Linux (x86_64) - CPU mode
FROM python:3.11-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    espeak-ng \
    libespeak-ng1 \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set espeak library path (works for both ARM64 and x86_64)
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "aarch64" ]; then \
        echo "PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1" >> /etc/environment; \
    else \
        echo "PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1" >> /etc/environment; \
    fi
ENV PHONEMIZER_ESPEAK_LIBRARY=/usr/lib/aarch64-linux-gnu/libespeak-ng.so.1

# Clone VieNeu-TTS
RUN git clone --depth 1 https://github.com/pnnbao97/VieNeu-TTS.git .

# Patch for ARM64 support - add aarch64 library path to search patterns
RUN sed -i 's|"/usr/lib/x86_64-linux-gnu/libespeak-ng.so\*",|"/usr/lib/x86_64-linux-gnu/libespeak-ng.so*",\n        "/usr/lib/aarch64-linux-gnu/libespeak-ng.so*",|' /app/utils/phonemize_text.py

# Patch for Gradio 4.x compatibility - replace Ocean theme with Base
RUN sed -i 's/gr.themes.Ocean/gr.themes.Base/' /app/gradio_app.py

# Patch server binding to listen on all interfaces (for Docker)
RUN sed -i 's/server_name="127.0.0.1"/server_name="0.0.0.0"/' /app/gradio_app.py

# Patch share=True to bypass localhost accessibility check in Docker
RUN sed -i 's/share=False/share=True/' /app/gradio_app.py

# Install CPU-only PyTorch first (separate index)
RUN pip install --no-cache-dir \
    torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other Python dependencies from PyPI
# Pin gradio to 4.x for neucodec compatibility
RUN pip install --no-cache-dir \
    phonemizer>=3.3.0 \
    "gradio>=4.0.0,<5.0.0" \
    neucodec>=0.0.4 \
    librosa>=0.11.0 \
    huggingface_hub

# Expose Gradio port
EXPOSE 7860

# Set Gradio to listen on all interfaces
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=5 \
    CMD curl -f http://localhost:7860/ || exit 1

# Run Gradio app
CMD ["python", "gradio_app.py"]
