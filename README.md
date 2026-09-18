# Concert Tracker

Windows desktop tray app (Python + PySide6) that finds every unique artist across the playlists
you own on Spotify, cross-references them against Ticketmaster's Discovery API, and shows which
ones have upcoming shows in whichever US state you pick. Everyone who runs it signs in with their
own Spotify account and their own API keys — nothing personal or secret is baked into the code.

## 1. Create a Spotify app (one-time, ~2 minutes)

1. Go to https://developer.spotify.com/dashboard and log in with your own Spotify account.
2. Click **Create app**.
3. Give it any name/description (e.g. "Concert Tracker").
4. Under **Redirect URIs**, add exactly: `http://127.0.0.1:8888/callback`
5. Check the **Web API** box and save.
6. Copy the **Client ID** shown on the app page — you'll paste it into the app's setup dialog.
   No client secret is needed; the app uses the secure PKCE login flow.

## 2. Get a Ticketmaster API key

Grab a free Consumer Key from https://developer.ticketmaster.com/. It's entered directly in the
app's setup dialog and stored in your OS's credential manager (via `keyring`), never in plain
text on disk or anywhere in this repo.

## 3. Run from source

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m concert_alerts
```

The first time it launches, a setup dialog asks you for:

- Your Spotify Client ID and redirect URI (defaults are correct if you followed step 1)
- The US state you want show alerts for
- Your Ticketmaster API key
- How often to check, and whether to start automatically with Windows

Signing in to Spotify opens your browser once to authorize your own account; after that a refresh
token is cached locally at `%APPDATA%\ConcertAlerts\` and reused automatically. You can revisit
these settings any time from the tray icon's right-click menu.

## 4. Build a standalone .exe (for auto-start)

```powershell
pip install pyinstaller
pyinstaller --noconfirm --windowed --onefile --name ConcertAlerts `
  --icon concert_alerts/resources/app_icon.ico `
  --add-data "concert_alerts/resources/app_icon.ico;concert_alerts/resources" `
  run.py
```

The executable is created at `dist\ConcertAlerts.exe`. Move it to a permanent folder (not
Downloads/Temp), run it once, complete setup, then check **Start automatically when Windows
starts** in Settings — this writes a `HKEY_CURRENT_USER\...\Run` registry entry pointing at that
exact exe path, so keep it there.

## How it works

- Only playlists **you own** are scanned for unique artists (not followed/collaborative ones).
- Every artist is checked against Ticketmaster's Discovery API for upcoming music events in the
  state you selected, throttled to stay under Ticketmaster's rate limit.
- Checks run automatically every 12 hours by default (configurable in Settings, 1–48h) and can
  be triggered manually via the tray icon menu or the refresh button in the dashboard.
- Closing the window minimizes it to the system tray; use **Quit** from the tray right-click menu
  to fully exit.
- Results are cached to `%APPDATA%\ConcertAlerts\data.json` so the dashboard shows the last known
  state instantly on launch, even before the first refresh completes.

## Privacy & credentials

- Each user brings their own Spotify Client ID and Ticketmaster API key — none are committed to
  this repo or shared between installs.
- `%APPDATA%\ConcertAlerts\config.json` stores only non-secret preferences (client ID, redirect
  URI, state, interval). The Ticketmaster key and Spotify tokens are never written there in plain
  text — the key lives in your OS credential store, and the Spotify token cache file is local to
  your machine and excluded from version control.

## Project layout

```
concert_alerts/
  app.py                   # wires config, tray, window, scheduler together
  config.py                # settings persistence + keyring-backed secrets
  constants.py, models.py, storage.py
  startup.py                # Windows "run at login" registry integration
  services/
    spotify_service.py      # PKCE login + unique-artist collection
    ticketmaster_service.py # per-state show lookup
    refresh_worker.py       # background QThread that runs a full refresh
    oauth_server.py         # local redirect capture for Spotify login
  ui/
    main_window.py, widgets.py, settings_dialog.py, tray.py, theme.py
```

## License

Released under the [MIT License](LICENSE).
