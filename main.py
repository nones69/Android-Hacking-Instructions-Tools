#!/usr/bin/env python3
"""
Mobile Device Toolkit - Main Entry Point
"""

import os
import sys
import configparser
import traceback
from pathlib import Path

# Set up base directory for resource paths
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Running in development environment
    BASE_DIR = Path(__file__).parent.parent

# Add the base directory to the path for imports
sys.path.insert(0, str(BASE_DIR))

# Import after path setup
import customtkinter as ctk
from app.gui.main_window import App
from app.utils.logger import setup_logger, get_logger

def load_config():
    """Load configuration from config.ini"""
    config = configparser.ConfigParser()
    config_path = BASE_DIR / 'config.ini'
    
    if not config_path.exists():
        # Create default config if it doesn't exist
        from app.utils.default_config import create_default_config
        create_default_config(config_path)
    
    config.read(config_path)
    return config

def setup_directories():
    """Ensure all required directories exist"""
    directories = [
        'logs',
        'firmware_repo',
        'payloads',
        'payloads/ducky',
        'drivers'
    ]
    
    for directory in directories:
        dir_path = BASE_DIR / directory
        dir_path.mkdir(exist_ok=True)

def main():
    """Main entry point for the application"""
    # Setup directories
    setup_directories()
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    log_level = config.get('General', 'log_level', fallback='INFO')
    log_path = BASE_DIR / 'logs' / 'mdt.log'
    setup_logger(log_path, log_level)
    
    log = get_logger(__name__)
    log.info("Starting Mobile Device Toolkit")
    
    try:
        # Set appearance mode from config
        theme = config.get('GUI', 'theme', fallback='dark')
        ctk.set_appearance_mode(theme)
        
        # Launch the application
        app = App(config)
        app.mainloop()
        
    except Exception as e:
        log.error(f"Unhandled exception: {e}")
        log.error(traceback.format_exc())
        
        # Show error dialog if GUI is available
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Error", 
                f"An unexpected error occurred:\n{e}\n\nSee logs for details."
            )
            root.destroy()
        except:
            # If even that fails, just print to console
            print(f"CRITICAL ERROR: {e}")
            print(traceback.format_exc())
    
    log.info("Application shutdown complete")

if __name__ == "__main__":
    main()