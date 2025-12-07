#!/bin/bash
# Vietnamese TTS Docker Setup for Open Unified TTS
# Tested on: Mac M1/M2/M3/M4, should work on Linux x86_64

set -e

echo "🇻🇳 Vietnamese TTS Setup"
echo "========================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop first."
    echo "   https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo -e "\033[0;32m✓ Docker found\033[0m"

# Check Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi
echo -e "\033[0;32m✓ Docker is running\033[0m"
echo ""

# Build VieNeu-TTS container
echo "📦 Building VieNeu-TTS (Vietnamese TTS engine)..."
echo "   This may take 5-10 minutes on first run..."
docker build -t vieneu-tts:latest ./docker/vieneu
echo -e "\033[0;32m✓ VieNeu-TTS built\033[0m"

# Build proxy container
echo "📦 Building Open Unified TTS proxy..."
docker build -t open-unified-tts:latest .
echo -e "\033[0;32m✓ Proxy built\033[0m"

# Create network if needed
echo ""
echo "🔗 Creating Docker network..."
docker network create tts-network 2>/dev/null || true

# Stop and remove old containers
echo "🧹 Cleaning up old containers..."
docker stop vieneu-tts unified-tts-proxy 2>/dev/null || true
docker rm vieneu-tts unified-tts-proxy 2>/dev/null || true

# Start VieNeu-TTS
echo "🚀 Starting VieNeu-TTS..."
echo "   First run will download ~2GB of models - be patient!"
docker run -d \
    --name vieneu-tts \
    --network tts-network \
    -p 7860:7860 \
    vieneu-tts:latest

# Wait for VieNeu-TTS to be ready
echo "⏳ Waiting for VieNeu-TTS to start (this takes 1-2 minutes)..."
for i in {1..60}; do
    if curl -s http://localhost:7860/ > /dev/null 2>&1; then
        echo -e "\033[0;32m✓ VieNeu-TTS is ready\033[0m"
        break
    fi
    echo "   Still loading... ($i/60)"
    sleep 5
done

# Check if VieNeu started
if ! curl -s http://localhost:7860/ > /dev/null 2>&1; then
    echo "❌ VieNeu-TTS failed to start. Check logs with: docker logs vieneu-tts"
    exit 1
fi

# Start proxy
echo "🚀 Starting unified-tts-proxy..."
docker run -d \
    --name unified-tts-proxy \
    --network tts-network \
    -p 8765:8765 \
    -e VIENEU_HOST=vieneu-tts \
    -e VIENEU_PORT=7860 \
    open-unified-tts:latest

sleep 3

# Test
echo ""
echo "🔍 Testing API..."
if curl -s http://localhost:8765/health | grep -q "ok"; then
    echo -e "\033[0;32m✓ API is healthy\033[0m"
else
    echo "⚠️  API health check failed, but it might still work"
fi

# Test Vietnamese TTS
echo ""
echo "🎤 Testing Vietnamese TTS..."
RESPONSE=$(curl -s -X POST http://localhost:8765/v1/audio/speech \
    -H "Content-Type: application/json" \
    -d '{"input":"Xin chào","voice":"huong"}' \
    -o test_vietnamese.wav -w "%{size_download}")

if [ "$RESPONSE" -gt 1000 ]; then
    echo -e "\033[0;32m✓ Vietnamese TTS working! Generated $RESPONSE bytes\033[0m"
    echo "   Audio saved to: test_vietnamese.wav"
else
    echo "⚠️  TTS test returned small file ($RESPONSE bytes)"
    echo "   Check: docker logs vieneu-tts"
fi

echo ""
echo "========================================"
echo -e "\033[0;32m🎉 Setup Complete!\033[0m"
echo "========================================"
echo ""
echo "API Endpoint: http://localhost:8765/v1/audio/speech"
echo ""
echo "Example usage:"
echo "  curl -X POST http://localhost:8765/v1/audio/speech \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"input\":\"Xin chào\",\"voice\":\"huong\"}' \\"
echo "    -o output.wav"
echo ""
echo "Available Vietnamese voices:"
echo "  - huong (female, Northern)"
echo "  - tuyen (male, Northern)"
echo "  - doan (female, Southern)"
echo "  - vinh (male, Southern)"
echo ""
echo "Commands:"
echo "  Stop:    docker stop vieneu-tts unified-tts-proxy"
echo "  Start:   docker start vieneu-tts unified-tts-proxy"
echo "  Logs:    docker logs unified-tts-proxy"
echo "  Remove:  docker rm -f vieneu-tts unified-tts-proxy"
