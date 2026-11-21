"""Fit a metal or reference line and quantify its measurement sensitivity."""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np
from scipy.optimize import OptimizeWarning, curve_fit

from .common import setting
from .contracts import Config, PeakFit, PpmWindow, Spectrum
from .sim import FWHM_PER_SIGMA, GAUSSIAN_AREA_FACTOR

PARAMETER_ORDER = ("height_au", "center_ppm", "sigma_ppm", "baseline_au", "baseline_slope_au_per_ppm")


def independent_points(spectrum: Spectrum, window_ppm: PpmWindow) -> tuple[np.ndarray, np.ndarray]:
    """Select independent native FFT bins for supported synthetic noise models."""
    lo, hi = window_ppm
    ppm, intensity = spectrum.ppm, spectrum.intensity_au
    if not lo < hi or len(ppm) < 2 or ppm.shape != intensity.shape:
        raise ValueError("A fit requires an ordered ppm window and matching data vectors")
    if not np.all(np.isfinite(ppm)) or not np.all(np.isfinite(intensity)):
        raise ValueError("Spectrum contains a non-finite value")
    gaps = np.diff(ppm)
    if gaps[0] <= 0 or not np.allclose(gaps, gaps[0]):
        raise ValueError("Only increasing, uniformly sampled spectra are supported")

    stride = 1
    noise_kind = spectrum.acquisition.get("noise_kind")
    if noise_kind == "zero_filled":
        acquired = spectrum.acquisition.get("acquired_complex_points")
        fourier = spectrum.acquisition.get("fourier_points")
        if not isinstance(acquired, int) or acquired < 1 or fourier != len(ppm) or len(ppm) % acquired:
            raise ValueError("Zero-filled spectrum lacks a consistent native grid")
        # For an integral zero-fill factor, periodic native samples are a
        # separately normalized DFT of the original complex white noise.
        stride = len(ppm) // acquired
    elif noise_kind != "white":
        raise ValueError("An explicit supported noise model is required")
    ppm, intensity = ppm[::stride], intensity[::stride]
    mask = (ppm >= lo) & (ppm <= hi)
    return ppm[mask], intensity[mask]


def gaussian_area(height: float, sigma: float) -> float:
    """Integral of a unit-baseline-subtracted Gaussian over the real line."""
    return float(height * sigma * GAUSSIAN_AREA_FACTOR)


def gaussian_area_uncertainty(height: float, sigma: float, covariance: np.ndarray) -> float:
    """Delta-method standard uncertainty, including height–width covariance."""
    gradient = np.zeros(covariance.shape[0], dtype=float)
    gradient[0] = sigma * GAUSSIAN_AREA_FACTOR
    gradient[2] = height * GAUSSIAN_AREA_FACTOR
    variance = float(gradient @ covariance @ gradient)
    return float(np.sqrt(max(variance, 0.0)))


@dataclass(frozen=True)
class _GaussianSolution:
    parameters: np.ndarray
    covariance: np.ndarray
    residual: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    pivot_ppm: float
    scale_ppm: float


def _gaussian_fit(
    x: np.ndarray, y: np.ndarray, window: PpmWindow, expected_sigma: float,
) -> _GaussianSolution:
    n_parameters = len(PARAMETER_ORDER)
    if len(x) <= n_parameters:
        raise ValueError("Too few independent spectral points in the fit window")
    lo, hi = window
    pivot = (lo + hi) / 2
    scale = (hi - lo) / 2
    step = x[1] - x[0]
    if step >= scale:
        raise ValueError("Fit window is too narrow to resolve the line width")
    lower = np.array([0, lo, step, -np.inf, -np.inf])
    upper = np.array([np.inf, hi, scale, np.inf, np.inf])

    def model(ppm, height, center, sigma, intercept, slope):
        distance = (ppm - center) / sigma
        return height * np.exp(-0.5 * distance**2) + intercept + slope * (ppm - pivot) / scale

    def jacobian(ppm, height, center, sigma, intercept, slope):
        distance = (ppm - center) / sigma
        shape = np.exp(-0.5 * distance**2)
        return np.column_stack((
            shape,
            height * shape * distance / sigma,
            height * shape * distance**2 / sigma,
            np.ones_like(ppm),
            (ppm - pivot) / scale,
        ))

    sigma = np.clip(expected_sigma, step, scale)
    baseline = np.column_stack((np.ones_like(x), (x - pivot) / scale))
    basis, _ = np.linalg.qr(baseline)
    # Initialize from the strongest baseline-adjusted Gaussian template.
    # The actual fit refines the center and width together.
    templates = np.exp(-0.5 * ((x[:, None] - x[None, :]) / sigma) ** 2)
    residual_templates = templates - basis @ (basis.T @ templates)
    template_scores = (y @ residual_templates) / np.linalg.norm(residual_templates, axis=0)
    index = int(np.argmax(template_scores))
    height, intercept, slope = np.linalg.lstsq(
        np.column_stack((templates[:, index], baseline)), y, rcond=None
    )[0]
    initial = [max(0, height), x[index], sigma, intercept, slope]
    with warnings.catch_warnings():
        warnings.simplefilter("error", OptimizeWarning)
        params, covariance = curve_fit(model, x, y, p0=initial, bounds=(lower, upper), jac=jacobian)
    residual = y - model(x, *params)
    if not np.all(np.isfinite(covariance)):
        raise ValueError("Fit covariance could not be estimated")
    return _GaussianSolution(params, covariance, residual, lower, upper, pivot, scale)


