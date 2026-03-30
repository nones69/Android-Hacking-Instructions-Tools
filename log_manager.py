import logging
import os
from logging.handlers import RotatingFileHandler
import datetime

LOG_DIR = "logs"

class LogManager:
    """A centralized logger for the application."""
    def __init__(self):
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        log_filename = os.path.join(LOG_DIR, f"log_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")

        self.logger = logging.getLogger("MobileDeviceToolkitLogger")
        self.logger.setLevel(logging.INFO)

        # Prevent adding duplicate handlers if this class is instantiated again
        if not self.logger.handlers:
            # This will create up to 5 log files, each up to 5MB in size.
            file_handler = RotatingFileHandler(
                log_filename, maxBytes=1024*1024*5, backupCount=5, encoding='utf-8'
            )
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        self.log_widget = None

    def set_log_widget(self, widget):
        """Registers the GUI widget to display logs."""
        self.log_widget = widget

    def log(self, message: str):
        """Logs a message to the file and optionally to the GUI widget."""
        self.logger.info(message)

        if self.log_widget:
            def _update_widget():
                self.log_widget.configure(state="normal")
                self.log_widget.insert("end", message + "\n")
                self.log_widget.see("end")
                self.log_widget.configure(state="disabled")
            
            self.log_widget.after(0, _update_widget)