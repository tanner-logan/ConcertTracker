"""Entry point used for PyInstaller builds (equivalent to `python -m concert_alerts`)."""
from concert_alerts.app import main

if __name__ == "__main__":
    raise SystemExit(main())