def _pseudo_voigt_area(x: np.ndarray, y: np.ndarray, primary: _GaussianSolution) -> float:
    half_fwhm_over_sigma = FWHM_PER_SIGMA / 2

    def model(ppm, height, center, sigma, intercept, slope, fraction):
        distance = (ppm - center) / sigma
        gaussian = np.exp(-0.5 * distance**2)
        lorentzian = 1 / (1 + (distance / half_fwhm_over_sigma) ** 2)
        profile = (1 - fraction) * gaussian + fraction * lorentzian
        return height * profile + intercept + slope * (ppm - primary.pivot_ppm) / primary.scale_ppm

    params, _ = curve_fit(
        model, x, y, p0=[*primary.parameters, 0.5],
        bounds=(np.r_[primary.lower, 0], np.r_[primary.upper, 1]),
    )
    height, _, sigma, _, _, fraction = params
    factor = (1 - fraction) * GAUSSIAN_AREA_FACTOR + fraction * np.pi * half_fwhm_over_sigma
    return float(height * sigma * factor)


def _failure(window_ppm: PpmWindow, reason: str) -> PeakFit:
    return PeakFit(
        fit_status="failed",
        window_ppm=window_ppm,
        parameter_order=PARAMETER_ORDER,
        parameters=None,
        covariance=None,
        residual_au=np.array([], dtype=float),
        peak_center_ppm=None,
        peak_center_u_ppm=None,
        peak_area_au_ppm=None,
        peak_area_u_au_ppm=None,
        fitted_snr=None,
        line_shape_area_shift_au_ppm=None,
        window_area_shift_au_ppm=None,
        reason=reason,
    )


def fit_peak(
    spectrum: Spectrum, config: Config, *, window_ppm: PpmWindow, sensitivity: bool = True,
) -> PeakFit:
    """Fit one peak, report the full covariance and optional area sensitivities."""
    midpoint = sum(window_ppm) / 2
    metal_center = setting(config, "simulation", "metal_center_ppm")
    reference_center = setting(config, "simulation", "reference_center_ppm")
    if abs(midpoint - metal_center) <= abs(midpoint - reference_center):
        width = setting(config, "simulation", "metal_fwhm_ppm")
    else:
        scenario = setting(config, "simulation", "trajectory_protocol_and_noise")
        width = scenario["reference_fwhm_ppm"]
    expected_sigma = width / FWHM_PER_SIGMA

    try:
        x, y = independent_points(spectrum, window_ppm)
        primary = _gaussian_fit(x, y, window_ppm, expected_sigma)
    except (RuntimeError, ValueError, OptimizeWarning, np.linalg.LinAlgError) as exc:
        return _failure(window_ppm, str(exc))

    # Return slope in intensity units per ppm rather than per window half-width.
    transform = np.diag([1, 1, 1, 1, 1 / primary.scale_ppm])
    params = transform @ primary.parameters
    cov = transform @ primary.covariance @ transform.T
    height, center, sigma, _, _ = params
    noise_sd = np.linalg.norm(primary.residual) / np.sqrt(len(x) - len(params))
    if not np.isfinite(noise_sd) or noise_sd <= 0:
        return _failure(window_ppm, "Residual noise is unavailable")
    area = gaussian_area(height, sigma)

    line_shape_shift = window_shift = None
    if sensitivity:
        try:
            line_shape_shift = abs(area - _pseudo_voigt_area(x, y, primary))
        except (RuntimeError, ValueError, OptimizeWarning, np.linalg.LinAlgError):
            pass
        fraction = setting(config, "fit", "window_sensitivity_fraction")
        shifts = []
        for scale in (1 - fraction, 1 + fraction):
            half_width = primary.scale_ppm * scale
            window = (midpoint - half_width, midpoint + half_width)
            try:
                wx, wy = independent_points(spectrum, window)
                variant = _gaussian_fit(wx, wy, window, expected_sigma)
                shifts.append(abs(area - gaussian_area(variant.parameters[0], variant.parameters[2])))
            except (RuntimeError, ValueError, OptimizeWarning, np.linalg.LinAlgError):
                break
        if len(shifts) == 2:
            window_shift = max(shifts)

    return PeakFit(
        fit_status="converged",
        window_ppm=window_ppm,
        parameter_order=PARAMETER_ORDER,
        parameters=params,
        covariance=cov,
        residual_au=primary.residual,
        peak_center_ppm=float(center),
        peak_center_u_ppm=float(np.sqrt(max(cov[1, 1], 0.0))),
        peak_area_au_ppm=area,
        peak_area_u_au_ppm=gaussian_area_uncertainty(height, sigma, cov),
        fitted_snr=float(height / noise_sd),
        line_shape_area_shift_au_ppm=line_shape_shift,
        window_area_shift_au_ppm=window_shift,
        reason=None,
    )
