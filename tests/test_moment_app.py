import os
import sys
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vigapp.ui.moment_app import MomentApp


def test_correct_moments_dual1_dual2():
    mn = np.array([-10.0, -20.0, -15.0])
    mp = np.array([5.0, 2.0, 3.0])

    mn_c1, mp_c1 = MomentApp.correct_moments(mn, mp, 'dual1')
    mn_c2, mp_c2 = MomentApp.correct_moments(mn, mp, 'dual2')

    assert np.allclose(mn_c1, [-10.0, -20.0, -15.0])
    assert np.allclose(mn_c2, [-10.0, -20.0, -15.0])
    assert np.allclose(mp_c1, [5.0, 5.0, 5.0])
    assert np.allclose(mp_c2, [5.0, 5.0, 7.5])

