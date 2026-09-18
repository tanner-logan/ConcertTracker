"""Simple data models shared across services and UI."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Artist:
    id: str
    name: str


@dataclass
class ShowMatch:
    artist_name: str
    venue_name: str
    city: str
    event_date: str  # ISO date, e.g. 2026-10-12
    event_url: str
    image_url: Optional[str] = None
    image_bytes: Optional[bytes] = None
    is_new: bool = False

    @property
    def dedupe_key(self) -> str:
        return f"{self.artist_name}|{self.venue_name}|{self.event_date}"


@dataclass
class RefreshResult:
    artist_count: int
    matches: list = field(default_factory=list)
    checked_at: str = ""
