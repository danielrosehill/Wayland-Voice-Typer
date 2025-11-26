# WhisperTux (AMD GPU Fork)

This is a fork of [WhisperTux](https://github.com/cjams/whispertux) - a simple voice dictation application for Linux, modified to support AMD GPU acceleration via Vulkan.

## Why This Fork?

The original WhisperTux only supports CPU-based transcription. This fork adds:

- **AMD GPU acceleration** via Vulkan backend for whisper.cpp
- **Custom finetune model support** for GGML-format models
- **Improved model discovery** scanning multiple directories for models

## Fork Modifications

### GPU Acceleration
- Configured to use an external Vulkan-accelerated `whisper-cli` binary
- Set `whisper_binary` in config to point to your Vulkan-built whisper.cpp
- Works with AMD GPUs (tested on RX 7700 XT) via Mesa RADV driver

### Model Support
- **Custom model directories**: Scans `~/ai/models/stt/` for models
- **Finetune discovery**: Finds GGML finetunes in `~/ai/models/stt/finetunes/v2/ggml/`
- **Flexible naming**: Supports both `ggml-model.bin` and custom naming like `daniel-fine-tune-*.bin`

### Other Changes
- Default keybinding changed to F13 (useful for macro keys)
- Reorganized directory structure (`app/` folder)
- Debian packaging support

## Installation

### Prerequisites

1. **Vulkan-enabled whisper.cpp** - Build whisper.cpp with Vulkan support:
   ```bash
   git clone https://github.com/ggerganov/whisper.cpp
   cd whisper.cpp
   mkdir build && cd build
   cmake .. -DGGML_VULKAN=ON
   make -j$(nproc)
   ```

2. **ydotool** - For text injection:
   ```bash
   sudo apt install ydotool
   systemctl --user enable --now ydotool
   ```

### From Debian Package

```bash
./build-deb.sh
sudo dpkg -i whispertux_1.0.0_all.deb
```

### From Source

```bash
cd app
./setup-venv.sh
python3 setup.py
```

## Configuration

Config file: `~/.config/whispertux/config.json`

Key settings:
```json
{
  "whisper_binary": "/path/to/vulkan/whisper-cli",
  "model": "[Finetune] base",
  "model_directories": [
    "/home/user/ai/models/stt/whisper-cpp",
    "/home/user/ai/models/stt/finetunes"
  ]
}
```

## Model Directories

The app scans these locations for models:
- `~/ai/models/stt/whisper-cpp/` - Standard whisper models
- `~/ai/models/stt/finetunes/v2/ggml/` - GGML format finetunes
- `~/ai/models/stt/finetunes/v2/acft/` - ACFT format finetunes

## Usage

1. Launch WhisperTux from your application menu
2. Press F13 (or configured shortcut) to start recording
3. Speak, then press again to stop
4. Transcribed text is typed into the focused application

## Original Project

- **Repository**: https://github.com/cjams/whispertux
- **Original docs**: [app/docs/](app/docs/)

## License

MIT License (see [LICENSE](LICENSE))
