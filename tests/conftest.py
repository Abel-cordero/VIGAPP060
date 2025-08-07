import os
import pytest

try:
    from PyQt5.QtWidgets import QApplication
except Exception:  # pragma: no cover - handled in test environment
    QApplication = None


@pytest.fixture(scope="session")
def qapp():
    if QApplication is None:
        pytest.skip("PyQt5 not available")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()
