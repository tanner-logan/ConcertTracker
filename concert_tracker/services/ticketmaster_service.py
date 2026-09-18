"""Cross-references artist names against Ticketmaster's Discovery API for a chosen US state."""
from __future__ import annotations

import logging
import time
from datetime import date, datetime
from typing import Iterable, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .. import constants
from ..models import Artist, ShowMatch

log = logging.getLogger(__name__)

_session: Optional[requests.Session] = None


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
        _session.mount("https://", HTTPAdapter(max_retries=retries))
    return _session


def find_shows_in_state(
    api_key: str, artists: Iterable[Artist], state_code: str, on_progress=None
) -> List[ShowMatch]:
    """Query Ticketmaster once per artist and return any matching music events in the given state."""
    matches: List[ShowMatch] = []
    artists = list(artists)
    failure_count = 0

    for index, artist in enumerate(artists, start=1):
        artist_matches, failed = _search_artist(api_key, artist.name, state_code)
        matches.extend(artist_matches)
        failure_count += int(failed)
        if on_progress:
            on_progress(index, len(artists))
        time.sleep(constants.TICKETMASTER_REQUEST_DELAY_SECONDS)

    if failure_count:
        log.warning("%d/%d Ticketmaster requests failed (see earlier log lines for details)", failure_count, len(artists))

    matches = _dedupe_matches(matches)
    matches.sort(key=lambda m: (m.event_date == "", m.event_date))
    return matches


def _dedupe_matches(matches: List[ShowMatch]) -> List[ShowMatch]:
    """Collapse multiple Ticketmaster listings (VIP/resale/GA, etc.) for the same show into one."""
    deduped: dict[str, ShowMatch] = {}
    for match in matches:
        deduped.setdefault(match.dedupe_key, match)
    return list(deduped.values())


def _search_artist(api_key: str, artist_name: str, state_code: str) -> tuple[List[ShowMatch], bool]:
    params = {
        "apikey": api_key,
        "keyword": artist_name,
        "stateCode": state_code,
        "countryCode": constants.COUNTRY_CODE,
        "classificationName": "Music",
        "size": 50,
        "sort": "date,asc",
    }
    try:
        response = _get_session().get(f"{constants.TICKETMASTER_BASE_URL}/events.json", params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        body = getattr(exc.response, "text", "")[:300] if getattr(exc, "response", None) is not None else ""
        log.error("Ticketmaster request failed for artist %r: %s %s", artist_name, exc, body)
        return [], True

    events = (response.json() or {}).get("_embedded", {}).get("events", [])
    results = []
    today = date.today()

    for event in events:
        if not _event_matches_artist(event, artist_name):
            continue
        event_date = _extract_event_date(event)
        if event_date and event_date < today:
            continue
        results.append(_to_show_match(artist_name, event, event_date, state_code))

    return results, False


def _event_matches_artist(event: dict, artist_name: str) -> bool:
    attractions = event.get("_embedded", {}).get("attractions", [])
    names = [a.get("name", "") for a in attractions] or [event.get("name", "")]
    target = artist_name.strip().lower()
    return any(target == name.strip().lower() or target in name.strip().lower() for name in names)


def _extract_event_date(event: dict):
    local_date = event.get("dates", {}).get("start", {}).get("localDate")
    if not local_date:
        return None
    try:
        return datetime.strptime(local_date, "%Y-%m-%d").date()
    except ValueError:
        return None


def _to_show_match(artist_name: str, event: dict, event_date, state_code: str) -> ShowMatch:
    venues = event.get("_embedded", {}).get("venues", [{}])
    venue = venues[0] if venues else {}
    images = event.get("images", [])
    image_url = next((img["url"] for img in images if img.get("width", 0) >= 300), None) or (
        images[0]["url"] if images else None
    )

    return ShowMatch(
        artist_name=artist_name,
        venue_name=venue.get("name", "Unknown venue"),
        city=venue.get("city", {}).get("name", constants.state_name_for(state_code)),
        event_date=event_date.isoformat() if event_date else "",
        event_url=event.get("url", ""),
        image_url=image_url,
    )
