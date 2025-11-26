# Diagnose Wayland Voice Typer Issues

Run diagnostic checks to identify issues with the application setup.

## Instructions

Run the following diagnostic checks and report results:

### 1. Check Python Environment
```bash
cd /home/daniel/programs/speech-voice/apps/forks/whispertux
python3 --version
ls -la .venv/ app/.venv/ 2>/dev/null
```

### 2. Check Dependencies
```bash
source .venv/bin/activate 2>/dev/null || source app/.venv/bin/activate
pip list | grep -E "PySide6|sounddevice|evdev|numpy|scipy"
```

### 3. Check Audio System
```bash
pactl info 2>&1 | head -10
pactl list sources short
```

### 4. Check ydotool
```bash
systemctl --user status ydotool
which ydotool
```

### 5. Check Input Device Access
```bash
ls -la /dev/input/event* | head -5
groups | grep -o input
```

### 6. Check Whisper Binary
```bash
cat ~/.config/whispertux/config.json 2>/dev/null | grep whisper_binary
# Test the binary if path found
```

### 7. Check Models
```bash
ls -la ~/ai/models/stt/whisper-cpp/ 2>/dev/null
ls -la ~/ai/models/stt/finetunes/ 2>/dev/null
```

Report findings with:
- What's working correctly
- What issues were found
- Recommended fixes for each issue
