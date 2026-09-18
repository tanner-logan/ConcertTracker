"""Windows 'run at login' integration via the current-user Run registry key."""
from __future__ import annotations

import sys
import winreg

from . import constants

_RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def _launch_command() -> str:
    if getattr(sys, "frozen", False):
        # Running as a PyInstaller-built executable.
        return f'"{sys.executable}"'
    # Running from source: launch with pythonw so no console window appears.
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    return f'"{pythonw}" -m concert_alerts'


def is_autostart_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, constants.APP_NAME)
            return True
    except FileNotFoundError:
        return False


def enable_autostart() -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH) as key:
        winreg.SetValueEx(key, constants.APP_NAME, 0, winreg.REG_SZ, _launch_command())


def disable_autostart() -> None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, constants.APP_NAME)
    except FileNotFoundError:
        pass
