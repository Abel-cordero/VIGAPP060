# Shear Scheme Diagram

This module provides utilities to draw simplified shear diagrams for beams.

The figure aims to mimic a clean technical drawing:

- Dimension lines include centered labels and use thin arrows.
- The Vu arrows stay just above the beam edge and are colored red.
- Simply supported beams show vertical marks at each support.
- Cantilever beams include a gray block at the fixed end.

Use `draw_shear_scheme(ax, Vu, ln, d, beam_type)` to add the diagram
to a Matplotlib axis. Set `beam_type` to either `"apoyada"` or `"volado"`.
