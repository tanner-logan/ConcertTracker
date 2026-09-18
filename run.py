"""Entry point used for PyInstaller builds (equivalent to `python -m concert_tracker`)."""
from concert_tracker.app import main

if __name__ == "__main__":
    raise SystemExit(main())
