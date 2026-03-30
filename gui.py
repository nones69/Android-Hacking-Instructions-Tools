import os
import customtkinter as ctk
import tkinter as tk
from device_detector import detect_android_devices, detect_ios_devices
from ducky_tab import DuckyPayloadTab
from device_detector import get_tool_path
from user_profile_tab import UserProfileTab
from path_utils import resource_path
from log_manager import LogManager
from firmware_flasher_tab import FirmwareFlasherTab
from settings_dialog import SettingsDialog
PAYLOADS_DIR = os.path.join(os.getcwd(), 'payloads')
os.makedirs(PAYLOADS_DIR, exist_ok=True)

class MobileDeviceToolkitApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mobile Device Toolkit")
        self.geometry("1024x700")
        self.resizable(True, True)
        ctk.set_appearance_mode("dark")
        self.platform_var = tk.StringVar(value="Android")

        self.log_manager = LogManager()
        self.create_main_layout()
        self.log_manager.set_log_widget(self.log_box)
        self.log_manager.log("--- Application Started ---")
        self.detect_devices()

    def create_main_layout(self):
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        main_container.grid_rowconfigure(2, weight=1) # Log box row
        main_container.grid_columnconfigure(0, weight=1)

        # Top bar for global controls
        top_bar = ctk.CTkFrame(main_container, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        title_label = ctk.CTkLabel(top_bar, text="Mobile Device Toolkit", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.pack(side="left", padx=10)

        settings_button = ctk.CTkButton(top_bar, text="⚙️ Settings", width=100, command=self.open_settings)
        settings_button.pack(side="right", padx=10, pady=5)

        # Tab View
        self.tab_view = ctk.CTkTabview(main_container)
        self.tab_view.grid(row=1, column=0, sticky="nsew")
        self.tab_view.add("Device")
        self.tab_view.add("Ducky Payloads")
        self.tab_view.add("User Profile")
        self.tab_view.add("Firmware Flasher")

        # --- Create Device Tab ---
        self.create_device_tab_widgets(self.tab_view.tab("Device"))

        # --- Create Ducky Payload Tab ---
        ducky_tab_frame = self.tab_view.tab("Ducky Payloads")
        self.ducky_tab = DuckyPayloadTab(ducky_tab_frame, log_callback=self.log_manager.log, get_tool_path=get_tool_path)
        self.ducky_tab.pack(fill="both", expand=True)

        # --- Create User Profile Tab ---
        profile_tab_frame = self.tab_view.tab("User Profile")
        self.profile_tab = UserProfileTab(profile_tab_frame, log_callback=self.log_manager.log)
        self.profile_tab.pack(fill="both", expand=True)

        # --- Create Firmware Flasher Tab ---
        firmware_tab_frame = self.tab_view.tab("Firmware Flasher")
        self.firmware_tab = FirmwareFlasherTab(firmware_tab_frame, log_callback=self.log_manager.log)
        self.firmware_tab.pack(fill="both", expand=True)

        # --- Log Output Box (Global) ---
        log_frame = ctk.CTkFrame(main_container)
        log_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        log_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(log_frame, text="Log Output:").pack(anchor="w", padx=10)
        self.log_box = ctk.CTkTextbox(log_frame, height=150, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def create_device_tab_widgets(self, master_frame):
        # Platform dropdown
        platform_frame = ctk.CTkFrame(master_frame)
        platform_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(platform_frame, text="Platform:").pack(side="left", padx=(0,5))
        platform_menu = ctk.CTkOptionMenu(platform_frame, variable=self.platform_var, values=["Android", "iOS", "USB-only", "Jailbroken"], command=lambda _: self.detect_devices())
        platform_menu.pack(side="left")

        # Device Info Panel
        self.device_info_frame = ctk.CTkFrame(master_frame)
        self.device_info_frame.pack(fill="x", padx=10, pady=5)
        self.device_info_labels = {}
        for label in ["Device Name", "Model", "Serial/UDID", "Status"]:
            row = ctk.CTkFrame(self.device_info_frame)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=label+":", width=120, anchor="w").pack(side="left")
            val = ctk.CTkLabel(row, text="-")
            val.pack(side="left")
            self.device_info_labels[label] = val

        # Payload Editor
        payload_frame = ctk.CTkFrame(master_frame)
        payload_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(payload_frame, text="Payload Editor:").pack(anchor="w")
        self.payload_box = ctk.CTkTextbox(payload_frame, height=6)
        self.payload_box.pack(fill="x", pady=2)
        btn_row = ctk.CTkFrame(payload_frame)
        btn_row.pack(fill="x")
        ctk.CTkButton(btn_row, text="Save Payload", command=self.save_payload).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="Run Payload", command=self.run_payload).pack(side="left", padx=2)

    def detect_devices(self):
        platform = self.platform_var.get()
        self.log_manager.log(f"Detecting devices for platform: {platform}")
        info = {"Device Name": "-", "Model": "-", "Serial/UDID": "-", "Status": "Offline"}
        if platform == "Android":
            result = detect_android_devices()
            if result:
                info.update(result)
        elif platform == "iOS":
            result = detect_ios_devices()
            if result:
                info.update(result)
        for k, v in info.items():
            self.device_info_labels[k].configure(text=v)

    def save_payload(self):
        payload = self.payload_box.get("1.0", "end").strip()
        if not payload:
            self.log_manager.log("[Error] Payload is empty.")
            return
        path = resource_path(os.path.join("payloads", "payload.txt"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload)
        self.log_manager.log(f"[Info] Payload saved to {path}")

    def run_payload(self):
        payload = self.payload_box.get("1.0", "end").strip()
        if not payload:
            self.log_manager.log("[Error] No payload to run.")
            return
        self.log_manager.log(f"[Simulated] Would execute payload: {payload}")

    def open_settings(self):
        """Opens the settings dialog window."""
        if not hasattr(self, 'settings_window') or not self.settings_window.winfo_exists():
            self.settings_window = SettingsDialog(self)
            self.log_manager.log("[Info] Settings window opened.")
            self.settings_window.wait_window() # This makes it modal and waits
            self.log_manager.log("[Info] Settings window closed. New paths will be used on next detection.")
        else:
            self.settings_window.focus() # Bring to front if already open

if __name__ == "__main__":
    app = MobileDeviceToolkitApp()
    app.mainloop()
