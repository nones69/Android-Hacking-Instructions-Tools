import customtkinter as ctk
from tkinter import filedialog
from settings_manager import SettingsManager

class SettingsDialog(ctk.CTkToplevel):
    """A modal dialog for configuring application settings."""
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("600x300")
        self.transient(master)  # Keep on top of the main window
        self.grab_set()         # Modal behavior

        self.settings_manager = SettingsManager()
        self.entries = {}

        self.grid_columnconfigure(1, weight=1)

        # --- Create fields for each setting ---
        settings_to_configure = [
            ("adb_path", "ADB Path"),
            ("fastboot_path", "Fastboot Path"),
            ("idevice_id_path", "iDevice ID Path"),
            ("idevicename_path", "iDevice Name Path"),
            ("ideviceinfo_path", "iDevice Info Path"),
        ]

        for i, (key, label_text) in enumerate(settings_to_configure):
            label = ctk.CTkLabel(self, text=f"{label_text}:")
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")

            entry = ctk.CTkEntry(self, width=350)
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            self.entries[key] = entry

            browse_button = ctk.CTkButton(self, text="Browse...", width=80,
                                          command=lambda e=entry: self.browse_file(e))
            browse_button.grid(row=i, column=2, padx=10, pady=10)

        # --- Save/Cancel buttons ---
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=len(settings_to_configure), column=0, columnspan=3, pady=20)

        save_button = ctk.CTkButton(button_frame, text="Save", command=self.save_and_close)
        save_button.pack(side="left", padx=10)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left", padx=10)

        self.load_current_settings()

    def browse_file(self, entry_widget):
        file_path = filedialog.askopenfilename(
            title="Select Executable",
            filetypes=(("Executable files", "*.exe"), ("All files", "*.*"))
        )
        if file_path:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, file_path)

    def load_current_settings(self):
        for key, entry_widget in self.entries.items():
            entry_widget.insert(0, self.settings_manager.get_setting(key))

    def save_and_close(self):
        for key, entry_widget in self.entries.items():
            self.settings_manager.set_setting(key, entry_widget.get())
        self.settings_manager.save_settings()
        self.destroy()