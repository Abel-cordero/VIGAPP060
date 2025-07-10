"""Steel design helper functions."""

import numpy as np


def calc_as_req(Mu: float, fc: float, b: float, d: float, fy: float, phi: float) -> float:
    """Calculate required steel area for a single moment."""
    Mu_kgcm = abs(Mu) * 100000  # convert TN·m to kg·cm
    term = 1.7 * fc * b * d / (2 * fy)
    root = (2.89 * (fc * b * d) ** 2) / (fy**2) - (6.8 * fc * b * Mu_kgcm) / (
        phi * (fy**2)
    )
    root = max(root, 0)
    return term - 0.5 * np.sqrt(root)


def calc_as_limits(fc: float, fy: float, b: float, d: float) -> tuple[float, float]:
    """Return minimum and maximum reinforcement areas."""
    beta1 = 0.85 if fc <= 280 else 0.85 - ((fc - 280) / 70) * 0.05
    as_min = 0.7 * (np.sqrt(fc) / fy) * b * d
    pmax = 0.75 * ((0.85 * fc * beta1 / fy) * (6000 / (6000 + fy)))
    as_max = pmax * b * d
    return as_min, as_max

