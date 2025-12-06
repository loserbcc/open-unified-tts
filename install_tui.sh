#!/bin/bash
# Install TUI Client Dependencies for Open Unified TTS

set -e

echo "Installing TUI Client dependencies..."
echo ""

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "No virtual environment detected."
    echo "Recommended: Use the project's .venv"
    echo ""
    read -p "Continue with system-wide install? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        echo "To use venv: source .venv/bin/activate"
        exit 1
    fi
fi

# Install dependencies
if command -v uv &> /dev/null; then
    echo "Using uv for installation (faster)..."
    uv pip install -r requirements-tui.txt
else
    echo "Using pip for installation..."
    pip install -r requirements-tui.txt
fi

echo ""
echo "Installation complete!"
echo ""
echo "Usage:"
echo "  ./tui_client.py"
echo "  ./tui_client.py --api-url http://remote:8765"
echo "  ./tui_client.py --no-autoplay"
echo ""
echo "For help:"
echo "  ./tui_client.py --help"
echo ""
