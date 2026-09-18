"""Configures file logging so refresh failures leave a trail in %APPDATA%\\ConcertTracker\\debug.log."""
from __future__ import annotations

import logging
import os

from . import constants


def setup_logging() -> None:
    os.makedirs(constants.APP_DATA_DIR, exist_ok=True)
    handler = logging.FileHandler(constants.LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
