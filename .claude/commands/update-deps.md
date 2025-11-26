# Update Dependencies

Update Python dependencies to latest compatible versions.

## Instructions

1. Activate the virtual environment:
   ```bash
   cd /home/daniel/programs/speech-voice/apps/forks/whispertux
   source .venv/bin/activate 2>/dev/null || source app/.venv/bin/activate
   ```

2. Update pip first:
   ```bash
   pip install --upgrade pip
   ```

3. Update all dependencies:
   ```bash
   pip install --upgrade -r app/requirements.txt
   ```

4. Check for any compatibility issues:
   ```bash
   pip check
   ```

5. Test the application launches correctly:
   ```bash
   python app/main.py --help 2>&1 || python app/main.py &
   sleep 3
   pkill -f "python.*main.py" 2>/dev/null
   ```

6. Report:
   - Which packages were updated
   - Any compatibility warnings
   - Whether the app still starts correctly
