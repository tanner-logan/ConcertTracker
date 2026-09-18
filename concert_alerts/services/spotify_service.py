"""Fetches the set of unique artists across the user's own Spotify playlists."""
from __future__ import annotations

import json
import logging
import os
import webbrowser
from urllib.parse import urlparse

import spotipy
from spotipy.oauth2 import SpotifyPKCE

from .. import constants
from ..models import Artist
from .oauth_server import wait_for_auth_code

log = logging.getLogger(__name__)


def _build_oauth(client_id: str, redirect_uri: str) -> SpotifyPKCE:
    return SpotifyPKCE(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=constants.SPOTIFY_SCOPE,
        cache_path=constants.SPOTIFY_TOKEN_CACHE_PATH,
        open_browser=False,
    )


def _clear_stale_token_cache() -> None:
    """Delete the cached token if it was authorized with a scope narrower than we need now."""
    path = constants.SPOTIFY_TOKEN_CACHE_PATH
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            cached_scopes = set((json.load(f).get("scope") or "").split())
    except (json.JSONDecodeError, OSError):
        cached_scopes = set()

    required_scopes = set(constants.SPOTIFY_SCOPE.split())
    if not required_scopes.issubset(cached_scopes):
        os.remove(path)


def get_spotify_client(client_id: str, redirect_uri: str) -> spotipy.Spotify:
    """Return an authenticated Spotify client, running the browser login only when needed."""
    _clear_stale_token_cache()
    oauth = _build_oauth(client_id, redirect_uri)

    if not oauth.get_cached_token():
        auth_url = oauth.get_authorize_url()
        webbrowser.open(auth_url)

        parsed = urlparse(redirect_uri)
        code = wait_for_auth_code(parsed.hostname or "127.0.0.1", parsed.port or 8888)
        oauth.get_access_token(code)

    return spotipy.Spotify(auth_manager=oauth)


def fetch_unique_artists(sp: spotipy.Spotify, include_followed: bool = True) -> list[Artist]:
    """Walk the current user's playlists and collect unique track artists.

    When `include_followed` is True (default), playlists the user follows/saved from others are
    scanned too, not just ones they created themselves.
    """
    my_id = sp.current_user()["id"]
    artists: dict[str, Artist] = {}

    playlists_page = sp.current_user_playlists(limit=50)
    while playlists_page:
        for playlist in playlists_page["items"]:
            if not playlist:
                continue
            owned = playlist.get("owner", {}).get("id") == my_id
            if not owned and not include_followed:
                continue
            try:
                _collect_artists_from_playlist(sp, playlist["id"], artists)
            except Exception:
                log.exception("Failed to read playlist '%s' (%s)", playlist.get("name"), playlist["id"])
        playlists_page = sp.next(playlists_page) if playlists_page.get("next") else None

    return list(artists.values())


def _collect_artists_from_playlist(sp: spotipy.Spotify, playlist_id: str, artists: dict) -> None:
    items_page = sp.playlist_items(playlist_id, additional_types=("track",), limit=100)
    while items_page:
        for item in items_page["items"]:
            track = item.get("track") or item.get("item") or {}
            for artist in track.get("artists") or []:
                artist_id = artist.get("id")
                if artist_id and artist_id not in artists:
                    artists[artist_id] = Artist(id=artist_id, name=artist["name"])
        items_page = sp.next(items_page) if items_page.get("next") else None
