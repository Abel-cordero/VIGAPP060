import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from PyQt5.QtWidgets import QApplication
from vigapp.ui.shear_window import ShearDesignWindow


def test_shear_diagram_offscreen(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication([])
    shear = ShearDesignWindow(None, show_window=False)
    shear.ed_vu.setText("30")
    shear.ed_ln.setText("6")
    shear.ed_d.setText("50")
    shear.draw_diagram()
