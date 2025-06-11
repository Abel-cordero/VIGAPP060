import pytest
import sys
import types
import importlib.util
import pathlib
import math


def load_viga_module():
    # minimal numpy stub
    class NDArray(list):
        def __mul__(self, other):
            return NDArray([x * other for x in self])

        __rmul__ = __mul__

        def __truediv__(self, other):
            return NDArray([x / other for x in self])

    np_stub = types.ModuleType('numpy')
    np_stub.array = lambda seq: NDArray(seq)
    np_stub.abs = lambda arr: NDArray([abs(x) for x in arr])
    np_stub.sqrt = math.sqrt
    sys.modules['numpy'] = np_stub

    # stub PyQt5 and related modules
    for name in [
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'matplotlib',
        'matplotlib.backends',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.pyplot',
        'scipy',
        'scipy.interpolate',
        'mplcursors',
    ]:
        if name not in sys.modules:
            sys.modules[name] = types.ModuleType(name)

    widgets = sys.modules['PyQt5.QtWidgets']
    for attr in [
        'QApplication', 'QMainWindow', 'QWidget', 'QGridLayout', 'QLabel',
        'QLineEdit', 'QPushButton', 'QRadioButton', 'QButtonGroup',
        'QMessageBox', 'QComboBox'
    ]:
        setattr(widgets, attr, object)

    sys.modules['PyQt5.QtCore'].Qt = object
    sys.modules['PyQt5.QtGui'].QGuiApplication = object
    sys.modules['matplotlib.backends.backend_qt5agg'].FigureCanvasQTAgg = object
    sys.modules['scipy.interpolate'].CubicSpline = object

    # load the target module
    path = pathlib.Path(__file__).resolve().parents[1] / 'viga2.0.py'
    spec = importlib.util.spec_from_file_location('viga', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules.pop('numpy', None)
    return module


viga = load_viga_module()


def test_correct_moments_dual2():
    mn = [2, 3, 2]
    mp = [10, 1, 10]
    mn_c, mp_c = viga.MomentApp.correct_moments(None, mn, mp, 'dual2')
    assert list(mn_c) == pytest.approx([5.0, 3.0, 5.0])
    assert list(mp_c) == pytest.approx([10.0, 2.5, 10.0])


def test_correct_moments_dual1():
    mn = [2, 3, 2]
    mp = [10, 1, 10]
    mn_c, mp_c = viga.MomentApp.correct_moments(None, mn, mp, 'dual1')
    assert list(mn_c) == pytest.approx([3.3333333333, 3.0, 3.3333333333])
    assert list(mp_c) == pytest.approx([10.0, 2.5, 10.0])


def test_calc_as_req():
    result = viga.DesignWindow._calc_as_req(None, 10, 210, 30, 40, 4200, 0.9)
    assert result == pytest.approx(7.1092626469)
