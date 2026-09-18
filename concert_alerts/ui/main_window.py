"""Main dashboard window styled after the Concert Tracker mockup."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from .. import constants
from ..models import RefreshResult
from .theme import build_app_icon
from .widgets import ShowRow, StatCard


class MainWindow(QWidget):
    hidden_to_tray = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(constants.APP_DISPLAY_NAME)
        self.setWindowIcon(build_app_icon())
        self.resize(420, 620)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 16)
        root.setSpacing(16)

        root.addLayout(self._build_header())

        stats_row = QHBoxLayout()
        self.artists_card = StatCard("Tracked artists", 0)
        self.shows_card = StatCard("Upcoming shows", 0)
        stats_row.addWidget(self.artists_card)
        stats_row.addWidget(self.shows_card)
        root.addLayout(stats_row)

        section_label = QLabel("Upcoming shows")
        section_label.setObjectName("sectionHeader")
        self.section_label = section_label
        root.addWidget(section_label)

        self.list_container = QVBoxLayout()
        self.list_container.setSpacing(8)
        self.list_container.addWidget(self._create_empty_label())
        self.list_container.addStretch()

        list_widget = QWidget()
        list_widget.setLayout(self.list_container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(list_widget)
        root.addWidget(scroll, stretch=1)

        root.addLayout(self._build_footer())

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()

        icon_label = QLabel()
        icon_label.setPixmap(build_app_icon(28).pixmap(28, 28))
        header.addWidget(icon_label)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel(constants.APP_DISPLAY_NAME)
        title.setObjectName("title")
        self.title_label = title
        subtitle = QLabel("Running in background")
        subtitle.setObjectName("subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addLayout(title_col)

        header.addStretch()

        self.status_badge = QLabel("\u25cf Active")
        self.status_badge.setObjectName("activeBadge")
        header.addWidget(self.status_badge, alignment=Qt.AlignTop)

        return header

    def _build_footer(self) -> QVBoxLayout:
        footer = QVBoxLayout()
        footer.setSpacing(2)

        row = QHBoxLayout()
        self.refresh_button = QPushButton("\u21bb")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.setFixedSize(24, 24)
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        row.addWidget(self.refresh_button)

        last_col = QVBoxLayout()
        last_col.setSpacing(0)
        last_label = QLabel("Last checked")
        last_label.setObjectName("footerLabel")
        self.last_checked_value = QLabel("Never")
        last_col.addWidget(last_label)
        last_col.addWidget(self.last_checked_value)
        row.addLayout(last_col)
        row.addStretch()
        footer.addLayout(row)

        disclaimer = QLabel("Live data from Spotify & Ticketmaster.")
        disclaimer.setObjectName("disclaimer")
        footer.addWidget(disclaimer)

        return footer

    @staticmethod
    def _create_empty_label() -> QLabel:
        label = QLabel("No matching shows found yet.")
        label.setObjectName("subtitle")
        return label

    def set_status(self, text: str) -> None:
        self.status_badge.setText(f"\u25cf {text}")

    def show_loading(self, message: str) -> None:
        self.last_checked_value.setText(message)

    def set_state(self, state_name: str) -> None:
        """Update the section header once the user picks a state in Settings."""
        self.section_label.setText(f"Upcoming {state_name} shows" if state_name else "Upcoming shows")

    def apply_result(self, result: RefreshResult) -> None:
        self.artists_card.set_value(result.artist_count)
        self.shows_card.set_value(len(result.matches))

        while self.list_container.count():
            item = self.list_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not result.matches:
            self.list_container.addWidget(self._create_empty_label())
        else:
            for match in result.matches:
                self.list_container.addWidget(ShowRow(match))
        self.list_container.addStretch()

        checked_dt = datetime.fromisoformat(result.checked_at) if result.checked_at else None
        self.last_checked_value.setText(_format_checked_at(checked_dt))

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        self.hidden_to_tray.emit()


def _format_checked_at(dt) -> str:
    if not dt:
        return "Never"
    today = datetime.now().date()
    time_str = dt.strftime("%I:%M %p").lstrip("0")
    if dt.date() == today:
        return f"Today, {time_str}"
    return f"{dt.strftime('%b')} {dt.day}, {time_str}"
