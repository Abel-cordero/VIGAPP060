"""Helper utilities for unit conversions and styling."""

from matplotlib.figure import Figure

from .models.constants import DIAM_CM


# Order of colours to cycle through for each diameter key
_COLOR_ORDER = ["red", "blue", "yellow"]

# Mapping of diameter labels to colours. This mirrors the mapping used in
# :mod:`vigapp.graphics.utilities` so both modules remain consistent.
DIAM_COLOR = {
    key: _COLOR_ORDER[i % len(_COLOR_ORDER)]
    for i, key in enumerate(DIAM_CM.keys())
}

_DEFAULT_COLOR = "black"


def color_for_diameter(diam: str) -> str:
    """Return a colour associated with a rebar diameter key.

    Parameters
    ----------
    diam:
        The label used to identify the rebar diameter (e.g. ``"12mm"``).

    Returns
    -------
    str
        Colour name for the given diameter or a default value when the
        diameter is unknown.
    """

    return DIAM_COLOR.get(diam, _DEFAULT_COLOR)


def latex_image(latex: str, fontsize: int = 10) -> str:
    """Return HTML using MathJax for a LaTeX expression."""
    style = f"font-size:{fontsize}px"
    return f'<span style="{style}">\\({latex}\\)</span>'


