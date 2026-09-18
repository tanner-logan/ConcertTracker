"""Local JSON cache of the last known artists/matches (survives restarts)."""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List

from . import constants
from .models import ShowMatch


def load_cache() -> dict:
    if not os.path.exists(constants.DATA_PATH):
        return {"artist_count": 0, "matches": [], "checked_at": ""}
    try:
        with open(constants.DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"artist_count": 0, "matches": [], "checked_at": ""}


def save_cache(artist_count: int, matches: List[ShowMatch], checked_at: datetime) -> None:
    os.makedirs(constants.APP_DATA_DIR, exist_ok=True)
    payload = {
        "artist_count": artist_count,
        "matches": [
            {
                "artist_name": m.artist_name,
                "venue_name": m.venue_name,
                "city": m.city,
                "event_date": m.event_date,
                "event_url": m.event_url,
                "image_url": m.image_url,
            }
            for m in matches
        ],
        "checked_at": checked_at.isoformat(),
    }
    with open(constants.DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
