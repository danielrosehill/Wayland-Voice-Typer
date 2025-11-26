#!/usr/bin/env python3
"""
WhisperTux - Voice dictation application for Linux
Modern CustomTkinter GUI
"""

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
import threading
import time
import os
import sys
from pathlib import Path

# Import our custom modules
from src.audio_capture import AudioCapture
from src.whisper_manager import WhisperManager
from src.text_injector import TextInjector
from src.config_manager import ConfigManager
from src.global_shortcuts import GlobalShortcuts
from src.waveform_visualizer import WaveformVisualizer

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SettingsDialog(ctk.CTkToplevel):
    """Settings configuration dialog for WhisperTux"""

    def __init__(self, parent, config, global_shortcuts, update_callback, text_injector=None, app_instance=None):
        super().__init__(parent)
        self.parent = parent
        self.config = config
        self.global_shortcuts = global_shortcuts
        self.update_callback = update_callback
        self.text_injector = text_injector
        self.app_instance = app_instance

        self.title("WhisperTux Settings")
        self.geometry("550x800")
        self.resizable(True, True)
        self.minsize(500, 600)

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center the dialog
        self._center_dialog()

        # Variables
        self.shortcut_var = ctk.StringVar(value=self.config.get_setting('primary_shortcut', 'F12'))
        self.model_var = ctk.StringVar(value=self.config.get_setting('model', 'base'))
        self.always_on_top_var = ctk.BooleanVar(value=self.config.get_setting('always_on_top', True))
        self.use_clipboard_var = ctk.BooleanVar(value=self.config.get_setting('use_clipboard', False))
        self.key_delay_var = ctk.StringVar(value=str(self.config.get_setting('key_delay', 15)))
        self.audio_device_var = ctk.StringVar()
        self.keyboard_device_var = ctk.StringVar()

        self.audio_device_options = []
        self.audio_device_values = []
        self.keyboard_options = []
        self.keyboard_values = []

        # Create scrollable frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="")
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create sections
        self._create_shortcuts_section()
        self._create_model_section()
        self._create_model_directories_section()
        self._create_general_section()
        self._create_word_overrides_section()
        self._create_buttons()

    def _center_dialog(self):
        """Center the dialog on the parent window"""
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        dialog_width = 550
        dialog_height = 800
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    def _create_shortcuts_section(self):
        """Create the global shortcuts configuration section"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Global Shortcuts", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(frame, text="Select a global shortcut key for voice recording:", text_color="gray").pack(anchor="w", padx=15)

        # Current shortcut display
        current_frame = ctk.CTkFrame(frame, fg_color="transparent")
        current_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(current_frame, text="Current Shortcut:").pack(side="left")
        self.current_shortcut_label = ctk.CTkLabel(current_frame, text=self.config.get_setting('primary_shortcut', 'F12'), font=ctk.CTkFont(weight="bold"), text_color="#3B8ED0")
        self.current_shortcut_label.pack(side="right")

        # Shortcut selection
        selection_frame = ctk.CTkFrame(frame, fg_color="transparent")
        selection_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(selection_frame, text="New Shortcut:").pack(side="left")

        shortcut_options = self._get_shortcut_options()
        self.shortcut_combo = ctk.CTkComboBox(selection_frame, variable=self.shortcut_var, values=shortcut_options, width=180)
        self.shortcut_combo.pack(side="right")

        # Test button
        test_frame = ctk.CTkFrame(frame, fg_color="transparent")
        test_frame.pack(fill="x", padx=15, pady=(10, 15))
        self.test_button = ctk.CTkButton(test_frame, text="Test Shortcut", command=self._test_shortcut, width=120)
        self.test_button.pack(side="left")
        self.test_status_label = ctk.CTkLabel(test_frame, text="", text_color="gray")
        self.test_status_label.pack(side="right")

    def _get_shortcut_options(self):
        """Get available shortcut options"""
        options = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']
        for prefix in ['Ctrl+', 'Alt+', 'Shift+', 'Super+']:
            for fkey in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
                options.append(f'{prefix}{fkey}')
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            options.append(f'Ctrl+{letter}')
            options.append(f'Ctrl+Shift+{letter}')
            options.append(f'Super+{letter}')
        return options

    def _create_model_section(self):
        """Create the model configuration section"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Model", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        model_frame = ctk.CTkFrame(frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(model_frame, text="Whisper Model:").pack(side="left")

        try:
            available_models = []
            if self.app_instance and hasattr(self.app_instance, 'whisper_manager'):
                available_models = self.app_instance.whisper_manager.get_available_models()
            if not available_models:
                available_models = ["No models found"]
        except Exception:
            available_models = ["No models found"]

        current_model = self.config.get_setting('model', 'base')
        if current_model in available_models:
            self.model_var.set(current_model)
        elif available_models and available_models[0] != "No models found":
            self.model_var.set(available_models[0])

        self.model_combo_dialog = ctk.CTkComboBox(model_frame, variable=self.model_var, values=available_models, width=250)
        self.model_combo_dialog.pack(side="right")

        # Download button
        download_frame = ctk.CTkFrame(frame, fg_color="transparent")
        download_frame.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkButton(download_frame, text="Download Models", command=self._show_model_download_from_settings, width=140).pack(side="right")

    def _create_model_directories_section(self):
        """Create the model directories configuration section"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Model Directories", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        ctk.CTkLabel(frame, text="Configure directories to scan for Whisper models:", text_color="gray").pack(anchor="w", padx=15)

        # Directory listbox (using tkinter Listbox within CTk)
        list_frame = ctk.CTkFrame(frame)
        list_frame.pack(fill="x", padx=15, pady=10)

        self.dirs_listbox = tk.Listbox(list_frame, height=4, font=("Arial", 10), bg="#2b2b2b", fg="#ffffff", selectbackground="#1f538d", highlightthickness=0, bd=0)
        scrollbar = ctk.CTkScrollbar(list_frame, command=self.dirs_listbox.yview)
        self.dirs_listbox.configure(yscrollcommand=scrollbar.set)
        self.dirs_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._refresh_directories_list()

        # Add directory
        add_frame = ctk.CTkFrame(frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=15, pady=5)
        self.new_dir_entry = ctk.CTkEntry(add_frame, placeholder_text="Enter directory path...", width=300)
        self.new_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(add_frame, text="Browse", command=self._browse_directory, width=80).pack(side="right")

        # Buttons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkButton(buttons_frame, text="Add", command=self._add_model_directory, width=80, fg_color="#2d7d46", hover_color="#236b38").pack(side="left")
        ctk.CTkButton(buttons_frame, text="Remove", command=self._remove_model_directory, width=80, fg_color="#d4652f", hover_color="#b85528").pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Refresh Models", command=self._refresh_models_after_dirs_change, width=120).pack(side="right")

    def _create_general_section(self):
        """Create the general settings section"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="General Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))

        # Always on top
        ctk.CTkSwitch(frame, text="Keep window always on top", variable=self.always_on_top_var).pack(anchor="w", padx=15, pady=5)

        # Use clipboard
        ctk.CTkSwitch(frame, text="Use clipboard for text injection", variable=self.use_clipboard_var).pack(anchor="w", padx=15, pady=5)

        # Key delay
        delay_frame = ctk.CTkFrame(frame, fg_color="transparent")
        delay_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(delay_frame, text="Key Delay (ms):").pack(side="left")
        ctk.CTkEntry(delay_frame, textvariable=self.key_delay_var, width=80).pack(side="right")

        # Microphone
        mic_frame = ctk.CTkFrame(frame, fg_color="transparent")
        mic_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(mic_frame, text="Microphone:").pack(side="left")

        try:
            available_mics = AudioCapture.get_available_input_devices()
            mic_options = ["System Default"]
            mic_values = [None]
            for device in available_mics:
                mic_options.append(device['display_name'])
                mic_values.append(device['id'])
        except Exception:
            mic_options = ["System Default"]
            mic_values = [None]

        self.audio_device_options = mic_options
        self.audio_device_values = mic_values

        current_audio_device = self.config.get_setting('audio_device', None)
        current_audio_index = 0
        if current_audio_device in mic_values:
            current_audio_index = mic_values.index(current_audio_device)
        self.audio_device_var.set(mic_options[current_audio_index])

        self.mic_combo = ctk.CTkComboBox(mic_frame, variable=self.audio_device_var, values=mic_options, width=250)
        self.mic_combo.pack(side="right")

        # Keyboard device
        kb_frame = ctk.CTkFrame(frame, fg_color="transparent")
        kb_frame.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkLabel(kb_frame, text="Keyboard Device:").pack(side="left")

        try:
            from src.global_shortcuts import get_available_keyboards
            available_keyboards = get_available_keyboards()
            keyboard_options = ["Auto-detect (All Keyboards)"]
            keyboard_values = [""]
            for kb in available_keyboards:
                keyboard_options.append(kb['display_name'])
                keyboard_values.append(kb['path'])
        except Exception:
            keyboard_options = ["Auto-detect (All Keyboards)"]
            keyboard_values = [""]

        self.keyboard_options = keyboard_options
        self.keyboard_values = keyboard_values

        current_device = self.config.get_setting('keyboard_device', '')
        current_index = 0
        if current_device in keyboard_values:
            current_index = keyboard_values.index(current_device)
        self.keyboard_device_var.set(keyboard_options[current_index])

        self.kb_combo = ctk.CTkComboBox(kb_frame, variable=self.keyboard_device_var, values=keyboard_options, width=250)
        self.kb_combo.pack(side="right")

    def _create_word_overrides_section(self):
        """Create the word overrides configuration section"""
        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(frame, text="Word Overrides", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=15, pady=(15, 10))
        ctk.CTkLabel(frame, text="Configure word replacements (e.g., 'tech' -> 'tek'):", text_color="gray").pack(anchor="w", padx=15)

        # Overrides list using Treeview
        list_frame = ctk.CTkFrame(frame)
        list_frame.pack(fill="x", padx=15, pady=10)

        columns = ('original', 'replacement')
        self.overrides_tree = tk.ttk.Treeview(list_frame, columns=columns, show='headings', height=4)
        self.overrides_tree.heading('original', text='Original')
        self.overrides_tree.heading('replacement', text='Replacement')
        self.overrides_tree.column('original', width=150)
        self.overrides_tree.column('replacement', width=150)

        # Style the treeview for dark mode
        style = tk.ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b", rowheight=25)
        style.configure("Treeview.Heading", background="#3b3b3b", foreground="white")
        style.map('Treeview', background=[('selected', '#1f538d')])

        tree_scrollbar = ctk.CTkScrollbar(list_frame, command=self.overrides_tree.yview)
        self.overrides_tree.configure(yscrollcommand=tree_scrollbar.set)
        self.overrides_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")

        self._refresh_overrides_list()

        # Add override inputs
        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(input_frame, text="Original:").pack(side="left")
        self.original_entry = ctk.CTkEntry(input_frame, width=120)
        self.original_entry.pack(side="left", padx=5)
        ctk.CTkLabel(input_frame, text="->").pack(side="left")
        ctk.CTkLabel(input_frame, text="Replacement:").pack(side="left", padx=(5, 0))
        self.replacement_entry = ctk.CTkEntry(input_frame, width=120)
        self.replacement_entry.pack(side="left", padx=5)

        # Buttons
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkButton(buttons_frame, text="Add", command=self._add_word_override, width=70, fg_color="#2d7d46", hover_color="#236b38").pack(side="left")
        ctk.CTkButton(buttons_frame, text="Edit", command=self._edit_word_override, width=70).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Delete", command=self._delete_word_override, width=70, fg_color="#d4652f", hover_color="#b85528").pack(side="left")
        ctk.CTkButton(buttons_frame, text="Clear All", command=self._clear_all_overrides, width=80, fg_color="#c42b1c", hover_color="#a52714").pack(side="right")

        self.overrides_tree.bind('<Double-1>', lambda e: self._edit_word_override())

    def _create_buttons(self):
        """Create dialog action buttons"""
        button_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(button_frame, text="Cancel", command=self.destroy, width=100, fg_color="#4a4a4a", hover_color="#3a3a3a").pack(side="left")
        ctk.CTkButton(button_frame, text="Reset to Defaults", command=self._reset_defaults, width=130, fg_color="#d4652f", hover_color="#b85528").pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Save Settings", command=self._save_settings, width=120, fg_color="#2d7d46", hover_color="#236b38").pack(side="right")

    def _refresh_directories_list(self):
        """Refresh the model directories list display"""
        self.dirs_listbox.delete(0, tk.END)
        directories = self.config.get_model_directories()
        for directory in directories:
            self.dirs_listbox.insert(tk.END, directory)

    def _browse_directory(self):
        """Open file dialog to browse for a directory"""
        from tkinter import filedialog
        directory = filedialog.askdirectory(title="Select Model Directory", initialdir=str(Path.home()))
        if directory:
            self.new_dir_entry.delete(0, tk.END)
            self.new_dir_entry.insert(0, directory)

    def _add_model_directory(self):
        """Add a new model directory"""
        new_dir = self.new_dir_entry.get().strip()
        if not new_dir:
            messagebox.showwarning("Invalid Input", "Please enter a directory path.")
            return

        expanded_path = Path(new_dir).expanduser()
        if not expanded_path.exists():
            if not messagebox.askyesno("Directory Not Found", f"Directory '{new_dir}' does not exist. Add it anyway?"):
                return

        if self.config.add_model_directory(new_dir):
            self._refresh_directories_list()
            self.new_dir_entry.delete(0, tk.END)
        else:
            messagebox.showinfo("Already Added", "This directory is already in the list.")

    def _remove_model_directory(self):
        """Remove the selected model directory"""
        selection = self.dirs_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a directory to remove.")
            return

        selected_dir = self.dirs_listbox.get(selection[0])
        if self.config.remove_model_directory(selected_dir):
            self._refresh_directories_list()

    def _refresh_models_after_dirs_change(self):
        """Refresh the model list after directory changes"""
        self.config.save_config()
        self._refresh_model_combo_dialog()
        messagebox.showinfo("Models Refreshed", "Model list has been refreshed with the current directories.")

    def _refresh_overrides_list(self):
        """Refresh the word overrides list display"""
        for item in self.overrides_tree.get_children():
            self.overrides_tree.delete(item)
        word_overrides = self.config.get_word_overrides()
        for original, replacement in word_overrides.items():
            self.overrides_tree.insert('', 'end', values=(original, replacement))

    def _add_word_override(self):
        """Add a new word override"""
        original = self.original_entry.get().strip()
        replacement = self.replacement_entry.get().strip()
        if not original or not replacement:
            messagebox.showwarning("Invalid Input", "Both original and replacement words are required.")
            return
        self.config.add_word_override(original, replacement)
        self._refresh_overrides_list()
        self.original_entry.delete(0, tk.END)
        self.replacement_entry.delete(0, tk.END)

    def _edit_word_override(self):
        """Edit the selected word override"""
        selection = self.overrides_tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.overrides_tree.item(item, 'values')
        original, replacement = values
        self.original_entry.delete(0, tk.END)
        self.original_entry.insert(0, original)
        self.replacement_entry.delete(0, tk.END)
        self.replacement_entry.insert(0, replacement)
        self.config.remove_word_override(original)
        self._refresh_overrides_list()

    def _delete_word_override(self):
        """Delete the selected word override"""
        selection = self.overrides_tree.selection()
        if not selection:
            return
        item = selection[0]
        values = self.overrides_tree.item(item, 'values')
        original = values[0]
        self.config.remove_word_override(original)
        self._refresh_overrides_list()

    def _clear_all_overrides(self):
        """Clear all word overrides"""
        self.config.clear_word_overrides()
        self._refresh_overrides_list()

    def _test_shortcut(self):
        """Test the selected shortcut"""
        selected_shortcut = self.shortcut_var.get()
        if not selected_shortcut:
            self.test_status_label.configure(text="No shortcut selected", text_color="#c42b1c")
            return

        self.test_status_label.configure(text="Testing...", text_color="#d4652f")
        self.test_button.configure(state="disabled")

        def test_shortcut_thread():
            try:
                test_triggered = threading.Event()

                def test_callback():
                    test_triggered.set()

                from src.global_shortcuts import GlobalShortcuts
                test_shortcuts = GlobalShortcuts(selected_shortcut, test_callback)

                if test_shortcuts.start():
                    self.after(100, lambda: self.test_status_label.configure(text=f"Press {selected_shortcut} within 5s...", text_color="#3B8ED0"))

                    if test_triggered.wait(timeout=5):
                        self.after(100, lambda: self.test_status_label.configure(text="Test successful!", text_color="#2d7d46"))
                    else:
                        self.after(100, lambda: self.test_status_label.configure(text="No response", text_color="#c42b1c"))

                    test_shortcuts.stop()
                else:
                    self.after(100, lambda: self.test_status_label.configure(text="Could not start test", text_color="#c42b1c"))
            except Exception as e:
                self.after(100, lambda: self.test_status_label.configure(text=f"Error: {str(e)[:20]}", text_color="#c42b1c"))
            finally:
                self.after(100, lambda: self.test_button.configure(state="normal"))

        threading.Thread(target=test_shortcut_thread, daemon=True).start()

    def _save_settings(self):
        """Save all settings and apply them"""
        try:
            new_shortcut = self.shortcut_var.get()
            old_shortcut = self.config.get_setting('primary_shortcut')

            selected_keyboard_index = self.keyboard_options.index(self.keyboard_device_var.get())
            selected_keyboard_path = self.keyboard_values[selected_keyboard_index]

            try:
                selected_audio_index = self.audio_device_options.index(self.audio_device_var.get())
            except ValueError:
                selected_audio_index = 0

            key_delay_str = self.key_delay_var.get().strip()
            try:
                key_delay_value = int(key_delay_str)
                if key_delay_value < 1:
                    messagebox.showwarning("Invalid Input", "Key delay must be a positive integer (minimum 1ms).")
                    return
                self.config.set_setting('key_delay', key_delay_value)
            except ValueError:
                messagebox.showwarning("Invalid Input", "Key delay must be a valid number.")
                return

            self.config.set_setting('primary_shortcut', new_shortcut)
            self.config.set_setting('always_on_top', self.always_on_top_var.get())
            self.config.set_setting('use_clipboard', self.use_clipboard_var.get())
            self.config.set_setting('keyboard_device', selected_keyboard_path)
            self.config.set_setting('audio_device', self.audio_device_values[selected_audio_index])

            new_model = self.model_var.get()
            if new_model != "No models found":
                self.config.set_setting('model', new_model)
                if hasattr(self.parent, 'whisper_manager'):
                    try:
                        self.parent.whisper_manager.set_model(new_model)
                    except Exception as e:
                        print(f"Failed to update model: {e}")

            if not self.config.save_config():
                messagebox.showerror("Error", "Failed to save settings to file!")
                return

            selected_audio_device = self.audio_device_values[selected_audio_index]
            if self.app_instance and hasattr(self.app_instance, 'audio_capture'):
                set_result = self.app_instance.audio_capture.set_device(selected_audio_device)
                if not set_result and selected_audio_device is not None:
                    messagebox.showwarning("Audio Device", "Selected microphone could not be activated. Using previous device.")

            self.parent.attributes('-topmost', self.always_on_top_var.get())

            if new_shortcut != old_shortcut:
                if self.global_shortcuts:
                    self.global_shortcuts.stop()
                    self.global_shortcuts.update_shortcut(new_shortcut)
                    if not self.global_shortcuts.start():
                        messagebox.showwarning("Warning", f"Settings saved, but failed to activate shortcut '{new_shortcut}'.")

            if self.current_shortcut_label:
                self.current_shortcut_label.configure(text=new_shortcut)

            if self.update_callback:
                self.update_callback()

            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def _reset_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            try:
                self.config.reset_to_defaults()
                new_shortcut = self.config.get_setting('primary_shortcut')
                self.shortcut_var.set(new_shortcut)
                self.always_on_top_var.set(self.config.get_setting('always_on_top'))
                self.key_delay_var.set(str(self.config.get_setting('key_delay')))
                self.use_clipboard_var.set(self.config.get_setting('use_clipboard'))
                if self.audio_device_options:
                    self.audio_device_var.set(self.audio_device_options[0])
                if self.current_shortcut_label:
                    self.current_shortcut_label.configure(text=new_shortcut)
                self._refresh_overrides_list()
                self.original_entry.delete(0, tk.END)
                self.replacement_entry.delete(0, tk.END)
                self.test_status_label.configure(text="Settings reset", text_color="#3B8ED0")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")

    def _show_model_download_from_settings(self):
        """Show model download dialog from settings"""
        if self.app_instance and hasattr(self.app_instance, '_show_model_download'):
            self.app_instance._show_model_download(callback=self._refresh_model_combo_dialog)

    def _refresh_model_combo_dialog(self):
        """Refresh the model combo box in this settings dialog"""
        try:
            available_models = []
            if self.app_instance and hasattr(self.app_instance, 'whisper_manager'):
                available_models = self.app_instance.whisper_manager.get_available_models()
            if not available_models:
                available_models = ["No models found"]

            if hasattr(self, 'model_combo_dialog') and self.model_combo_dialog:
                self.model_combo_dialog.configure(values=available_models)
                current_model = self.config.get_setting('model', 'base')
                if current_model in available_models:
                    self.model_var.set(current_model)
                elif available_models and available_models[0] != "No models found":
                    self.model_var.set(available_models[0])
        except Exception as e:
            print(f"Error refreshing settings dialog model combo: {e}")


