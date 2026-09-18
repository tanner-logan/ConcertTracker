"""Persisted (non-secret) app configuration + secret access via keyring."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Optional

import keyring

from . import constants


@dataclass
class AppConfig:
    spotify_client_id: str = ""
    spotify_redirect_uri: str = constants.DEFAULT_SPOTIFY_REDIRECT_URI
    state_code: str = ""
    check_interval_hours: int = constants.DEFAULT_CHECK_INTERVAL_HOURS
    start_with_windows: bool = False
    include_followed_playlists: bool = True

    @property
    def is_complete(self) -> bool:
        return bool(self.spotify_client_id) and bool(self.state_code) and bool(get_ticketmaster_api_key())


def load_config() -> AppConfig:
    if not os.path.exists(constants.CONFIG_PATH):
        return AppConfig()
    try:
        with open(constants.CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        known_fields = AppConfig.__dataclass_fields__
        return AppConfig(**{k: v for k, v in raw.items() if k in known_fields})
    except (json.JSONDecodeError, OSError, TypeError):
        return AppConfig()


def save_config(config: AppConfig) -> None:
    os.makedirs(constants.APP_DATA_DIR, exist_ok=True)
    with open(constants.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2)


def get_ticketmaster_api_key() -> Optional[str]:
    return keyring.get_password(constants.KEYRING_SERVICE, constants.KEYRING_TICKETMASTER_KEY) or ""


def set_ticketmaster_api_key(api_key: str) -> None:
    keyring.set_password(constants.KEYRING_SERVICE, constants.KEYRING_TICKETMASTER_KEY, api_key)
