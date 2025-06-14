import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vigapp.ui.design_window import DesignWindow


def test_calc_as_req_sample():
    result = DesignWindow._calc_as_req(None, 20, 210, 30, 45, 4200, 0.9)
    assert abs(result - 13.2991) < 1e-4

