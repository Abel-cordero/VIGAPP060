import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vigapp.ui.design_window import DesignWindow


def test_calc_as_req_sample():
    result = DesignWindow._calc_as_req(None, 20, 210, 30, 45, 4200, 0.9)
    assert abs(result - 13.2991) < 1e-4


def test_required_areas_offscreen(monkeypatch):
    """Ensure required areas use the general formula with limits."""
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PyQt5.QtWidgets import QApplication
    import numpy as np

    app = QApplication([])
    mn = np.array([-10.0, -15.0, -20.0])
    mp = np.array([5.0, 10.0, 15.0])
    win = DesignWindow(mn, mp, show_window=False)
    win.edits['b (cm)'].setText('30')
    win.edits["h (cm)"].setText('50')
    win.edits["r (cm)"].setText('4')
    win.edits["f'c (kg/cm²)"].setText('210')
    win.edits["fy (kg/cm²)"].setText('4200')
    win.edits['φ'].setText('0.9')
    win.calc_effective_depth()
    as_n, as_p = win._required_areas()

    # Raw formula results should be stored and within the min/max limits
    assert np.all(as_n >= win.as_min)
    assert np.all(as_n <= win.as_max)
    assert np.all(as_p >= win.as_min)
    assert np.all(as_p <= win.as_max)

