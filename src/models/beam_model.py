"""Data model representing a reinforced concrete beam."""


class BeamModel:
    """Encapsulates beam geometry, loads and reinforcement."""

    def __init__(self):
        self.sections = []
        self.bars = []
        self.layers = []
