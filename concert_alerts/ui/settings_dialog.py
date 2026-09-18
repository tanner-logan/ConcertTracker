"""Dialog for entering API credentials and refresh/startup preferences."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
)

from .. import config as config_module
from .. import constants, startup


class SettingsDialog(QDialog):
    def __init__(self, config: config_module.AppConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Concert Alerts Settings")
        self.setMinimumWidth(420)
        self._config = config

        form = QFormLayout(self)

        self.client_id_edit = QLineEdit(config.spotify_client_id)
        self.client_id_edit.setPlaceholderText("Spotify app Client ID")
        form.addRow("Spotify Client ID", self.client_id_edit)

        self.redirect_uri_edit = QLineEdit(config.spotify_redirect_uri)
        form.addRow("Spotify Redirect URI", self.redirect_uri_edit)

        self.state_combo = QComboBox()
        self.state_combo.addItem("Select a state…", userData="")
        for code, name in sorted(constants.US_STATES, key=lambda s: s[1]):
            self.state_combo.addItem(f"{name} ({code})", userData=code)
        if config.state_code:
            index = self.state_combo.findData(config.state_code)
            if index >= 0:
                self.state_combo.setCurrentIndex(index)
        form.addRow("Notify me about shows in", self.state_combo)

        self.include_followed_check = QCheckBox("Also scan playlists you follow (not just ones you created)")
        self.include_followed_check.setChecked(config.include_followed_playlists)
        form.addRow(self.include_followed_check)

        self.ticketmaster_edit = QLineEdit(config_module.get_ticketmaster_api_key())
        self.ticketmaster_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Ticketmaster API Key", self.ticketmaster_edit)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(constants.MIN_CHECK_INTERVAL_HOURS, constants.MAX_CHECK_INTERVAL_HOURS)
        self.interval_spin.setValue(config.check_interval_hours)
        self.interval_spin.setSuffix(" hours")
        form.addRow("Check every", self.interval_spin)

        self.autostart_check = QCheckBox("Start automatically when Windows starts")
        self.autostart_check.setChecked(startup.is_autostart_enabled())
        form.addRow(self.autostart_check)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _on_save(self) -> None:
        client_id = self.client_id_edit.text().strip()
        redirect_uri = self.redirect_uri_edit.text().strip()
        state_code = self.state_combo.currentData()
        ticketmaster_key = self.ticketmaster_edit.text().strip()

        if not client_id or not redirect_uri or not ticketmaster_key:
            QMessageBox.warning(self, "Missing information", "All API fields are required.")
            return
        if not state_code:
            QMessageBox.warning(self, "Missing information", "Please select a state to track shows in.")
            return

        self._config.spotify_client_id = client_id
        self._config.spotify_redirect_uri = redirect_uri
        self._config.state_code = state_code
        self._config.check_interval_hours = self.interval_spin.value()
        self._config.start_with_windows = self.autostart_check.isChecked()
        self._config.include_followed_playlists = self.include_followed_check.isChecked()

        config_module.save_config(self._config)
        config_module.set_ticketmaster_api_key(ticketmaster_key)

        if self._config.start_with_windows:
            startup.enable_autostart()
        else:
            startup.disable_autostart()

        self.accept()
