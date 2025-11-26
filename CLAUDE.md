# Wayland Voice Typer - Claude Code Instructions

## Project Overview

Wayland Voice Typer is a voice dictation application for Linux, specifically designed for Wayland desktop environments. It's a fork of [WhisperTux](https://github.com/cjams/whispertux) with AMD GPU acceleration support via Vulkan.

**Repository**: https://github.com/danielrosehill/Wayland-Voice-Typer
**Upstream**: https://github.com/cjams/whispertux

## Tech Stack

- **Python 3.12+** with PySide6 GUI framework
- **whisper.cpp** for transcription (Vulkan-accelerated)
- **ydotool** for text injection on Wayland
- **evdev** for global keyboard shortcuts
- **PipeWire/PulseAudio** for audio capture

## Project Structure

```
.
├── app/                    # Main application code
│   ├── main.py            # Entry point and GUI
│   ├── src/               # Source modules
│   │   ├── audio_capture.py
│   │   ├── config_manager.py
│   │   ├── global_shortcuts.py
│   │   ├── text_injector.py
│   │   ├── whisper_manager.py
│   │   ├── benchmark.py
│   │   └── ...
│   ├── scripts/           # Setup and helper scripts
│   ├── docs/              # Documentation
│   └── assets/            # Icons and images
├── build-deb.sh           # Debian package builder
├── run.sh                 # Quick launcher script
├── install.sh             # Installation script
└── update.sh              # Update script
```

## Development Environment

### Virtual Environment

The project uses a Python virtual environment at `.venv/`. When working with this project:

```bash
# Activate venv
source .venv/bin/activate

# Or run directly
./run.sh
```

### Dependencies

Install with:
```bash
cd app
pip install -r requirements.txt
```

Key dependencies:
- PySide6 (Qt GUI)
- sounddevice (audio capture)
- evdev (keyboard shortcuts)
- numpy/scipy (audio processing)

## Configuration

User config is stored at: `~/.config/whispertux/config.json`

Key settings:
- `whisper_binary`: Path to Vulkan-enabled whisper-cli
- `model`: Active Whisper model name
- `primary_shortcut`: Global hotkey (default: F13)
- `key_delay`: Milliseconds between keystrokes for typing
- `model_directories`: Where to scan for models

## Common Tasks

### Running the App

```bash
./run.sh
# or
cd app && source .venv/bin/activate && python main.py
```

### Building the Deb Package

```bash
./build-deb.sh
# Creates whispertux_1.0.0_all.deb
```

### Rebuilding After Changes

After modifying Python code:
1. Test directly with `python app/main.py`
2. For distribution, rebuild deb: `./build-deb.sh`

### Adding New Models

Models should be placed in:
- `~/ai/models/stt/whisper-cpp/` - Standard models
- `~/ai/models/stt/finetunes/` - Custom finetunes

## Architecture Notes

### Audio Pipeline

1. `AudioCapture` captures from PipeWire/PulseAudio via sounddevice
2. Audio saved to temp WAV file
3. `WhisperManager` calls external whisper-cli binary
4. Transcription returned to GUI

### Text Injection

Uses ydotool for Wayland-compatible text injection:
- ydotool daemon must be running
- Configurable key delay for compatibility

### Global Shortcuts

Uses evdev to capture keyboard events system-wide:
- Requires `/dev/input/` access
- User may need to be in `input` group

## Troubleshooting

### Audio Issues
- Check PipeWire: `pactl info`
- List sources: `pactl list sources short`

### Keyboard Shortcut Issues
- Check evdev access to `/dev/input/`
- Add user to input group if needed

### Text Injection Issues
- Verify ydotool daemon: `systemctl --user status ydotool`

## Related Files

- Models: `~/ai/models/stt/`
- Config: `~/.config/whispertux/`
- Temp audio: `~/.local/share/whispertux/temp/`
