import os
import requests
import threading

class DownloadManager:
    """Handles downloading files in a separate thread."""
    def __init__(self):
        self.firmware_dir = "firmware"
        if not os.path.exists(self.firmware_dir):
            os.makedirs(self.firmware_dir)
        self.cancellation_event = threading.Event()

    def cancel_download(self):
        """Signals the download worker to stop."""
        self.cancellation_event.set()

    def download_file_threaded(self, url, progress_callback, log_callback, finished_callback):
        """Starts the download process in a new thread."""
        self.cancellation_event.clear() # Reset for the new download
        thread = threading.Thread(
            target=self._download_worker,
            args=(url, progress_callback, log_callback, finished_callback),
            daemon=True
        )
        thread.start()

    def _download_worker(self, url, progress_callback, log_callback, finished_callback):
        """The worker function that executes the download."""
        dest_path = ""
        try:
            filename = url.split('/')[-1]
            if not filename:
                filename = "downloaded_firmware.zip" # Default filename
            
            dest_path = os.path.join(self.firmware_dir, filename)
            log_callback(f"[Info] Starting download from: {url}")
            log_callback(f"[Info] Saving to: {dest_path}")

            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                bytes_downloaded = 0
                
                with open(dest_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if self.cancellation_event.is_set():
                            log_callback("[Info] Download cancelled by user.")
                            break
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        if total_size > 0:
                            progress = (bytes_downloaded / total_size) * 100
                            progress_callback(progress)
            
            if not self.cancellation_event.is_set():
                log_callback(f"[Success] Download finished: {filename}")
                progress_callback(100)

        except requests.exceptions.RequestException as e:
            log_callback(f"[Error] Download failed: {e}")
            progress_callback(0)
        except Exception as e:
            log_callback(f"[Error] An unexpected error occurred during download: {e}")
            progress_callback(0)
        finally:
            # If cancellation was triggered, clean up the partial file
            if self.cancellation_event.is_set() and dest_path and os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                    log_callback(f"[Info] Removed partial file: {os.path.basename(dest_path)}")
                except OSError as e:
                    log_callback(f"[Error] Could not remove partial file: {e}")
            finished_callback()