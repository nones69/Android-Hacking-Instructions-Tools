import os
import subprocess
import threading
from device_detector import get_tool_path
import zipfile
import tarfile

class FirmwareFlasher:
    """Handles the logic for executing firmware flashing commands."""
    def __init__(self, log_callback):
        self.log = log_callback

    def flash_firmware_threaded(self, filepath, method, finished_callback=None):
        """Starts the flashing process in a new thread."""
        thread = threading.Thread(
            target=self._flash_worker,
            args=(filepath, method, finished_callback),
            daemon=True
        )
        thread.start()

    def extract_firmware_threaded(self, filepath, finished_callback):
        """Starts the extraction process in a new thread."""
        thread = threading.Thread(
            target=self._extract_worker,
            args=(filepath, finished_callback),
            daemon=True
        )
        thread.start()

    def _extract_worker(self, filepath, finished_callback):
        """The worker function that extracts an archive."""
        self.log(f"--- Starting Extraction ---")
        self.log(f"File: {os.path.basename(filepath)}")

        if not os.path.exists(filepath):
            self.log(f"[Error] File not found: {filepath}")
            self.log("--- Extraction Failed ---")
            if finished_callback: finished_callback()
            return

        archive_name = os.path.splitext(os.path.basename(filepath))[0]
        extract_path = os.path.join(os.path.dirname(filepath), archive_name)
        
        try:
            os.makedirs(extract_path, exist_ok=True)
            self.log(f"Extracting to: {extract_path}")

            if filepath.lower().endswith('.zip'):
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            elif filepath.lower().endswith(('.tar', '.tar.gz', '.tgz')):
                with tarfile.open(filepath, 'r:*') as tar_ref:
                    tar_ref.extractall(path=extract_path)
            self.log(f"--- Extraction Finished ---")
        except Exception as e:
            self.log(f"[Error] An error occurred during extraction: {e}")
            self.log("--- Extraction Failed ---")
        finally:
            if finished_callback: finished_callback()

    def _flash_worker(self, filepath, method, finished_callback=None):
        """The worker function that executes the flash command."""
        self.log(f"--- Starting Firmware Flash ---")
        self.log(f"File: {os.path.basename(filepath)}")
        self.log(f"Method: {method}")

        if not os.path.exists(filepath):
            self.log(f"[Error] File not found: {filepath}")
            self.log("--- Flash Failed ---")
            if finished_callback:
                finished_callback()
            return

        command = []
        if method == "ADB Sideload":
            tool_path = get_tool_path("adb")
            command = [tool_path, "sideload", filepath]
        elif method == "Fastboot Flash":
            tool_path = get_tool_path("fastboot")
            command = [tool_path, "update", filepath]
        else:
            self.log(f"[Error] Flashing method '{method}' is not implemented.")
            self.log("--- Flash Failed ---")
            if finished_callback:
                finished_callback()
            return

        try:
            self.log(f"Executing: {' '.join(command)}")
            
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            else:
                startupinfo = None

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', startupinfo=startupinfo)

            for line in iter(process.stdout.readline, ''):
                self.log(f"> {line.strip()}")
            
            process.wait()
            self.log(f"--- Flash process finished with exit code {process.returncode} ---")

        except FileNotFoundError:
            self.log(f"[Error] Command failed: '{command[0]}' not found. Please check PATH or configure it in Settings.")
        except Exception as e:
            self.log(f"[Error] An unexpected error occurred: {e}")
        finally:
            if finished_callback:
                finished_callback()