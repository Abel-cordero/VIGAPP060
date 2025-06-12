"""3D window rendering the beam model using pyqtgraph.opengl."""

from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
import pyqtgraph.opengl as gl
import numpy as np


class Section3DView(QMainWindow):
    """Shows a transparent beam with its reinforcement."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Desarrollo de Refuerzo")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.view = gl.GLViewWidget()
        layout.addWidget(self.view)
        self.view.opts['distance'] = 200

    def set_model(self, b, h, L):
        """Draw a simple rectangular prism as the beam."""
        self.view.clear()
        verts = np.array([
            [0, 0, 0], [b, 0, 0], [b, h, 0], [0, h, 0],
            [0, 0, L], [b, 0, L], [b, h, L], [0, h, L]
        ])
        faces = np.array([
            [0, 1, 2], [0, 2, 3],
            [4, 5, 6], [4, 6, 7],
            [0, 1, 5], [0, 5, 4],
            [1, 2, 6], [1, 6, 5],
            [2, 3, 7], [2, 7, 6],
            [3, 0, 4], [3, 4, 7]
        ])
        mesh = gl.GLMeshItem(vertexes=verts, faces=faces, smooth=False,
                              color=(0.5, 0.5, 0.5, 0.3), shader='shaded', drawEdges=True)
        self.view.addItem(mesh)
