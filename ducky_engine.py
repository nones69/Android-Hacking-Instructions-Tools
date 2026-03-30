import pyautogui
import time
import subprocess
import os

def run_ducky_script_on_desktop(script_content, log_callback):
    """
    Parses and executes a Ducky Script on the local desktop using pyautogui.
    """
    log_callback("--- Starting Ducky Script on Desktop ---")
    try:
        for line in script_content.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith("REM"):
                continue

            log_callback(f"Executing: {line}")
            parts = line.split(" ", 1)
            command = parts[0].upper()
            argument = parts[1] if len(parts) > 1 else ""

            if command == "DELAY":
                time.sleep(int(argument) / 1000)
            elif command == "STRING":
                pyautogui.write(argument, interval=0.01)
            elif command == "ENTER":
                pyautogui.press("enter")
            elif command == "GUI":
                if argument:
                    pyautogui.hotkey("win", argument.lower())
                else:
                    pyautogui.press("win")
            elif command in ("SHIFT", "CTRL", "ALT", "ALTGR"):
                pyautogui.keyDown(command.lower())
                pyautogui.keyUp(command.lower())
            elif command in ("UPARROW", "DOWNARROW", "LEFTARROW", "RIGHTARROW"):
                arrow_map = {
                    "UPARROW": "up",
                    "DOWNARROW": "down",
                    "LEFTARROW": "left",
                    "RIGHTARROW": "right",
                }
                pyautogui.press(arrow_map[command])
            else:
                pyautogui.press(command.lower())
    except Exception as e:
        log_callback(f"[Error] Ducky Script execution failed: {e}")
    finally:
        log_callback("--- Ducky Script on Desktop Finished ---")

def convert_ducky_to_shell_commands(script_content):
    """
    Converts a Ducky Script into a list of equivalent shell commands for ADB.
    """
    shell_commands = []
    key_map = {
        "ENTER": "66", "BACKSPACE": "67", "TAB": "61", "SPACE": "62",
        "UPARROW": "19", "DOWNARROW": "20", "LEFTARROW": "21", "RIGHTARROW": "22",
        "HOME": "3", "END": "123", "ESC": "111",
        "DELETE": "112", "PAGEUP": "92", "PAGEDOWN": "93",
    }

    for line in script_content.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith("REM"):
            continue

        parts = line.split(" ", 1)
        command = parts[0].upper()
        argument = parts[1] if len(parts) > 1 else ""

        if command == "DELAY":
            milliseconds = int(argument)
            shell_commands.append(f"sleep {milliseconds / 1000}")
        elif command == "STRING":
            # Sanitize text for shell command
            sanitized_text = argument.replace("'", "'\\''")
            shell_commands.append(f"input text '{sanitized_text}'")
        elif command in key_map:
            shell_commands.append(f"input keyevent {key_map[command]}")
        else:
            # If unknown command, just log a comment in output
            shell_commands.append(f"# Unsupported Ducky command for ADB: {line}")

    return shell_commands

def run_adb_payload(shell_commands, adb_executable_path, log_callback):
    """
    Executes a list of adb shell commands on a connected Android device.
    """
    log_callback("--- Starting ADB Payload Execution ---")
    try:
        for shell_cmd in shell_commands:
            if shell_cmd.startswith("#"):
                log_callback(f"Skipping: {shell_cmd}")
                continue  # Skip comments

            # Construct the full command with the correct adb path
            full_command = [adb_executable_path, "shell"] + shell_cmd.split()
            
            log_callback(f"Running: {' '.join(full_command)}")
            
            startupinfo = subprocess.STARTUPINFO() if os.name == 'nt' else None
            if startupinfo:
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(full_command, capture_output=True, text=True, check=False, startupinfo=startupinfo)
            log_callback(result.stdout.strip() if result.stdout else "[OK]")
            if result.stderr:
                log_callback(f"[stderr] {result.stderr.strip()}")
    except Exception as e:
        log_callback(f"[Error] ADB payload failed: {e}")
    finally:
        log_callback("--- ADB Payload Execution Finished ---")
