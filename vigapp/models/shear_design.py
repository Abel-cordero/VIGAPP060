"""Simple shear design calculations based on README_SHEAR.md."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt, ceil


# Available stirrup diameters and areas (cm^2)
BAR_AREAS = {
    '3/8"': 0.71,
    '1/2"': 1.27,
    '5/8"': 1.98,
}

# Diameters in centimeters for each option
BAR_DIAM_CM = {
    '3/8"': 0.95,
    '1/2"': 1.27,
    '5/8"': 1.59,
}


@dataclass
class ShearDesignResult:
    """Result summary for shear design."""

    Vc: float
    Vs: float
    phi_Vc: float
    phi_Vc_Vs: float
    S_sc: float
    S_sr: float
    Lo: float
    Lc: float
    ok: bool
    n_sc: int = 0
    n_sr: int = 0
    sep_sc_real: float = 0.0
    sep_sr_real: float = 0.0


def calc_vc(fc: float, b: float, d: float) -> float:
    """Return concrete shear capacity ``Vc`` in tons."""
    vc_kg = 0.53 * sqrt(fc) * b * d
    return vc_kg / 1000.0


def min_spacing_sc(d: float, phi_long: float, phi_stirr: float) -> float:
    """Return minimum stirrup spacing for the confinement zone (cm)."""
    opts = [d / 4.0, 10.0 * phi_long, 24.0 * phi_stirr, 30.0]
    return min(opts)


def max_spacing_sr(d: float) -> float:
    """Return maximum stirrup spacing for the remaining zone (cm)."""
    return min(0.5 * d, 30.0)


def shear_design(
    Vu: float,
    Ln: float,
    d: float,
    b: float,
    h: float,
    fc: float,
    *,
    fy: float = 4200.0,
    phi: float = 0.85,
    system: str = "dual2",
    stirrup_diam: str = '3/8"',
    phi_long: float = 1.0,
    n_legs: int = 2,
    beam_type: str = "apoyada",
) -> ShearDesignResult:
    """Compute stirrup spacing for a reinforced concrete beam."""

    if stirrup_diam not in BAR_AREAS:
        raise ValueError("Di\u00e1metro de estribo no v\u00e1lido")

    Vc = calc_vc(fc, b, d)
    phi_Vc = phi * Vc

    Av = n_legs * BAR_AREAS[stirrup_diam]
    phi_st = BAR_DIAM_CM[stirrup_diam]

    # Required shear carried by steel (tons)
    Vs_req = max(Vu / phi - Vc, 0.0)

    if Vs_req > 0:
        S_req = Av * fy * d / (Vs_req * 1000.0)
    else:
        S_req = float("inf")

    sc_min = min_spacing_sc(d, phi_long, phi_st)
    sr_max = max_spacing_sr(d)

    S_sc = min(S_req, sc_min)
    S_sr = min(S_req, sr_max)

    Vs_prov = Av * fy * d / min(S_sc, S_sr) / 1000.0
    phi_Vc_Vs = phi * (Vc + Vs_prov)
    ok = Vu <= phi_Vc_Vs

    if system.lower() == "dual1":
        Lo_cm = 2.0 * h
    else:
        Lo_cm = 2.0 * d
    Ln_cm = Ln * 100.0
    if Ln_cm < 0:
        Ln_cm = 0.0

    if Ln_cm - (2.0 * Lo_cm) < 0:
        Lc_cm = 0.0
    else:
        Lc_cm = Ln_cm - (2.0 * Lo_cm)

    # Number of stirrups by zone and real spacing (cm)
    if system.lower() == "volado":
        Lc_cm = Ln_cm - Lo_cm
        n_sc = ceil(Lo_cm / S_sc) if S_sc > 0 else 0
        sep_sc = Lo_cm / n_sc if n_sc else 0.0
        n_sr = ceil(Lc_cm / S_sr) if S_sr > 0 else 0
        sep_sr = Lc_cm / n_sr if n_sr else 0.0
    else:
        n_sc = ceil(Lo_cm / S_sc) if S_sc > 0 else 0
        sep_sc = Lo_cm / n_sc if n_sc else 0.0
        n_sr = ceil(Lc_cm / S_sr) if S_sr > 0 else 0
        sep_sr = Lc_cm / n_sr if n_sr else 0.0

    Lo = Lo_cm / 100.0
    Lc = Lc_cm / 100.0

    return ShearDesignResult(
        Vc=Vc,
        Vs=Vs_prov,
        phi_Vc=phi_Vc,
        phi_Vc_Vs=phi_Vc_Vs,
        S_sc=S_sc,
        S_sr=S_sr,
        Lo=Lo,
        Lc=Lc,
        ok=ok,
        n_sc=n_sc,
        n_sr=n_sr,
        sep_sc_real=sep_sc,
        sep_sr_real=sep_sr,
    )

