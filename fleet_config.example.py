"""Example fleet configuration - copy to fleet_config.py and customize.

This file defines your local network's TTS server locations.
The adapters will auto-discover services across these hosts.
"""

# VoxCPM 1.5 hosts (priority order) - voice cloning
VOXCPM15_HOSTS = [
    "http://localhost:7870",
    # "http://gpu-server:7870",
]

# VibeVoice hosts (priority order) - streaming TTS
VIBEVOICE_HOSTS = [
    "http://localhost:8086",
    # "http://gpu-server:8086",
]

# Higgs Audio hosts (priority order) - generative voices
HIGGS_HOSTS = [
    "http://localhost:8085",
    # "http://gpu-server:8085",
]

# Kyutai/Moshi hosts (priority order) - emotional TTS
KYUTAI_HOSTS = [
    {"name": "local", "url": "http://localhost:8087"},
    # {"name": "gpu-server", "url": "http://gpu-server:8087"},
]

# Maya1 hosts (priority order) - CPU emotional TTS
MAYA1_HOSTS = [
    {"name": "local", "url": "http://localhost:8090"},
    # {"name": "cpu-server", "url": "http://cpu-server:8090"},
]
