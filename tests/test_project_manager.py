"""Tests for the :mod:`vigapp.sistema.project_manager` module."""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vigapp.sistema.project_manager import ProjectManager


def test_save_and_load_roundtrip(tmp_path):
    manager = ProjectManager()
    model = {"name": "sample", "values": [1, 2, 3]}
    file_path = tmp_path / "project.json"

    manager.save(model, file_path)
    loaded = manager.load(file_path)

    assert loaded == model

