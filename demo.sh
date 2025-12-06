#!/bin/bash
# Open Unified TTS Demo Script
# Run this in a terminal while recording with OBS

# Use MOYA_IP env var or default to localhost (set MOYA_IP=192.168.4.44 when running from Tayln)
MOYA_IP="${MOYA_IP:-localhost}"
API="http://${MOYA_IP}:8765/v1/audio/speech"
DEMO_DIR="/tmp/tts-demo"
mkdir -p "$DEMO_DIR"

# Colors for terminal
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

pause() {
    sleep "${1:-2}"
}

show_command() {
    echo -e "${CYAN}$1${NC}"
}

section() {
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    pause 1
}

# Generate and play with status
generate_and_play() {
    local voice="$1"
    local text="$2"
    local outfile="$DEMO_DIR/${voice}_$(date +%s).mp3"

    echo -e "${MAGENTA}[Generating: voice=${voice}]${NC}"

    local start_time=$(date +%s.%N)
    curl -s -X POST "$API" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"tts-1\",\"voice\":\"${voice}\",\"input\":\"${text}\"}" \
        --output "$outfile"
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)

    local filesize=$(du -h "$outfile" 2>/dev/null | cut -f1)
    echo -e "${MAGENTA}[Generated: ${filesize} in ${duration}s]${NC}"
    echo -e "${MAGENTA}[Playing...]${NC}"

    # Use afplay on Mac, mpv on Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        afplay "$outfile"
    else
        mpv --really-quiet "$outfile"
    fi

    echo -e "${MAGENTA}[Done]${NC}"
    pause 1
}

clear
echo ""
echo "    ╔═══════════════════════════════════════════════════════════╗"
echo "    ║           OPEN UNIFIED TTS - LIVE DEMO                    ║"
echo "    ║     One API • Multiple Backends • Unlimited Length        ║"
echo "    ╚═══════════════════════════════════════════════════════════╝"
echo ""
pause 3

# ============ MOVIEGUY INTRO ============
section "1. Epic Movie Trailer Intro (VoxCPM Clone: MovieGuy)"

show_command 'curl -X POST http://localhost:8765/v1/audio/speech \'
show_command '  -d {"model":"tts-1", "voice":"movieguy", "input":"..."}'
echo ""
echo -e "${NC}\"In a world... where dozens of TTS backends speak different languages..."
echo "where developers struggle to unite them all..."
echo "one API rises above the chaos..."
echo -e "to bring order to the voice universe.\"${NC}"
echo ""
generate_and_play "movieguy" "In a world... where dozens of TTS backends speak different languages... where developers struggle to unite them all... one API rises above the chaos... to bring order to the voice universe."
pause 2

# ============ DAVID ATTENBOROUGH - THE PROBLEM ============
section "2. The Problem (VoxCPM Clone: David Attenborough)"

show_command 'curl -X POST http://localhost:8765/v1/audio/speech \'
show_command '  -d {"model":"tts-1", "voice":"davidat", "input":"..."}'
echo ""
echo -e "${NC}\"Here we observe the curious landscape of text-to-speech systems."
echo "Dozens of backends, each speaking a completely different language."
echo "VoxCPM communicates through Gradio. Kyutai prefers WebSockets."
echo "ElevenLabs insists on REST. And the developer, poor creature,"
echo -e "must learn them all. A remarkable challenge indeed.\"${NC}"
echo ""
generate_and_play "davidat" "Here we observe the curious landscape of text-to-speech systems. Dozens of backends, each speaking a completely different language. VoxCPM communicates through Gradio. Kyutai prefers WebSockets. ElevenLabs insists on REST. And the developer, poor creature, must learn them all. A remarkable challenge indeed."
pause 1

# ============ CONFUSED - RELATABLE ============
section "3. The Frustration (Kyutai Emotion: Confused)"

show_command 'curl -X POST http://localhost:8765/v1/audio/speech \'
show_command '  -d {"model":"tts-1", "voice":"confused", "input":"..."}'
echo ""
echo -e "${NC}\"Wait, hold on. Let me get this straight."
echo "So every time I want to use a different voice, I have to completely rewrite my code?"
echo "And if I want to switch from ElevenLabs to a local model, I need different authentication,"
echo "different request formats, different response handling?"
echo "What about long paragraphs? Most of these models just... stop working after a hundred words."
echo "They clip the audio, or the quality degrades, or you get weird artifacts."
echo -e "This doesn't make any sense. There has to be a better way to do this.\"${NC}"
echo ""
generate_and_play "confused" "Wait, hold on. Let me get this straight. So every time I want to use a different voice, I have to completely rewrite my code? And if I want to switch from ElevenLabs to a local model, I need different authentication, different request formats, different response handling? What about long paragraphs? Most of these models just... stop working after a hundred words. They clip the audio, or the quality degrades, or you get weird artifacts. This doesn't make any sense. There has to be a better way to do this."
pause 1

