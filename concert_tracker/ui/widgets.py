"""Small reusable UI pieces: stat cards and show-row list items."""
from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ..models import ShowMatch


class StatCard(QFrame):
    def __init__(self, label: str, value: int, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)

        self._label = QLabel(label.upper())
        self._label.setObjectName("statLabel")

        self._value = QLabel(str(value))
        self._value.setObjectName("statValue")

        layout.addWidget(self._label)
        layout.addWidget(self._value)

    def set_value(self, value: int) -> None:
        self._value.setText(str(value))


class ShowRow(QFrame):
    def __init__(self, match: ShowMatch, parent=None):
        super().__init__(parent)
        self.setObjectName("card")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        thumb = QLabel()
        thumb.setFixedSize(48, 48)
        thumb.setStyleSheet("border-radius: 6px; background-color: #2a2a2e;")
        thumb.setScaledContents(True)
        if match.image_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(match.image_bytes):
                thumb.setPixmap(pixmap)
        layout.addWidget(thumb)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        name_row = QHBoxLayout()
        name_label = QLabel(match.artist_name)
        name_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        name_row.addWidget(name_label)
        name_row.addStretch()
        text_col.addLayout(name_row)

        detail_label = QLabel(f"{match.city} • {_format_date(match.event_date)}")
        detail_label.setObjectName("subtitle")
        text_col.addWidget(detail_label)

        if match.is_new:
            badge = QLabel("New match")
            badge.setObjectName("newBadge")
            badge.setFixedWidth(70)
            text_col.addWidget(badge)

        layout.addLayout(text_col, stretch=1)

        link_button = QPushButton("\u2197")
        link_button.setObjectName("linkButton")
        link_button.setCursor(Qt.PointingHandCursor)
        link_button.setFixedSize(28, 28)
        link_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(match.event_url)))
        layout.addWidget(link_button, alignment=Qt.AlignTop)


def _format_date(iso_date: str) -> str:
    if not iso_date:
        return "Date TBA"
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%d")
        return f"{dt.strftime('%b')} {dt.day}"
    except ValueError:
        return iso_date
