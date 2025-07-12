import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vigapp.models.shear_design import shear_design, min_spacing_sc, max_spacing_sr


def test_shear_design_sample():
    res = shear_design(
        Vu=30,
        Ln=6,
        d=50,
        b=30,
        h=60,
        fc=210,
        phi_long=1.27,
    )
    assert res.ok
    assert abs(res.S_sc - 12.55) < 0.1
    assert abs(res.Lc - 4.0) < 1e-6
    assert res.phi_Vc_Vs >= 30


def test_min_spacing():
    sc = min_spacing_sc(50, 1.27, 0.95)
    sr = max_spacing_sr(50)
    assert sc <= 15
    assert sr <= 25
