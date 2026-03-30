import sys
import os

def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource, which works for development
    and for the PyInstaller --onefile bundle.
    """
    try:
        # PyInstaller creates a temp folder and stores its path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Not running in a bundle, so it's in the project root
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)