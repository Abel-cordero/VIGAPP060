import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from PyQt5.QtWidgets import QApplication
from vigapp.ui.design_window import DesignWindow
from vigapp.ui.shear_window import ShearDesignWindow
import numpy as np


def test_shear_diagram_offscreen(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication([])
    mn = np.array([-10.0, -15.0, -20.0])
    mp = np.array([5.0, 10.0, 15.0])
    design = DesignWindow(mn, mp, show_window=False)
    shear = ShearDesignWindow(design, show_window=False)
    shear.ed_vu.setText("30")
    shear.ed_ln.setText("6")
    shear.calculate()
    assert shear.ed_d.isReadOnly()
    assert shear.btn_pdf.isEnabled()
    assert shear.btn_dxf.isEnabled()

    shear2 = ShearDesignWindow(None, show_window=False)
    shear2.ed_vu.setText("30")
    shear2.ed_ln.setText("6")
    shear2.calculate()
    assert shear2.ed_d.isReadOnly()
    app.quit()


def test_section_canvas_exists(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    app = QApplication([])
    shear = ShearDesignWindow(None, show_window=False)
    assert hasattr(shear, "canvas_sec")
    app.quit()
