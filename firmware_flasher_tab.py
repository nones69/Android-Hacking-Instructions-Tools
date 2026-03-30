import customtkinter as ctk
from tkinter import filedialog
import os
from firmware_flasher import FirmwareFlasher
from download_manager import DownloadManager

class FirmwareFlasherTab(ctk.CTkFrame):
    """The UI for the Firmware Flasher tab."""
    def __init__(self, master, log_callback):
        super().__init__(master)
        self.log = log_callback
        self.selected_filepath = None
        self.flasher = FirmwareFlasher(log_callback=self.log)
        self.downloader = DownloadManager()

        self.grid_columnconfigure(0, weight=1, minsize=220) # File browser column
        self.grid_columnconfigure(1, weight=3)              # Main controls column

        # --- Left Panel: Firmware Browser ---
        browser_container = ctk.CTkFrame(self)
        browser_container.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        browser_container.grid_rowconfigure(1, weight=1)
        browser_container.grid_columnconfigure(0, weight=1)

        browser_top_frame = ctk.CTkFrame(browser_container, fg_color="transparent")
        browser_top_frame.grid(row=0, column=0, padx=5, pady=(5,0), sticky="ew")
        browser_top_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(browser_top_frame, text="Firmware Files", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        refresh_button = ctk.CTkButton(browser_top_frame, text="🔄", width=30, command=self.populate_firmware_browser)
        refresh_button.grid(row=0, column=1, sticky="e")

        self.file_browser_frame = ctk.CTkScrollableFrame(browser_container)
        self.file_browser_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # --- Right Panel: Controls and Log ---
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=0, column=1, padx=(5, 10), pady=0, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)

        # --- File Selection ---
        file_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        file_frame.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        file_frame.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(file_frame, text="No firmware file selected.")
        self.file_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        browse_button = ctk.CTkButton(file_frame, text="Browse...", command=self.browse_for_file)
        browse_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")

        # --- Download Section ---
        download_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        download_frame.grid(row=1, column=0, pady=5, sticky="ew")
        download_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(download_frame, placeholder_text="Enter firmware URL to download...")
        self.url_entry.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # Container for download/cancel buttons
        dl_button_container = ctk.CTkFrame(download_frame, fg_color="transparent")
        dl_button_container.grid(row=0, column=1, padx=10, pady=5)

        self.download_button = ctk.CTkButton(download_frame, text="Download", command=self.start_download)
        self.download_button.pack()

        self.cancel_button = ctk.CTkButton(download_frame, text="Cancel", command=self.cancel_download, fg_color="tomato")

        self.progress_bar = ctk.CTkProgressBar(download_frame)
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 5), sticky="ew")
        self.progress_bar.set(0)

        # --- Controls ---
        controls_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        controls_frame.grid(row=2, column=0, pady=5, sticky="ew")
        controls_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(controls_frame, text="Method:").grid(row=0, column=0, padx=10, pady=5)
        self.method_combo = ctk.CTkComboBox(controls_frame, values=["ADB Sideload", "Fastboot Flash"])
        self.method_combo.grid(row=0, column=1, padx=10, pady=5)

        self.extract_button = ctk.CTkButton(controls_frame, text="Extract Archive", command=self.start_extraction)
        self.extract_button.grid(row=0, column=2, padx=10, pady=5)
        self.extract_button.configure(state="disabled")

        self.flash_button = ctk.CTkButton(controls_frame, text="Start Flashing", command=self.start_flashing)
        self.flash_button.grid(row=0, column=3, padx=10, pady=5, sticky="e")
        self.flash_button.configure(state="disabled")

        self.populate_firmware_browser()

    def browse_for_file(self):
        initial_dir = self.downloader.firmware_dir
        filetypes = (("Firmware Files", "*.zip *.img *.bin *.tar *.md5 *.ipsw"), ("All files", "*.*"))
        filepath = filedialog.askopenfilename(title="Select Firmware File", filetypes=filetypes, initialdir=initial_dir)
        if filepath:
            self.selected_filepath = filepath
            self.file_label.configure(text=os.path.basename(filepath))
            self.log(f"[Info] Selected file: {filepath}")
            self.update_button_states()

    def populate_firmware_browser(self):
        """Reads the firmware directory and populates the file browser."""
        for widget in self.file_browser_frame.winfo_children():
            widget.destroy()

        firmware_dir = self.downloader.firmware_dir
        if not os.path.exists(firmware_dir):
            ctk.CTkLabel(self.file_browser_frame, text="Firmware directory not found.").pack(padx=5, pady=5, anchor="w")
            return

        try:
            files = sorted(os.listdir(firmware_dir), key=lambda s: s.lower())
            if not files:
                ctk.CTkLabel(self.file_browser_frame, text="No files found.").pack(padx=5, pady=5, anchor="w")
                return

            for filename in files:
                filepath = os.path.join(firmware_dir, filename)
                icon = "📁" if os.path.isdir(filepath) else "📄"
                button = ctk.CTkButton(self.file_browser_frame, text=f"{icon} {filename}",
                                       fg_color="transparent", anchor="w",
                                       command=lambda p=filepath: self.select_file_from_browser(p))
                button.pack(fill="x", padx=2, pady=1)
        except Exception as e:
            self.log(f"[Error] Failed to read firmware directory: {e}")

    def select_file_from_browser(self, filepath):
        """Callback when a file is selected from the browser list."""
        if os.path.isfile(filepath):
            self.selected_filepath = filepath
            self.file_label.configure(text=

    def update_button_states(self):
        """Enables or disables buttons based on the currently selected file."""
        if not self.selected_filepath:
            self.extract_button.configure(state="disabled")
            return

        is_archive = self.selected_filepath.lower().endswith(('.zip', '.tar', '.tar.gz', '.tgz'))
        self.extract_button.configure(state="normal" if is_archive else "disabled")

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log("[Error] URL field is empty.")
            return
        self.download_button.configure(state="disabled", text="Downloading...")
        self.progress_bar.set(0)
        try:
            self.downloader.download_file_threaded(
                url,
                progress_callback=self.update_progress,
                log_callback=self.log,
                finished_callback=self.on_download_finished_with_validation
            )
        except Exception as e:
            self.log(f"[Error] Download failed: {e}")
            self.download_button.configure(state="normal", text="Download")

    def on_download_finished_with_validation(self):
        self.after(0, self._validate_downloaded_file)

    def _validate_downloaded_file(self):
        self.download_button.configure(state="normal", text="Download")
        # Optionally, auto-select the most recent file in firmware_dir
        try:
            files = [os.path.join(self.downloader.firmware_dir, f) for f in os.listdir(self.downloader.firmware_dir)]
            files = [f for f in files if os.path.isfile(f)]
            if files:
                latest = max(files, key=os.path.getmtime)
                self.selected_filepath = latest
                self.file_label.configure(text=os.path.basename(latest))
                self.log(f"[Info] Downloaded and selected: {latest}")
            else:
                self.log("[Warning] Download finished, but no file found.")
        except Exception as e:
            self.log(f"[Error] Could not validate downloaded file: {e}")

    def update_progress(self, value):
        self.after(0, lambda: self.progress_bar.set(value / 100))

    def on_download_finished(self):
        self.after(0, lambda: self.download_button.configure(state="normal", text="Download"))

    def start_extraction(self):
        if not self.selected_filepath:
            self.log("[Error] No file selected for extraction.")
            return
        
        self.extract_button.configure(state="disabled", text="Extracting...")
        self.flasher.extract_firmware_threaded(
            self.selected_filepath,
            finished_callback=self.on_extraction_finished
        )

    def on_extraction_finished(self):
        self.after(0, lambda: self.extract_button.configure(state="normal", text="Extract Archive"))

    def start_flashing(self):
        if not self.selected_filepath:
            self.log("[Error] No firmware file has been selected.")
            return
        if not os.path.isfile(self.selected_filepath):
            self.log(f"[Error] Selected file does not exist: {self.selected_filepath}")
            return
        ext = os.path.splitext(self.selected_filepath)[1].lower()
        if ext not in [".zip", ".img", ".bin", ".tar", ".md5", ".ipsw"]:
            self.log(f"[Error] Unsupported firmware file type: {ext}")
            return
        self.flash_button.configure(state="disabled", text="Flashing...")
        method = self.method_combo.get()
        try:
            self.flasher.flash_firmware_threaded(self.selected_filepath, method)
        except Exception as e:
            self.log(f"[Error] Flashing failed to start: {e}")
            self.flash_button.configure(state="normal", text="Start Flashing")

    def log(self, message):
        def _update():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
            # Re-enable flash button on finish/failure
            if ("--- Flash process finished" in message or "--- Flash Failed ---" in message or
                "[Error]" in message or "[Warning]" in message):
                self.flash_button.configure(state="normal", text="Start Flashing")
            # Re-enable download button on error
            if "[Error] Download failed" in message or "[Warning] Download finished, but no file found." in message:
                self.download_button.configure(state="normal", text="Download")
        self.after(0, _update)