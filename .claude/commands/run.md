# Run Wayland Voice Typer

Launch the application for testing.

## Instructions

1. Check if the virtual environment exists and activate it:
   ```bash
   cd /home/daniel/programs/speech-voice/apps/forks/whispertux
   source .venv/bin/activate 2>/dev/null || source app/.venv/bin/activate 2>/dev/null
   ```

2. Launch the application:
   ```bash
   ./run.sh
   ```

   Or directly:
   ```bash
   python app/main.py
   ```

3. The app should launch in a window. Report any startup errors to the user.

Note: The app requires:
- ydotool daemon running for text injection
- Access to /dev/input/ for global shortcuts
- PipeWire/PulseAudio for audio capture
