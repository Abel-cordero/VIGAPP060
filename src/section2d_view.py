"""Interactive 2D view of the beam section using pyqtgraph."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph as pg


class Section2DView(QWidget):
    """Simple 2D representation of the beam section with draggable bars."""

    barraSeleccionada = pyqtSignal(int)
    barraMovida = pyqtSignal(int, float)
    longitudCambiada = pyqtSignal(int, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.plot = pg.PlotWidget()
        layout.addWidget(self.plot)
        self.plot.setAspectLocked(True)
        self.plot.hideAxis('left')
        self.plot.hideAxis('bottom')
        self._bars = []
        self._selected = None
        self.b = 30
        self.h = 50
        self.cover = 4

    def set_section(self, b, h, cover):
        """Configure dimensions of the drawn section."""
        self.b = b
        self.h = h
        self.cover = cover
        self._draw_section()

    def set_bars(self, diams):
        """Create draggable bars for each diameter entry."""
        self._bars = []
        self.plot.clear()
        self._draw_section()
        if not diams:
            return
        spacing = (self.b - 2 * self.cover) / max(len(diams) - 1, 1)
        xs = [self.cover + i * spacing for i in range(len(diams))]
        for idx, (x, d) in enumerate(zip(xs, diams)):
            item = pg.ScatterPlotItem([x], [self.cover], size=8 + d * 3,
                                       brush=pg.mkBrush('b'))
            item.opts['data'] = idx
            item.sigClicked.connect(self._on_clicked)
            self.plot.addItem(item)
            self._bars.append(item)

    # internal helpers -------------------------------------------------
    def _draw_section(self):
        self.plot.clear()
        rect = pg.QtGui.QGraphicsRectItem(0, 0, self.b, self.h)
        rect.setPen(pg.mkPen('k'))
        self.plot.addItem(rect)
        inner = pg.QtGui.QGraphicsRectItem(
            self.cover, self.cover,
            self.b - 2 * self.cover, self.h - 2 * self.cover)
        inner.setPen(pg.mkPen('r', style=Qt.DashLine))
        self.plot.addItem(inner)

    def _on_clicked(self, plot, points):
        if not points:
            return
        idx = points[0].data()
        self._selected = idx
        self.barraSeleccionada.emit(idx)
