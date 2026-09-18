"""Dark theme stylesheet + the app icon (shared by the window, taskbar, and the built .exe)."""
from __future__ import annotations

import os

from PySide6.QtGui import QIcon

BG = "#0d0d0f"
CARD_BG = "#18181b"
BORDER = "#2a2a2e"
TEXT = "#f5f5f5"
SUBTEXT = "#9a9aa0"
ACCENT = "#3ecf8e"
PILL_BG = "#1f3d31"

STYLESHEET = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Segoe UI';
    font-size: 13px;
}}
QFrame#card {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QLabel#title {{
    font-size: 17px;
    font-weight: 600;
}}
QLabel#subtitle, QLabel#footerLabel, QLabel#disclaimer {{
    color: {SUBTEXT};
    font-size: 11px;
}}
QLabel#statValue {{
    font-size: 30px;
    font-weight: 700;
}}
QLabel#statLabel {{
    color: {SUBTEXT};
    font-size: 10px;
}}
QLabel#sectionHeader {{
    font-size: 14px;
    font-weight: 600;
}}
QLabel#activeBadge {{
    color: {ACCENT};
    background-color: {PILL_BG};
    border-radius: 9px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}}
QLabel#newBadge {{
    color: {ACCENT};
    background-color: {PILL_BG};
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 600;
}}
QPushButton#linkButton, QPushButton#refreshButton {{
    background-color: transparent;
    border: none;
    color: {SUBTEXT};
    font-size: 14px;
}}
QPushButton#linkButton:hover, QPushButton#refreshButton:hover {{
    color: {ACCENT};
}}
QScrollArea {{
    border: none;
}}
"""


_ICON_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "resources", "app_icon.ico"))
_app_icon: QIcon | None = None


def build_app_icon(size: int = 64) -> QIcon:
    global _app_icon
    if _app_icon is None:
        _app_icon = QIcon(_ICON_PATH)
    return _app_icon
