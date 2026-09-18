"""Application-wide constants."""
import os

APP_NAME = "ConcertAlerts"
APP_DISPLAY_NAME = "Concert Tracker"
ORG_NAME = "ConcertAlerts"

APP_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), APP_NAME)
CONFIG_PATH = os.path.join(APP_DATA_DIR, "config.json")
DATA_PATH = os.path.join(APP_DATA_DIR, "data.json")
LOG_PATH = os.path.join(APP_DATA_DIR, "debug.log")
SPOTIFY_TOKEN_CACHE_PATH = os.path.join(APP_DATA_DIR, ".spotify_token_cache")

KEYRING_SERVICE = APP_NAME
KEYRING_TICKETMASTER_KEY = "ticketmaster_api_key"

# Read-only access to the user's playlists, including collaborative ones (Spotify treats
# collaborative playlists as requiring this separately from playlist-read-private).
SPOTIFY_SCOPE = "playlist-read-private playlist-read-collaborative"
DEFAULT_SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8888/callback"

TICKETMASTER_BASE_URL = "https://app.ticketmaster.com/discovery/v2"
COUNTRY_CODE = "US"

# (USPS code, display name) for the state-picker shown during setup.
US_STATES = [
    ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"),
    ("CA", "California"), ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"),
    ("DC", "District of Columbia"), ("FL", "Florida"), ("GA", "Georgia"), ("HI", "Hawaii"),
    ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"), ("KS", "Kansas"),
    ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"),
    ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"), ("MS", "Mississippi"),
    ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"), ("NV", "Nevada"),
    ("NH", "New Hampshire"), ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"),
    ("NC", "North Carolina"), ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"),
    ("OR", "Oregon"), ("PA", "Pennsylvania"), ("RI", "Rhode Island"), ("SC", "South Carolina"),
    ("SD", "South Dakota"), ("TN", "Tennessee"), ("TX", "Texas"), ("UT", "Utah"),
    ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"), ("WV", "West Virginia"),
    ("WI", "Wisconsin"), ("WY", "Wyoming"),
]
_STATE_NAMES_BY_CODE = dict(US_STATES)


def state_name_for(state_code: str) -> str:
    return _STATE_NAMES_BY_CODE.get((state_code or "").upper(), state_code)


DEFAULT_CHECK_INTERVAL_HOURS = 12
MIN_CHECK_INTERVAL_HOURS = 1
MAX_CHECK_INTERVAL_HOURS = 48

# Ticketmaster's default consumer rate limit is 5 requests/second.
TICKETMASTER_REQUEST_DELAY_SECONDS = 0.25
