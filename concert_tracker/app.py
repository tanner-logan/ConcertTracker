"""Application entry point: wires together config, tray icon, window and scheduler."""
from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from . import config as config_module
from . import constants, storage
from .logging_setup import setup_logging
from .models import RefreshResult, ShowMatch
from .services.refresh_worker import RefreshWorker
from .ui.main_window import MainWindow
from .ui.settings_dialog import SettingsDialog
from .ui.theme import STYLESHEET, build_app_icon
from .ui.tray import AppTrayIcon


def _register_windows_app_id() -> None:
    """Give the process its own taskbar identity so Windows shows our icon, not python.exe's."""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            f"{constants.ORG_NAME}.{constants.APP_NAME}"
        )
    except Exception:
        pass


class ConcertTrackerApp:
    def __init__(self):
        setup_logging()
        _register_windows_app_id()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setStyleSheet(STYLESHEET)
        self.app.setWindowIcon(build_app_icon())

        self.config = config_module.load_config()
        self.window = MainWindow()
        self.tray = AppTrayIcon(build_app_icon())
        self.worker: Optional[RefreshWorker] = None
        self._tray_notice_shown = False

        self._load_cached_data()
        self._wire_signals()
        self._apply_state_labels()

        self.timer = QTimer()
        self.timer.timeout.connect(self.start_refresh)

        self.tray.show()

        if not self.config.is_complete:
            self._open_settings(first_run=True)
        else:
            self._restart_timer()
            self.start_refresh()

        self.window.show()

    def run(self) -> int:
        return self.app.exec()

    def _wire_signals(self) -> None:
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show_action.triggered.connect(self._show_window)
        self.tray.refresh_action.triggered.connect(self.start_refresh)
        self.tray.settings_action.triggered.connect(lambda: self._open_settings(first_run=False))
        self.tray.quit_action.triggered.connect(self.app.quit)
        self.window.refresh_button.clicked.connect(self.start_refresh)
        self.window.hidden_to_tray.connect(self._on_hidden_to_tray)

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.Trigger:
            self._show_window()

    def _show_window(self) -> None:
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()

    def _on_hidden_to_tray(self) -> None:
        if self._tray_notice_shown:
            return
        self._tray_notice_shown = True
        self.tray.showMessage(
            self._display_name(),
            "Still running in the background. Right-click the tray icon to reopen or quit.",
            build_app_icon(),
            4000,
        )

    def _display_name(self) -> str:
        if self.config.state_code:
            return f"{constants.state_name_for(self.config.state_code)} Concert Tracker"
        return constants.APP_DISPLAY_NAME

    def _apply_state_labels(self) -> None:
        state_name = constants.state_name_for(self.config.state_code) if self.config.state_code else ""
        self.window.set_state(state_name)
        self.tray.set_state(state_name)

    def _load_cached_data(self) -> None:
        cached = storage.load_cache()
        matches = [
            ShowMatch(
                artist_name=m["artist_name"],
                venue_name=m["venue_name"],
                city=m["city"],
                event_date=m["event_date"],
                event_url=m["event_url"],
                image_url=m.get("image_url"),
            )
            for m in cached.get("matches", [])
        ]
        result = RefreshResult(
            artist_count=cached.get("artist_count", 0),
            matches=matches,
            checked_at=cached.get("checked_at", ""),
        )
        self.window.apply_result(result)

    def _restart_timer(self) -> None:
        self.timer.stop()
        interval_ms = self.config.check_interval_hours * 60 * 60 * 1000
        self.timer.start(interval_ms)

    def _open_settings(self, first_run: bool) -> None:
        if first_run:
            self._show_window()
            QMessageBox.information(
                self.window,
                "Welcome",
                "Sign in with your own Spotify account, choose the state you want show alerts for, "
                "and enter your Ticketmaster API key to get started.",
            )
        dialog = SettingsDialog(self.config, self.window)
        if dialog.exec():
            self.config = config_module.load_config()
            self._apply_state_labels()
            self._restart_timer()
            self.start_refresh()

    def start_refresh(self) -> None:
        if self.worker and self.worker.isRunning():
            return
        if not self.config.is_complete:
            return

        self.window.set_status("Refreshing")
        self.window.show_loading("Refreshing…")

        self.worker = RefreshWorker(
            self.config.spotify_client_id,
            self.config.spotify_redirect_uri,
            config_module.get_ticketmaster_api_key(),
            self.config.state_code,
            self.config.include_followed_playlists,
        )
        self.worker.progress.connect(self.window.show_loading)
        self.worker.finished_ok.connect(self._on_refresh_finished)
        self.worker.failed.connect(self._on_refresh_failed)
        self.worker.start()

    def _on_refresh_finished(self, result: RefreshResult) -> None:
        self.window.set_status("Active")
        self.window.apply_result(result)
        self.tray.showMessage(
            self._display_name(),
            f"{len(result.matches)} upcoming show(s) for your artists.",
            build_app_icon(),
            5000,
        )

    def _on_refresh_failed(self, message: str) -> None:
        self.window.set_status("Error")
        self.window.show_loading("Refresh failed")
        self.tray.showMessage(
            self._display_name(),
            f"Refresh failed: {message}",
            QSystemTrayIcon.Warning,
            6000,
        )


def main() -> int:
    app = ConcertTrackerApp()
    return app.run()
