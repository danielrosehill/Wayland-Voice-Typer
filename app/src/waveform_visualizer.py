"""
Simple audio level meter for WhisperTux
Displays a horizontal bar showing the current audio level
"""

import tkinter as tk
import threading
from typing import Optional


class WaveformVisualizer(tk.Frame):
    """Simple horizontal audio level meter widget for tkinter"""

    def __init__(self, parent, width=400, height=120, **kwargs):
        super().__init__(parent, **kwargs)

        # Widget dimensions
        self.width = width
        self.height = 40  # Simpler, smaller height

        # Audio state
        self.current_level = 0.0
        self.peak_level = 0.0
        self.recording_state = False
        self.is_active = False

        # Visual configuration
        self.background_color = "#2b2b2b"
        self.meter_bg_color = "#1a1a1a"
        self.level_color_low = "#2d7d46"      # Green for low levels
        self.level_color_mid = "#d4a82f"      # Yellow for mid levels
        self.level_color_high = "#c42b1c"     # Red for high levels
        self.inactive_color = "#404040"

        # Threading
        self.lock = threading.Lock()

        # Create the canvas
        self._create_canvas()

        # Bind resize events
        self.bind('<Configure>', self._on_resize)

    def _create_canvas(self):
        """Create the simple level meter canvas"""
        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg=self.background_color,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Draw initial state
        self._draw_meter()

    def _draw_meter(self):
        """Draw the level meter"""
        self.canvas.delete("all")

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width() or self.width
        canvas_height = self.canvas.winfo_height() or self.height

        # Meter bar dimensions with padding
        padding = 10
        meter_height = 20
        meter_y = (canvas_height - meter_height) // 2
        meter_width = canvas_width - (padding * 2)

        # Draw background bar
        self.canvas.create_rectangle(
            padding, meter_y,
            padding + meter_width, meter_y + meter_height,
            fill=self.meter_bg_color,
            outline="#3a3a3a",
            width=1
        )

        # Calculate level width
        level_width = int(meter_width * min(1.0, self.current_level))

        if level_width > 0 and self.recording_state:
            # Determine color based on level
            if self.current_level < 0.5:
                color = self.level_color_low
            elif self.current_level < 0.8:
                color = self.level_color_mid
            else:
                color = self.level_color_high

            # Draw level bar
            self.canvas.create_rectangle(
                padding + 1, meter_y + 1,
                padding + level_width - 1, meter_y + meter_height - 1,
                fill=color,
                outline=""
            )
        elif not self.recording_state:
            # Draw inactive state - subtle gradient
            self.canvas.create_rectangle(
                padding + 1, meter_y + 1,
                padding + 5, meter_y + meter_height - 1,
                fill=self.inactive_color,
                outline=""
            )

        # Draw level markers (25%, 50%, 75%)
        for pct in [0.25, 0.5, 0.75]:
            x = padding + int(meter_width * pct)
            self.canvas.create_line(
                x, meter_y,
                x, meter_y + meter_height,
                fill="#555555",
                width=1
            )

    def _on_resize(self, event):
        """Handle widget resize events"""
        if event.widget == self:
            self.width = event.width - 10
            self.height = event.height - 10
            self._draw_meter()

    def update_audio_data(self, amplitude: float):
        """Update with new audio amplitude data

        Args:
            amplitude: Audio amplitude level (0.0 to 1.0)
        """
        with self.lock:
            if self.recording_state:
                # Smooth the level slightly
                self.current_level = 0.7 * self.current_level + 0.3 * min(1.0, amplitude)

                # Track peak
                if amplitude > self.peak_level:
                    self.peak_level = amplitude
            else:
                # Decay when not recording
                self.current_level = self.current_level * 0.9

        # Update display
        if self.is_active:
            self.after(0, self._draw_meter)

    def set_recording_state(self, is_recording: bool):
        """Set recording state for visual feedback

        Args:
            is_recording: True if currently recording, False otherwise
        """
        self.recording_state = is_recording

        if not is_recording:
            with self.lock:
                self.current_level = 0.0
                self.peak_level = 0.0

        self._draw_meter()

    def set_colors(self, waveform_color: str = None, active_color: str = None,
                   background_color: str = None):
        """Update colors for theme compatibility (kept for API compatibility)"""
        pass

    def clear_waveform(self):
        """Clear the level display"""
        with self.lock:
            self.current_level = 0.0
            self.peak_level = 0.0
        self._draw_meter()

    def start_animation(self):
        """Start the animation/updates"""
        self.is_active = True

    def stop_animation(self):
        """Stop the animation/updates"""
        self.is_active = False

    def destroy(self):
        """Clean shutdown of the widget"""
        self.stop_animation()
        super().destroy()


if __name__ == "__main__":
    # Simple demo
    import time
    import math

    root = tk.Tk()
    root.title("Level Meter Demo")
    root.geometry("500x100")
    root.configure(bg="#2b2b2b")

    meter = WaveformVisualizer(root, width=450, height=60)
    meter.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
    meter.start_animation()
    meter.set_recording_state(True)

    def demo_update():
        t = time.time()
        level = abs(math.sin(t * 2)) * 0.8 + 0.1
        meter.update_audio_data(level)
        root.after(50, demo_update)

    demo_update()
    root.mainloop()
