"""System tray icon + context menu."""
from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from .. import constants


class AppTrayIcon(QSystemTrayIcon):
    def __init__(self, icon: QIcon, parent=None):
        super().__init__(icon, parent)
        self.setToolTip(constants.APP_DISPLAY_NAME)

        self.menu = QMenu()
        self.show_action = self.menu.addAction("Show Dashboard")
        self.refresh_action = self.menu.addAction("Refresh Now")
        self.settings_action = self.menu.addAction("Settings…")
        self.menu.addSeparator()
        self.quit_action = self.menu.addAction("Quit")

        self.setContextMenu(self.menu)

    def set_state(self, state_name: str) -> None:
        title = f"{state_name} Concert Tracker" if state_name else constants.APP_DISPLAY_NAME
        self.setToolTip(title)
