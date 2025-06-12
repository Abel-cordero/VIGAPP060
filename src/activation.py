"""Simple hardware-locked activation handling."""

import hashlib
import os
import uuid

def _app_dir() -> str:
    """Return the application data folder."""
    if os.name == "nt":
        base = os.getenv("APPDATA", os.path.expanduser("~"))
    else:
        base = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    path = os.path.join(base, "vigapp060")
    os.makedirs(path, exist_ok=True)
    return path


APP_DIR = _app_dir()
# File storing the hardware fingerprint
KEY_FILE = os.path.join(APP_DIR, "key.dat")
COUNTER_FILE = os.path.join(APP_DIR, "counter.dat")
# Static license key prefix
LICENSE_PREFIX = "ABC"
LICENSE_SUFFIX = "-XYZ"


def _read_counter() -> int:
    """Return the current license counter."""
    if os.path.exists(COUNTER_FILE):
        try:
            return int(open(COUNTER_FILE).read().strip())
        except ValueError:
            pass
    return 1


def _write_counter(val: int) -> None:
    """Persist the license counter."""
    with open(COUNTER_FILE, "w") as f:
        f.write(str(val))


def current_license() -> str:
    """Return the expected license for activation."""
    counter = _read_counter()
    return f"{LICENSE_PREFIX}{counter:03d}{LICENSE_SUFFIX}"

def hardware_id() -> str:
    """Return a stable identifier for the current machine."""
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode()).hexdigest()


def activate(key: str) -> bool:
    """Store the hardware hash if the provided key is correct."""
    if key != current_license():
        return False
    with open(KEY_FILE, "w") as f:
        f.write(hardware_id())
    _write_counter(_read_counter() + 1)
    return True

def check_activation() -> bool:
    """Check that this machine matches the stored activation."""
    if not os.path.exists(KEY_FILE):
        return False
    with open(KEY_FILE) as f:
        stored = f.read().strip()
    return stored == hardware_id()
