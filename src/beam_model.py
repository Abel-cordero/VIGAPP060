"""Data model representing a reinforced concrete beam."""

class BeamModel:
    """Encapsulates beam geometry, dimensions and reinforcement."""

    def __init__(self, width=0.0, height=0.0, length=0.0, cover=0.0):
        self.width = width
        self.height = height
        self.length = length
        self.cover = cover
        self.rebars = []

    def set_geometry(self, width, height, length, cover):
        """Update basic geometric properties."""
        self.width = width
        self.height = height
        self.length = length
        self.cover = cover

    def add_rebar(self, x, y, diameter):
        """Add a single rebar at the given coordinates."""
        self.rebars.append({"x": x, "y": y, "dia": diameter})

    def clear_rebars(self):
        """Remove all defined rebars."""
        self.rebars.clear()

    def bottom_rebars(self):
        """Return rebars located in the bottom layer."""
        return sorted(
            [r for r in self.rebars if r["y"] <= self.cover],
            key=lambda r: r["x"],
        )

