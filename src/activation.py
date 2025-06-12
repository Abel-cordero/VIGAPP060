"""Simple hardware-locked activation handling."""

import hashlib
import os
import uuid

# File storing the hardware fingerprint
KEY_FILE = "key.dat"
# Static license key distributed to users
LICENSE_KEY = "ABC123-XYZ"

def hardware_id():
    """Return a stable identifier for the current machine."""
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode()).hexdigest()

def activate(key: str) -> bool:
    """Store the hardware hash if the provided key is correct."""
    if key != LICENSE_KEY:
        return False
    with open(KEY_FILE, "w") as f:
        f.write(hardware_id())
    return True

def check_activation() -> bool:
    """Check that this machine matches the stored activation."""
    if not os.path.exists(KEY_FILE):
        return False
    with open(KEY_FILE) as f:
        stored = f.read().strip()
    return stored == hardware_id()
