import subprocess
import os

# To prevent console windows from flashing on Windows when running subprocess
if os.name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
else:
    startupinfo = None

def _run_command(command):
    """A helper to run commands without a flashing console window on Windows."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )
        return result.stdout.strip()
    except FileNotFoundError:
        # The command (e.g., 'adb') was not found.
        return None
    except subprocess.CalledProcessError:
        # The command returned a non-zero exit code (e.g., no device found).
        return ""
    except Exception as e:
        print(f"An unexpected error occurred in _run_command: {e}")
        return ""

def detect_android_devices():
    """Detects connected Android devices via ADB and gets their info."""
    output = _run_command(["adb", "devices"])
    if output is None:
        return {"Status": "Error: ADB not found in PATH"}

    lines = output.strip().split('\n')
    # Find the first line that indicates a connected and authorized device
    device_line = next((line for line in lines[1:] if '\tdevice' in line), None)

    if not device_line:
        return {"Device Name": "-", "Model": "-", "Serial/UDID": "-", "Status": "Offline"}

    serial = device_line.split('\t')[0]
    
    # Fetch additional properties from the device
    def get_prop(prop_name):
        return _run_command(["adb", "-s", serial, "shell", "getprop", prop_name])

    model = get_prop("ro.product.model") or "Unknown Model"
    brand = get_prop("ro.product.brand") or "Unknown Brand"
    
    return {
        "Device Name": f"{brand.capitalize()} {model}",
        "Model": model,
        "Serial/UDID": serial,
        "Status": "Online"
    }

def detect_ios_devices():
    """Detects connected iOS devices via libimobiledevice."""
    # idevice_id is the most common tool for getting the UDID.
    output = _run_command(["idevice_id", "-l"])
    if output is None:
        return {"Status": "Error: libimobiledevice not found in PATH"}

    udids = [udid for udid in output.strip().split('\n') if udid]
    if not udids:
        return {"Device Name": "-", "Model": "-", "Serial/UDID": "-", "Status": "Offline"}

    udid = udids[0] # Use the first device found

    # Fetch additional properties using other libimobiledevice tools
    device_name = _run_command(["idevicename", "-u", udid]) or "Unknown Name"
    # ProductType gives a model identifier like 'iPhone13,2'
    model_info = _run_command(["ideviceinfo", "-u", udid, "-k", "ProductType"]) or "Unknown Model"

    return {
        "Device Name": device_name,
        "Model": model_info,
        "Serial/UDID": udid,
        "Status": "Online"
    }