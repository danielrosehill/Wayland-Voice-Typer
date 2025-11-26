# Build Wayland Voice Typer

Build the application for distribution.

## Instructions

1. First, ensure the virtual environment is set up and dependencies are installed:
   ```bash
   cd app
   source .venv/bin/activate || python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the Debian package build script:
   ```bash
   ./build-deb.sh
   ```

3. Verify the build output:
   - Check that `whispertux_1.0.0_all.deb` was created
   - Test installation if requested: `sudo dpkg -i whispertux_1.0.0_all.deb`

4. Report the build results to the user, including:
   - Package file size
   - Any warnings or errors during build
   - Installation instructions if relevant