class WhisperTuxApp:
    """Main application class for WhisperTux voice dictation"""

    def __init__(self):
        # Initialize core components
        self.config = ConfigManager()

        audio_device_id = self.config.get_setting('audio_device', None)
        self.audio_capture = AudioCapture(device_id=audio_device_id)
        self.whisper_manager = WhisperManager()
        self.text_injector = TextInjector(self.config)
        self.global_shortcuts = None

        # Application state
        self.is_recording = False
        self.is_processing = False
        self.current_transcription = ""

        # GUI components
        self.root = None
        self.status_label = None
        self.record_button = None
        self.transcription_text = None
        self.waveform_visualizer = None
        self.shortcut_display_label = None
        self.audio_device_display_label = None
        self.model_display_label = None
        self.key_delay_display_label = None

        # Initialize GUI
        self._setup_gui()
        self._setup_global_shortcuts()

    def _setup_gui(self):
        """Initialize the main GUI window with CustomTkinter"""
        self.root = ctk.CTk()
        self.root.title("WhisperTux - Voice Dictation")
        self.root.geometry("480x650")
        self.root.minsize(450, 550)

        # Always on top
        self.root.attributes('-topmost', self.config.get_setting('always_on_top', True))
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Position window
        self._position_window()

        # Main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create GUI sections
        self._create_header()
        self._create_status_section()
        self._create_audio_section()
        self._create_transcription_section()
        self._create_control_buttons()

    def _position_window(self):
        """Position window in bottom-left corner of the screen"""
        self.root.update_idletasks()
        screen_height = self.root.winfo_screenheight()
        window_width = 480
        window_height = 650
        x_position = 20
        y_position = screen_height - window_height - 60
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    def _create_header(self):
        """Create the application header"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))

        # Logo and text container
        content_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        content_frame.pack(anchor="w")

        # Logo
        logo_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=(0, 15))

        try:
            from PIL import Image
            img = Image.open("assets/whispertux.png")
            img = img.resize((70, 60), Image.Resampling.LANCZOS)
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(70, 60))
            logo_label = ctk.CTkLabel(logo_frame, image=self.logo_image, text="")
            logo_label.pack()
        except Exception as e:
            print(f"Failed to load whispertux.png: {e}")
            logo_label = ctk.CTkLabel(logo_frame, text="", font=ctk.CTkFont(size=28))
            logo_label.pack()

        # Text
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.pack(side="left", pady=(8, 0))

        title_label = ctk.CTkLabel(text_frame, text="whispertux", font=ctk.CTkFont(size=22, weight="bold"), text_color="#3B8ED0")
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(text_frame, text="Voice Dictation for Linux", font=ctk.CTkFont(size=11), text_color="#8B8B8B")
        subtitle_label.pack(anchor="w")

    def _create_status_section(self):
        """Create the status display section"""
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", pady=(0, 10))

        # Header
        header = ctk.CTkFrame(status_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(header, text="Status", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")

        self.status_label = ctk.CTkLabel(header, text="Ready", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2d7d46")
        self.status_label.pack(side="right")

        # Info grid
        info_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 12))

        # Model
        model_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        model_row.pack(fill="x", pady=2)
        ctk.CTkLabel(model_row, text="Model:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.model_display_label = ctk.CTkLabel(model_row, text=self.config.get_setting('model', 'base'), font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B8ED0")
        self.model_display_label.pack(side="left", padx=(8, 0))

        # Shortcut
        shortcut_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        shortcut_row.pack(fill="x", pady=2)
        ctk.CTkLabel(shortcut_row, text="Shortcut:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.shortcut_display_label = ctk.CTkLabel(shortcut_row, text=self.config.get_setting('primary_shortcut', 'F12'), font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B8ED0")
        self.shortcut_display_label.pack(side="left", padx=(8, 0))

        # Key delay
        delay_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        delay_row.pack(fill="x", pady=2)
        ctk.CTkLabel(delay_row, text="Key Delay:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.key_delay_display_label = ctk.CTkLabel(delay_row, text=f"{self.config.get_setting('key_delay', 15)}ms", font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B8ED0")
        self.key_delay_display_label.pack(side="left", padx=(8, 0))

        # Microphone
        mic_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        mic_row.pack(fill="x", pady=2)
        ctk.CTkLabel(mic_row, text="Microphone:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.audio_device_display_label = ctk.CTkLabel(mic_row, text=self._get_current_audio_device_name(), font=ctk.CTkFont(size=11, weight="bold"), text_color="#3B8ED0", wraplength=280)
        self.audio_device_display_label.pack(side="left", padx=(8, 0))

    def _create_audio_section(self):
        """Create the audio monitoring section with waveform visualizer"""
        audio_frame = ctk.CTkFrame(self.main_frame)
        audio_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(audio_frame, text="Audio Level", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))

        # Waveform visualizer (uses tkinter Frame internally)
        viz_container = ctk.CTkFrame(audio_frame, fg_color="transparent")
        viz_container.pack(fill="x", padx=15, pady=(0, 12))

        self.waveform_visualizer = WaveformVisualizer(viz_container, width=420, height=120)
        self.waveform_visualizer.pack(fill="x", expand=True)

    def _create_transcription_section(self):
        """Create the transcription display section"""
        trans_frame = ctk.CTkFrame(self.main_frame)
        trans_frame.pack(fill="both", expand=True, pady=(0, 10))

        ctk.CTkLabel(trans_frame, text="Transcription", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))

        # Text widget
        text_container = ctk.CTkFrame(trans_frame, fg_color="transparent")
        text_container.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        self.transcription_text = ctk.CTkTextbox(text_container, height=120, font=ctk.CTkFont(size=11), wrap="word")
        self.transcription_text.pack(fill="both", expand=True)

        # Buttons
        buttons_frame = ctk.CTkFrame(trans_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 12))

        ctk.CTkButton(buttons_frame, text="Copy", command=self._copy_all_transcription, width=80).pack(side="left")
        ctk.CTkButton(buttons_frame, text="Clear", command=self._clear_transcription, width=80, fg_color="#4a4a4a", hover_color="#3a3a3a").pack(side="left", padx=8)

    def _create_control_buttons(self):
        """Create the main control buttons"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(5, 0))

        ctk.CTkButton(button_frame, text="Quit", command=self._on_closing, width=90, fg_color="#c42b1c", hover_color="#a52714").pack(side="left")
        ctk.CTkButton(button_frame, text="Settings", command=self._show_settings, width=100, fg_color="#4a4a4a", hover_color="#3a3a3a").pack(side="left", padx=10)

        self.record_button = ctk.CTkButton(button_frame, text="Record", command=self._toggle_recording, width=130, height=40, fg_color="#2d7d46", hover_color="#236b38", font=ctk.CTkFont(size=13, weight="bold"))
        self.record_button.pack(side="right")

    def _setup_global_shortcuts(self):
        """Set up global keyboard shortcuts"""
        try:
            keyboard_device = self.config.get_setting('keyboard_device', '')
            device_path = keyboard_device if keyboard_device else None
            self.global_shortcuts = GlobalShortcuts(
                primary_key=self.config.get_setting('primary_shortcut', 'F12'),
                callback=self._toggle_recording,
                device_path=device_path
            )
            self.global_shortcuts.start()
            print("Global shortcuts initialized")
        except Exception as e:
            print(f"ERROR: Failed to setup global shortcuts: {e}")

    def _start_audio_monitor(self):
        """Start the audio level monitoring thread"""
        def monitor_audio():
            while hasattr(self, 'root') and self.root:
                try:
                    level = self.audio_capture.get_audio_level()
                    if self.root:
                        self.root.after(0, self._update_audio_level, level)
                    time.sleep(0.05)
                except:
                    break

        self.monitor_thread = threading.Thread(target=monitor_audio, daemon=True)
        self.monitor_thread.start()

    def _stop_audio_monitor(self):
        """Stop the audio level monitoring thread"""
        pass

    def _update_audio_level(self, level):
        """Update the waveform visualizer with audio level data"""
        if self.waveform_visualizer:
            self.waveform_visualizer.update_audio_data(level)

    def _reset_audio_level(self):
        """Reset the waveform visualizer"""
        if self.waveform_visualizer:
            self.waveform_visualizer.clear_waveform()

    def _clear_transcription(self):
        """Clear the transcription text area"""
        if self.transcription_text:
            self.transcription_text.delete("1.0", "end")

    def _copy_all_transcription(self):
        """Copy all transcription text to clipboard"""
        if self.transcription_text:
            text_content = self.transcription_text.get("1.0", "end").strip()
            if text_content:
                self.root.clipboard_clear()
                self.root.clipboard_append(text_content)

    def _toggle_recording(self):
        """Toggle recording state"""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        """Start audio recording"""
        if self.is_recording or self.is_processing:
            return

        try:
            self.is_recording = True
            self._update_ui_recording_state()

            self._start_audio_monitor()
            if self.waveform_visualizer:
                self.waveform_visualizer.start_animation()

            def record_audio():
                try:
                    self.audio_capture.start_recording()
                except Exception as e:
                    self.root.after(0, self._show_error, f"Failed to start recording: {e}")
                    self.root.after(0, self._stop_recording)

            threading.Thread(target=record_audio, daemon=True).start()

        except Exception as e:
            self._show_error(f"Failed to start recording: {e}")
            self.is_recording = False
            self._update_ui_recording_state()

    def _stop_recording(self):
        """Stop audio recording and process transcription"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.is_processing = True
        self._update_ui_recording_state()

        def process_recording():
            try:
                audio_data = self.audio_capture.stop_recording()

                if audio_data is not None and len(audio_data) > 0:
                    transcription = self.whisper_manager.transcribe_audio(audio_data)
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, self._handle_transcription, transcription)
                else:
                    if hasattr(self, 'root') and self.root:
                        self.root.after(0, self._handle_transcription, None)

            except Exception as e:
                if hasattr(self, 'root') and self.root:
                    self.root.after(0, self._show_error, f"Transcription failed: {e}")
            finally:
                self.is_processing = False
                if hasattr(self, 'root') and self.root:
                    self.root.after(0, self._update_ui_recording_state)

        threading.Thread(target=process_recording, daemon=True).start()

    def _handle_transcription(self, transcription):
        """Handle completed transcription"""
        self._stop_audio_monitor()
        if self.waveform_visualizer:
            self.waveform_visualizer.stop_animation()
        self._reset_audio_level()

        if transcription and transcription.strip():
            cleaned_transcription = transcription.strip()
            blank_indicators = ["[blank_audio]", "(blank)", "(silence)", "[silence]"]
            is_blank = any(indicator in cleaned_transcription.lower() for indicator in blank_indicators) or cleaned_transcription == "[BLANK_AUDIO]"

            if not is_blank and cleaned_transcription:
                self.transcription_text.insert("end", f"{cleaned_transcription}\n")
                self.transcription_text.see("end")

                try:
                    self.text_injector.inject_text(cleaned_transcription)
                except Exception:
                    self.status_label.configure(text="Text injection failed", text_color="#c42b1c")
        else:
            print("No speech detected")
            self.status_label.configure(text="No speech detected", text_color="#8B8B8B")
            self.transcription_text.insert("end", "[No speech detected]\n")
            self.transcription_text.see("end")

    def _update_ui_recording_state(self):
        """Update UI elements based on recording state"""
        if self.is_recording:
            self.status_label.configure(text="Recording...", text_color="#c42b1c")
            self.record_button.configure(text="Stop Recording", fg_color="#c42b1c", hover_color="#a52714")
            if self.waveform_visualizer:
                self.waveform_visualizer.set_recording_state(True)
        elif self.is_processing:
            self.status_label.configure(text="Processing...", text_color="#d4652f")
            self.record_button.configure(text="Processing...", fg_color="#d4652f", hover_color="#b85528", state="disabled")
            if self.waveform_visualizer:
                self.waveform_visualizer.set_recording_state(False)
        else:
            self.status_label.configure(text="Ready", text_color="#2d7d46")
            self.record_button.configure(text="Record", fg_color="#2d7d46", hover_color="#236b38", state="normal")
            if self.waveform_visualizer:
                self.waveform_visualizer.set_recording_state(False)

    def _show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self.root, self.config, self.global_shortcuts, self._update_shortcut_display, self.text_injector, self)

    def _get_current_audio_device_name(self):
        """Get the display name of the current audio device"""
        try:
            configured_device_id = self.config.get_setting('audio_device', None)
            if configured_device_id is None:
                return "System Default"

            current_device_info = self.audio_capture.get_current_device_info()
            if current_device_info:
                name = current_device_info['name']
                if len(name) > 32:
                    name = name[:29] + "..."
                return name

            return "Unknown Device"
        except:
            return "Error"

    def _update_shortcut_display(self):
        """Update all status displays in the main window"""
        if self.shortcut_display_label:
            self.shortcut_display_label.configure(text=self.config.get_setting('primary_shortcut', 'F12'))

        if self.model_display_label:
            self.model_display_label.configure(text=self.config.get_setting('model', 'base'))

        if self.key_delay_display_label:
            self.key_delay_display_label.configure(text=f"{self.config.get_setting('key_delay', 15)}ms")

        if self.audio_device_display_label:
            self.audio_device_display_label.configure(text=self._get_current_audio_device_name())

    def _show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)

    def _show_model_download(self, callback=None):
        """Show model download dialog"""
        available_models = ["base.en", "small.en", "medium.en", "large-v3", "base", "small", "medium", "large"]

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Download Whisper Models")
        dialog.geometry("420x320")
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 420) // 2
        y = (dialog.winfo_screenheight() - 320) // 2
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text="Download Whisper Models", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="Select a model to download:").pack(pady=5)

        model_var = ctk.StringVar(value=available_models[0])
        model_combo = ctk.CTkComboBox(dialog, variable=model_var, values=available_models, width=200)
        model_combo.pack(pady=10)

        progress = ctk.CTkProgressBar(dialog, mode="indeterminate", width=300)
        progress.pack(pady=10)

        status_label = ctk.CTkLabel(dialog, text="")
        status_label.pack(pady=5)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=15)

        def download_model():
            selected_model = model_var.get()
            status_label.configure(text=f"Downloading {selected_model}...")
            progress.start()

            def download_thread():
                try:
                    project_root = Path(__file__).parent
                    models_dir = project_root / "whisper.cpp" / "models"
                    import subprocess
                    result = subprocess.run(
                        ["bash", str(models_dir / "download-ggml-model.sh"), selected_model],
                        cwd=str(models_dir), capture_output=True, text=True
                    )

                    if result.returncode == 0:
                        dialog.after(100, lambda: status_label.configure(text=f"{selected_model} downloaded!"))
                        dialog.after(100, progress.stop)
                        dialog.after(2000, lambda: self._refresh_model_combo())
                        if callback:
                            dialog.after(2000, callback)
                        dialog.after(2000, dialog.destroy)
                    else:
                        dialog.after(100, lambda: status_label.configure(text=f"Download failed"))
                        dialog.after(100, progress.stop)
                except Exception as e:
                    dialog.after(100, lambda: status_label.configure(text=f"Error: {str(e)[:30]}"))
                    dialog.after(100, progress.stop)

            threading.Thread(target=download_thread, daemon=True).start()

        ctk.CTkButton(button_frame, text="Download", command=download_model, fg_color="#2d7d46", hover_color="#236b38").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy, fg_color="#4a4a4a", hover_color="#3a3a3a").pack(side="left", padx=5)

    def _refresh_model_combo(self):
        """Refresh the model settings after downloading new models"""
        try:
            available_models = self.whisper_manager.get_available_models()
            if available_models:
                current_model = self.config.get_setting('model', 'base')
                if current_model not in available_models and available_models:
                    self.config.set_setting('model', available_models[0])
                    self.config.save_config()
                    self._update_shortcut_display()
        except Exception as e:
            print(f"Error refreshing model settings: {e}")

    def _on_closing(self):
        """Handle application closing"""
        try:
            if self.global_shortcuts:
                self.global_shortcuts.stop()

            if self.is_recording:
                self.audio_capture.stop_recording()

            if self.waveform_visualizer:
                self.waveform_visualizer.stop_animation()

            self.config.save_config()

        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            self.root.destroy()

    def run(self):
        """Start the application"""
        print("Starting WhisperTux...")

        if not self.whisper_manager.initialize():
            messagebox.showerror(
                "Initialization Error",
                "Failed to initialize Whisper. Please ensure whisper.cpp is built.\nRun the build scripts first."
            )
            return False

        self.root.mainloop()
        return True


def main():
    """Main entry point"""
    if not sys.platform.startswith('linux'):
        print("Warning: This application is designed for Linux systems")

    app = WhisperTuxApp()
    success = app.run()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
