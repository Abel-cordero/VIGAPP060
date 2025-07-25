"""Interactive 2D view of the beam section using pyqtgraph."""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QInputDialog
import pyqtgraph as pg


class BarROI(pg.CircleROI):
    """Draggable circular ROI representing a single bar."""

    clicked = pyqtSignal(object)

    def __init__(self, pos, size, index, **kw):
        super().__init__(pos, size, movable=True, **kw)
        self.bar_index = index

    def mouseClickEvent(self, ev):
        if ev.button() == Qt.LeftButton and ev.isFinish():
            self.clicked.emit(self)
        super().mouseClickEvent(ev)


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
        self.setFocusPolicy(Qt.StrongFocus)
        self.plot.setAspectLocked(True)
        self.plot.hideAxis('left')
        self.plot.hideAxis('bottom')
        self._bars = []
        self._selected = None
        self._dragging = None
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
            roi = BarROI([x - d/2, self.cover - d/2], [d, d], idx, pen=pg.mkPen('b'), brush=pg.mkBrush('b'))
            roi.sigRegionChangeFinished.connect(lambda r=roi: self._on_drag_finished(r))
            roi.clicked.connect(self._on_bar_clicked)
            self.plot.addItem(roi)
            self._bars.append(roi)

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

    def _on_bar_clicked(self, roi):
        idx = roi.bar_index
        self._selected = idx
        self.barraSeleccionada.emit(idx)
        value, ok = QInputDialog.getDouble(self, "Longitud", "L (m):", decimals=2)
        if ok:
            self.longitudCambiada.emit(idx, value)

    def _on_drag_finished(self, roi):
        center_x = roi.pos()[0] + roi.size()[0] / 2
        self._bars.sort(key=lambda r: r.pos()[0])
        for i, r in enumerate(self._bars):
            r.bar_index = i
        self.barraMovida.emit(roi.bar_index, center_x)

    def keyPressEvent(self, event):
        """Allow reordering bars using left/right arrows."""
        if self._selected is None:
            return super().keyPressEvent(event)

        if event.key() in (Qt.Key_Left, Qt.Key_Right):
            idx = self._selected
            if event.key() == Qt.Key_Left and idx > 0:
                j = idx - 1
            elif event.key() == Qt.Key_Right and idx < len(self._bars) - 1:
                j = idx + 1
            else:
                return

            roi_i = self._bars[idx]
            roi_j = self._bars[j]
            pos_i = roi_i.pos()
            pos_j = roi_j.pos()
            roi_i.setPos(pos_j)
            roi_j.setPos(pos_i)
            self._bars[idx], self._bars[j] = self._bars[j], self._bars[idx]
            for k, r in enumerate(self._bars):
                r.bar_index = k
            self._selected = j
            center_x = self._bars[j].pos()[0] + self._bars[j].size()[0] / 2
            self.barraMovida.emit(j, center_x)
            event.accept()
        else:
            super().keyPressEvent(event)
