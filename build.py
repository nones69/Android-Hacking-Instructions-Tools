import PyInstaller.__main__
import os
import shutil
import sys
import platform
from pathlib import Path

# --- Configuration ---
APP_NAME = "MobileDeviceToolkit"
MAIN_SCRIPT = Path("src") / "MobileDeviceToolkit" / "__main__.py"
ICON_PATH = Path("assets") / "icon.ico"
ASSETS_TO_BUNDLE = {
    "tools": "tools",
    "payloads": "payloads",
}

# --- Path Constants ---
PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / f"{APP_NAME}.spec"

def verify_environment():
    """Checks if the build environment is Windows 64-bit."""
    print("--- Verifying Build Environment ---")
    if not (sys.platform == "win32" and platform.architecture()[0] == "64bit"):
        print("Error: This build script is configured for Windows 64-bit.")
        print(f"You are running on: {sys.platform} ({platform.architecture()[0]})")
        sys.exit(1)
    print("Environment: Windows 64-bit... OK")

def pre_build_checks():
    """Performs checks for required files and directories before building."""
    print("\n--- Pre-build Checks ---")
    if not MAIN_SCRIPT.exists():
        print(f"Error: Main script '{MAIN_SCRIPT}' not found. Have you restructured the project as recommended?")
        sys.exit(1)

    for asset_dir in ASSETS_TO_BUNDLE:
        if not (PROJECT_ROOT / asset_dir).exists():
            print(f"Warning: '{asset_dir}' directory not found. Some features may be missing.")

    if not ICON_PATH.exists():
        print(f"Warning: Icon file at '{ICON_PATH}' not found. A default icon will be used.")
        return False
    return True

def clean_previous_builds():
    """Removes artifacts from previous builds."""
    print("\n--- Cleaning up previous build artifacts ---")
    for folder in [BUILD_DIR, DIST_DIR]:
        if folder.exists():
            print(f"Removing directory: {folder}")
            shutil.rmtree(folder)
    if SPEC_FILE.exists():
        print(f"Removing file: {SPEC_FILE}")
        SPEC_FILE.unlink()

def run_pyinstaller(has_icon: bool):
    """Constructs and runs the PyInstaller command."""
    pyinstaller_args = [
        str(MAIN_SCRIPT),
        f'--name={APP_NAME}',
        '--onefile',
        '--windowed',
        # Explicitly include modules that PyInstaller might miss.
        '--hidden-import=pyautogui',
        '--hidden-import=pywin32',  # pyautogui has dependencies on this
    ]

    # Add asset directories to the bundle.
    for src, dest in ASSETS_TO_BUNDLE.items():
        if (PROJECT_ROOT / src).exists():
            pyinstaller_args.append(f'--add-data={src}{os.pathsep}{dest}')

    if has_icon:
        pyinstaller_args.append(f'--icon={ICON_PATH}')

    print("\n--- Starting PyInstaller build ---")
    print(f"Arguments: {' '.join(pyinstaller_args)}")

    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n--- Build Successful ---")
        print(f"The executable can be found in the '{DIST_DIR.resolve()}' folder.")
    except Exception as e:
        print(f"\n--- Build Failed ---")
        print(f"An error occurred during the build process: {e}")
        sys.exit(1)

def main():
    """Main build script execution."""
    verify_environment()
    has_icon = pre_build_checks()
    clean_previous_builds()
    run_pyinstaller(has_icon)

if __name__ == "__main__":
    main()