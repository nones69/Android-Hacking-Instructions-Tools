import customtkinter as ctk
import json
from tkinter import filedialog
import os
import threading
import subprocess
from ducky_engine import run_ducky_script_on_desktop, convert_ducky_to_shell_commands, run_adb_payload
from path_utils import resource_path

PAYLOADS_FILE = resource_path("payloads/payloads.json")

class DuckyPayloadTab(ctk.CTkFrame):
    def __init__(self, master, log_callback, get_tool_path):
        super().__init__(master)
        self.log = log_callback
        self.get_tool_path = get_tool_path
        self.payloads = []

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top controls ---
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self.payload_combo = ctk.CTkOptionMenu(top_frame, values=["Select a payload..."], command=self.load_selected_payload)
        self.payload_combo.pack(side="left", padx=(0, 10))

        self.load_button = ctk.CTkButton(top_frame, text="Load .duck", command=self.load_duck_file)
        self.load_button.pack(side="left", padx=5)

        self.save_button = ctk.CTkButton(top_frame, text="Save .duck", command=self.save_duck_file)
        self.save_button.pack(side="left", padx=5)

        self.run_desktop_btn = ctk.CTkButton(top_frame, text="▶️ Run on Desktop", command=self.run_on_desktop)
        self.run_desktop_btn.pack(side="left", padx=5)

        self.run_android_btn = ctk.CTkButton(top_frame, text="▶️ Run on Android", command=self.run_on_android)
        self.run_android_btn.pack(side="left", padx=5)

        # --- Script Editor ---
        self.script_box = ctk.CTkTextbox(self, font=("Consolas", 12))
        self.script_box.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.script_box.insert("1.0", "REM Select a payload from the dropdown or paste your script here...")
        self.script_box.bind("<FocusIn>", self._clear_placeholder)

        self.load_payloads_into_dropdown()

    def _clear_placeholder(self, event):
        current_text = self.script_box.get("1.0", "end").strip()
        if current_text.startswith("REM Select a payload"):
            self.script_box.delete("1.0", "end")
            self.script_box.unbind("<FocusIn>")

    def load_payloads_into_dropdown(self):
        try:
            with open(PAYLOADS_FILE, "r", encoding="utf-8") as f:
                self.payloads = json.load(f)
                payload_names = ["Select a payload..."] + [p.get("name", "Unnamed") for p in self.payloads]
                self.payload_combo.configure(values=payload_names)
        except FileNotFoundError:
            self.log(f"[Error] {PAYLOADS_FILE} not found.")
            self.payloads = []
        except json.JSONDecodeError:
            self.log(f"[Error] Invalid JSON in {PAYLOADS_FILE}.")
            self.payloads = []

    def load_selected_payload(self, selected_name: str):
        if selected_name == "Select a payload...":
            return
        payload = next((p for p in self.payloads if p.get("name") == selected_name), None)
        if payload:
            self.script_box.delete("1.0", "end")
            self.script_box.insert("1.0", payload.get("script", ""))
            self.log(f"[Info] Loaded payload: {payload.get('name')}")
            if "description" in payload:
                self.log(f"[Info] Description: {payload['description']}")

    def load_duck_file(self):
        filepath = filedialog.askopenfilename(
            title="Load .duck Script",
            filetypes=(("Ducky Scripts", "*.duck"), ("Text Files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.script_box.delete("1.0", "end")
            self.script_box.insert("1.0", content)
            self.log(f"[Info] Loaded script from: {os.path.basename(filepath)}")
        except Exception as e:
            self.log(f"[Error] Failed to load file: {e}")

    def save_duck_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Save .duck Script",
            defaultextension=".duck",
            filetypes=(("Ducky Scripts", "*.duck"), ("Text Files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return
        try:
            content = self.script_box.get("1.0", "end-1c")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            self.log(f"[Info] Saved script to: {os.path.basename(filepath)}")
        except Exception as e:
            self.log(f"[Error] Failed to save file: {e}")

    def run_on_desktop(self):
        script_content = self.script_box.get("1.0", "end").strip()
        if not script_content:
            self.log("[Error] Script is empty. Nothing to run.")
            return
        self._set_buttons_state("disabled")
        thread = threading.Thread(target=self._run_desktop_thread, args=(script_content,), daemon=True)
        thread.start()

    def _run_desktop_thread(self, script_content):
        try:
            run_ducky_script_on_desktop(script_content, self.log)
        finally:
            self._set_buttons_state("normal")

    def run_on_android(self):
        script_content = self.script_box.get("1.0", "end").strip()
        if not script_content:
            self.log("[Error] Script is empty. Nothing to run.")
            return

        adb_path = self.get_tool_path("adb")
        # Check if adb_path is a valid file or if just 'adb' command
        if not (os.path.exists(adb_path) or adb_path == "adb"):
            self.log("[Error] ADB executable not found. Please check your tools directory or PATH.")
            return

        # Validate adb availability if only 'adb'
        if adb_path == "adb":
            try:
                startupinfo = subprocess.STARTUPINFO() if os.name == 'nt' else None
                if startupinfo:
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.run([adb_path, "version"], check=True, capture_output=True, startupinfo=startupinfo)
            except (FileNotFoundError, subprocess.CalledProcessError):
                self.log("[Error] ADB not found in system PATH. Please install or configure it.")
                return

        self.log("--- Converting Ducky Script to ADB ---")
        adb_commands = convert_ducky_to_shell_commands(script_content)
        for cmd in adb_commands:
            self.log(f"Converted: {cmd}")

        self._set_buttons_state("disabled")
        thread = threading.Thread(target=self._run_android_thread, args=(adb_commands, adb_path), daemon=True)
        thread.start()

    def _run_android_thread(self, adb_commands, adb_path):
        try:
            run_adb_payload(adb_commands, adb_path, self.log)
        finally:
            self._set_buttons_state("normal")

    def _set_buttons_state(self, state):
        self.run_desktop_btn.configure(state=state)
        self.run_android_btn.configure(state=state)
        self.load_button.configure(state=state)
        self.save_button.configure(state=state)
        self.payload_combo.configure(state=state)