# ============ GLADOS - THE SOLUTION ============
section "4. The Solution (VoxCPM Clone: GLaDOS)"

show_command 'curl -X POST http://localhost:8765/v1/audio/speech \'
show_command '  -d {"model":"tts-1", "voice":"glados", "input":"..."}'
echo ""
echo -e "${NC}\"Oh, how delightful. You've finally discovered the obvious solution."
echo "Open Unified TTS. One API endpoint. All backends unified."
echo "Even a human could understand it."
echo -e "I'm almost impressed. Almost.\"${NC}"
echo ""
generate_and_play "glados" "Oh, how delightful. You've finally discovered the obvious solution. Open Unified TTS. One API endpoint. All backends unified. Even a human could understand it. I'm almost impressed. Almost."
pause 1

# ============ CALM - WISDOM ============
section "5. The Clarity (Kyutai Emotion: Calm)"

show_command 'curl -X POST http://localhost:8765/v1/audio/speech \'
show_command '  -d {"model":"tts-1", "voice":"calm", "input":"..."}'
echo ""
echo -e "${NC}\"Now the API is unified. You don't need to care about backends anymore."
echo "Write once, speak everywhere. VoxCPM, Kyutai, ElevenLabs..."
echo "it doesn't matter which one you choose. The same code works for all of them."
echo "Long text? The system handles it. It chunks intelligently."
echo "Stitches seamlessly. Your application just works."
echo -e "This is how it should have been from the start.\"${NC}"
echo ""
generate_and_play "calm" "Now the API is unified. You don't need to care about backends anymore. Write once, speak everywhere. VoxCPM, Kyutai, ElevenLabs... it doesn't matter which one you choose. The same code works for all of them. Long text? The system handles it. It chunks intelligently. Stitches seamlessly. Your application just works. This is how it should have been from the start."
pause 1

# ============ HAPPY - EXCITEMENT ============
section "6. The Benefits (Kyutai Emotion: Happy)"

show_command 'curl -X POST http://localhost:8765/v1/audio/speech \'
show_command '  -d {"model":"tts-1", "voice":"happy", "input":"..."}'
echo ""
echo -e "${NC}\"Oh my gosh, this is amazing! It handles long text automatically!"
echo "You can write an entire book chapter and it just works!"
echo "The system intelligently splits your text at natural sentence boundaries,"
echo "generates each chunk within the model's sweet spot,"
echo "then stitches everything together with smooth crossfades."
echo "No more weird audio artifacts! No more quality drops halfway through!"
echo "No more clicking sounds between segments!"
echo -e "This is exactly what I've been looking for!\"${NC}"
echo ""
generate_and_play "happy" "Oh my gosh, this is amazing! It handles long text automatically! You can write an entire book chapter and it just works! The system intelligently splits your text at natural sentence boundaries, generates each chunk within the model's sweet spot, then stitches everything together with smooth crossfades. No more weird audio artifacts! No more quality drops halfway through! No more clicking sounds between segments! This is exactly what I've been looking for!"
pause 1

# ============ GLADOS - WRAP UP ============
section "7. Final Summary (VoxCPM Clone: GLaDOS)"

show_command 'curl -X POST http://localhost:8765/v1/audio/speech \'
show_command '  -d {"model":"tts-1", "voice":"glados", "input":"..."}'
echo ""
echo -e "${NC}\"Well. Look at you. You actually made it to the end."
echo "Smart chunking. Seamless stitching. Multi-backend routing."
echo "Open source. Apache licensed."
echo -e "I suppose even you can use it. Good luck with that.\"${NC}"
echo ""
generate_and_play "glados" "Well. Look at you. You actually made it to the end. Smart chunking. Seamless stitching. Multi-backend routing. Open source. Apache licensed. I suppose even you can use it. Good luck with that."
pause 2

# ============ END CARD ============
echo ""
echo ""
echo "    ╔═══════════════════════════════════════════════════════════╗"
echo "    ║                                                           ║"
echo "    ║       github.com/loserbcc/open-unified-tts                ║"
echo "    ║                                                           ║"
echo "    ║              Apache 2.0 License                           ║"
echo "    ║                                                           ║"
echo "    ╚═══════════════════════════════════════════════════════════╝"
echo ""
pause 5

echo "Demo complete!"
