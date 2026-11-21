"""Classify metal-region evidence and quantify simulated detection performance."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.stats import binomtest, t

from .common import canonical_bytes, setting, sha256_bytes
from .contracts import Config, DetectionResult, PeakFit, QCResult, Spectrum
from .fit import fit_peak, independent_points
from .qc import assess_qc
from .sim import FWHM_PER_SIGMA, GAUSSIAN_AREA_FACTOR, simulate_spectrum


@dataclass(frozen=True)
class _AreaBounds:
    lower: np.ndarray
    upper: np.ndarray


def _template_area_bounds(
    x: np.ndarray,
    y: np.ndarray,
    centers: np.ndarray,
    fwhm: float,
    tail_probability: float,
) -> _AreaBounds | None:
    """Fit each unit-area Gaussian template with its own linear baseline."""
    degrees = x.size - 3  # Offset, slope, and template area.
    if degrees < 1 or fwhm <= 0 or not np.all(np.isfinite(y)):
        return None

    span = float(np.ptp(x))
    if span <= 0:
        return None
    background = np.column_stack((np.ones(x.size), (x - x.mean()) / span))
    basis, _ = np.linalg.qr(background)
    data = y - basis @ (basis.T @ y)
    sigma = fwhm / FWHM_PER_SIGMA
    profiles = np.exp(-0.5 * ((x[:, None] - centers) / sigma) ** 2)
    profiles /= GAUSSIAN_AREA_FACTOR * sigma
    templates = profiles - basis @ (basis.T @ profiles)
    information = np.sum(templates**2, axis=0)
    if np.any(information <= np.finfo(float).tiny):
        return None

    area = data @ templates / information
    residual = data[:, None] - templates * area
    variance = np.sum(residual**2, axis=0) / degrees
    margin = t.isf(tail_probability, degrees) * np.sqrt(variance / information)
    return _AreaBounds(lower=area - margin, upper=np.maximum(area, 0) + margin)


def upper_limit(
    spectrum: Spectrum,
    config: Config,
) -> tuple[float | None, str | None]:
    """Compute the finite-template one-sided area envelope for a synthetic spectrum."""
    if spectrum.origin != "SIMULATED" or spectrum.acquisition.get("noise_kind") not in {
        "white", "zero_filled"
    }:
        return None, None
    if setting(config, "qc", "upper_limit_method") != "gaussian_template_bank_t_bound":
        return None, None

    confidence = float(setting(config, "qc", "upper_limit_confidence"))
    alpha = 1 - confidence
    step = float(setting(config, "qc", "upper_limit_center_step_ppm"))
    low, high = setting(config, "qc", "metal_center_bounds_ppm")
    nominal = float(setting(config, "simulation", "metal_center_ppm"))
    if not (0 < alpha < 0.5 and step > 0 and low <= nominal <= high):
        raise ValueError("Upper limit requires a valid tail probability and finite center bank")

    centers = np.unique(np.r_[np.arange(low, high, step), high, nominal])
    fwhm = float(setting(config, "simulation", "metal_fwhm_ppm"))
    x, y = independent_points(spectrum, tuple(setting(config, "fit", "metal_window_ppm")))
    post_discharge = spectrum.stage == "post_discharge"
    bounds = _template_area_bounds(x, y, centers, fwhm, alpha / 2 if post_discharge else alpha)
    if bounds is None:
        return None, None

    limit = float(np.max(bounds.upper))
    method = (
        f"{1 - alpha:.0%} one-sided finite-bank Gaussian area envelope, FWHM {fwhm:g} ppm, "
        f"centers {low:g}–{high:g} ppm at {step:g} ppm steps plus {nominal:g} ppm. "
        "A_UL = max_j(max(0, A_j) + t_(1-alpha*,n-3) u_j). "
        "Each template has a linear baseline and independent Gaussian native-grid noise."
    )
    if post_discharge:
        scenario = setting(config, "simulation", "trajectory_protocol_and_noise")
        center = float(setting(config, "simulation", "reference_center_ppm"))
        rx, ry = independent_points(spectrum, tuple(setting(config, "fit", "reference_window_ppm")))
        reference = _template_area_bounds(
            rx, ry, np.array([center]), float(scenario["reference_fwhm_ppm"]), alpha / 2
        )
        lower_reference = float(reference.lower[0]) if reference is not None else 0.0
        if not math.isfinite(lower_reference) or lower_reference <= 0:
            return None, None
        limit /= lower_reference
        method += (
            " RMDI_UL = A_UL / lower reference area. The metal and reference tails each use alpha/2."
        )
    else:
        method += " The metal tail uses alpha."
    return (limit, method) if math.isfinite(limit) and limit > 0 else (None, None)


def _area_and_sd(fit: PeakFit) -> tuple[float, float] | None:
    area, sd = fit.peak_area_au_ppm, fit.peak_area_u_au_ppm
    if area is None or sd is None or not all(math.isfinite(item) and item > 0 for item in (area, sd)):
        return None
    return area, sd


def _supports_detection(qc: QCResult) -> bool:
    needed = {"fit_convergence", "peak_position", "baseline_residual_lag1"}
    passed = {check["name"] for check in qc.checks if check["status"] == "PASS"}
    return qc.status != "FAIL" and needed <= passed


def classify(
    spectrum: Spectrum,
    metal_fit: PeakFit,
    reference_fit: PeakFit | None,
    qc: QCResult,
    config: Config,
) -> DetectionResult:
    """Return detection status and a quantitative estimate only when supported."""
    snr = metal_fit.fitted_snr
    if qc.status == "FAIL" or snr is None or not math.isfinite(snr):
        return DetectionResult("invalid", None, None, None, None, "Acquisition or fit fails QC.")

    lower = float(setting(config, "qc", "censor_snr_candidate"))
    upper = float(setting(config, "qc", "detect_snr_candidate"))
    if not 0 <= lower < upper:
        raise ValueError("Detection thresholds require 0 <= censor_snr < detect_snr")

    if not _supports_detection(qc):
        return DetectionResult(
            "uncertain", None, None, None, None, "Peak location or residual structure limits interpretation."
        )
    if snr < lower:
        bound, method = upper_limit(spectrum, config)
        return DetectionResult("censored", None, None, bound, method, f"Fitted SNR below {lower:g}.")
    if snr < upper:
        return DetectionResult("uncertain", None, None, None, None, f"Fitted SNR between {lower:g} and {upper:g}.")

    metal = _area_and_sd(metal_fit)
    if metal is None:
        return DetectionResult("uncertain", None, None, None, None, "Metal-area uncertainty is unavailable.")
    value, sd = metal
    if spectrum.stage == "post_discharge":
        reference = _area_and_sd(reference_fit) if reference_fit is not None else None
        if reference is None:
            return DetectionResult("uncertain", None, None, None, None, "Reference-area uncertainty is unavailable.")
        ref_area, ref_sd = reference
        value /= ref_area
        # The metal and reference windows use disjoint independent native bins.
        sd = math.hypot(sd / ref_area, value * ref_sd / ref_area)

    return DetectionResult(
        "detected", value, sd, None, None, f"Fitted SNR at least {upper:g} with quantifiable area."
    )


def _rate(count: int, trials: int) -> dict[str, int | float | list[float] | None]:
    if trials == 0:
        return {"count": count, "trials": 0, "rate": None, "wilson95": None}
    interval = binomtest(count, trials).proportion_ci(method="wilson")
    return {"count": count, "trials": trials, "rate": count / trials, "wilson95": [interval.low, interval.high]}


def run_detection_calibration(config: Config) -> dict:
    """Run full-search threshold and upper-limit validation against known synthetic truth."""
    trials = int(setting(config, "qc", "calibration_trials"))
    levels = setting(config, "qc", "calibration_peak_snrs")
    thresholds = [
        float(setting(config, "qc", "censor_snr_candidate")),
        float(setting(config, "qc", "detect_snr_candidate")),
    ]
    metal_window = tuple(setting(config, "fit", "metal_window_ppm"))
    reference_window = tuple(setting(config, "fit", "reference_window_ppm"))
    base_seed = int(setting(config, "simulation", "seed"))
    confidence = float(setting(config, "qc", "upper_limit_confidence"))
    rows, bound_rows = [], []

    for level_index, level in enumerate(levels):
        raw_above = dict.fromkeys(thresholds, 0)
        accepted_above = dict.fromkeys(thresholds, 0)
        covered = censored_count = bounds_available = censored_covered = censored_bounded = 0
        for trial in range(trials):
            # An independent seed stream across SNR settings and replicates.
            seed = int(np.random.SeedSequence([base_seed, 2, level_index, trial]).generate_state(1)[0])
            spectrum, truth = simulate_spectrum(config, metal_snr=level, seed=seed)
            metal = fit_peak(spectrum, config, window_ppm=metal_window, sensitivity=False)
            reference = fit_peak(spectrum, config, window_ppm=reference_window, sensitivity=False)
            qc = assess_qc(spectrum, metal, reference, config, comparison_acquisition=None)
            result = classify(spectrum, metal, reference, qc, config)
            fit_snr = metal.fitted_snr
            for threshold in thresholds:
                if fit_snr is not None and fit_snr >= threshold:
                    raw_above[threshold] += 1
                    if _supports_detection(qc) and _area_and_sd(metal) is not None:
                        accepted_above[threshold] += 1

            bound = result.upper_limit
            if result.classification != "censored":
                bound, _ = upper_limit(spectrum, config)
            if bound is not None:
                bounds_available += 1
                covered += int(bound >= truth["rmdi"])
            if result.classification == "censored":
                censored_count += 1
                if bound is not None:
                    censored_bounded += 1
                    censored_covered += int(bound >= truth["rmdi"])

        for threshold in thresholds:
            rows.append(
                {
                    "input_snr": level,
                    "fitted_snr_threshold": threshold,
                    "quantity": "false_positive_rate" if level == 0 else "detection_rate",
                    "full_search": _rate(raw_above[threshold], trials),
                    "full_search_with_qc": _rate(accepted_above[threshold], trials),
                }
            )
        bound_rows.append(
            {
                "input_snr": level,
                "bound_availability": _rate(bounds_available, trials),
                "coverage_with_availability": _rate(covered, trials),
                "censored_trials": censored_count,
                "coverage_in_bounded_censored_trials": _rate(censored_covered, censored_bounded),
            }
        )
    return {
        "origin": "SIMULATED",
        "config_version": setting(config, "config_version"),
        "config_sha256": sha256_bytes(canonical_bytes(config)),
        "calibration_trials_per_input_snr": trials,
        "candidate_thresholds": rows,
        "upper_limit_nominal_confidence": confidence,
        "upper_limit_validation": bound_rows,
        "notes": [
            "The free peak center and width create a look-elsewhere effect. "
            "These rates are empirical under the full configured search and noise model.",
            "Rates after QC require usable fit, plausible peak position and acceptable residual structure.",
            "The upper bound assumes that the true Gaussian center is on the finite bank "
            "and its width equals the configured linewidth. The ratio also assumes the configured reference model.",
            "Coverage is nominal before the detection decision. The observed coverage among "
            "censored trials is reported separately.",
        ],
    }
