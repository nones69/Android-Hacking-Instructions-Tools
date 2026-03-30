
# Mobile Device Toolkit (MDT)

**Platform:** Windows 11/10 64-bit OS (x64) only. Designed and tested for modern Windows desktop environments. For .exe builds, use PyInstaller (see below).

## Features
- Android & iOS device detection
- Rubber Ducky payload engine (Android, iOS, Desktop)
- Real-time push to Android via ADB shell
- Wireless "Remote Ducky over Wi-Fi" deployment
- Jailbroken iOS compatibility (SSH + shell payloads)
- Script database for payloads
- Real-time execution logs


## Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Launch the app: `python app/main.py`
3. Use the "Ducky Payloads" tab to load, edit, and run .duck scripts on Android, iOS, or Desktop.

### Windows Executable (.exe) Build
To build a standalone Windows 64-bit executable:
1. Install PyInstaller: `pip install pyinstaller`
2. Run: `pyinstaller --noconsole --onefile --icon=assets/icon.ico app/main.py`
3. The .exe will be in the `dist/` folder. Run on Windows 11/10 64-bit only.

## Sample Payload
See `payloads/hello_world.duck` for a test script.

## Legal & Ethical Notice
This tool is for authorized device management, repair, and research only. Use responsibly and comply with all applicable laws.
