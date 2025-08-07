import os
import sys
import pytest

try:
    from PyQt5.QtWidgets import QApplication
except Exception:  # pragma: no cover - handled in test environment
    QApplication = None


# Ensure the project root is on PYTHONPATH so tests can import vigapp
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
os.environ.setdefault("PYTHONPATH", ROOT_DIR)

@pytest.fixture(scope="session")
def qapp():
    if QApplication is None:
        pytest.skip("PyQt5 not available")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()
