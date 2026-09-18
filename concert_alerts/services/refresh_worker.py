"""Background worker that performs the full Spotify -> Ticketmaster refresh cycle."""
from __future__ import annotations

import logging
from datetime import datetime

import requests
from PySide6.QtCore import QThread, Signal

from .. import storage
from ..models import RefreshResult
from . import spotify_service, ticketmaster_service

log = logging.getLogger(__name__)


class RefreshWorker(QThread):
    progress = Signal(str)
    finished_ok = Signal(object)  # RefreshResult
    failed = Signal(str)

    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        ticketmaster_key: str,
        state_code: str,
        include_followed_playlists: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self._client_id = client_id
        self._redirect_uri = redirect_uri
        self._ticketmaster_key = ticketmaster_key
        self._state_code = state_code
        self._include_followed_playlists = include_followed_playlists

    def run(self) -> None:
        try:
            self.progress.emit("Signing in to Spotify…")
            sp = spotify_service.get_spotify_client(self._client_id, self._redirect_uri)

            self.progress.emit("Reading your playlists…")
            artists = spotify_service.fetch_unique_artists(sp, self._include_followed_playlists)
            log.info("Fetched %d unique artists from Spotify", len(artists))

            previous = storage.load_cache()
            previous_keys = {
                f"{m['artist_name']}|{m['venue_name']}|{m['event_date']}" for m in previous.get("matches", [])
            }

            self.progress.emit(f"Checking Ticketmaster for {len(artists)} artists…")
            matches = ticketmaster_service.find_shows_in_state(
                self._ticketmaster_key,
                artists,
                self._state_code,
                on_progress=lambda i, total: self.progress.emit(f"Checking Ticketmaster… ({i}/{total})"),
            )

            for match in matches:
                match.is_new = match.dedupe_key not in previous_keys
                if match.image_url:
                    match.image_bytes = self._download_image_or_none(match.image_url)

            checked_at = datetime.now()
            storage.save_cache(len(artists), matches, checked_at)
            log.info("Refresh complete: %d artists, %d matching shows", len(artists), len(matches))

            self.finished_ok.emit(
                RefreshResult(artist_count=len(artists), matches=matches, checked_at=checked_at.isoformat())
            )
        except Exception as exc:  # surfaced to the UI rather than crashing the app
            log.exception("Refresh failed")
            self.failed.emit(str(exc))

    @staticmethod
    def _download_image_or_none(url: str):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.RequestException:
            return None
