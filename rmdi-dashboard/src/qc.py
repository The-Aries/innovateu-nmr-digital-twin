"""Machine-readable acquisition, comparability, and fit checks."""

from collections.abc import Mapping
import math
from numbers import Real
from typing import Literal

import numpy as np

from .common import setting
from .contracts import Config, JsonValue, PeakFit, QCCheck, QCResult, QCStatus, Spectrum


ACQUISITION_NUMERIC = (
    "field_strength_T",
    "spectrometer_frequency_MHz",
    "TE_s",
    "TR_s",
    "averages",
    "spectral_width_ppm",
    "measurement_delay_s",
)
CELL_NUMERIC = ("charge_current_mA", "soc_start_pct", "soc_end_pct", "temperature_C")
COMPARABILITY_KEYS = (
    "field_strength_T",
    "spectrometer_frequency_MHz",
    "sequence",
    "TE_s",
    "TR_s",
    "averages",
    "spectral_width_ppm",
    "spectral_reference",
    "measurement_delay_s",
    "acquired_complex_points",
    "fourier_points",
    "noise_kind",
    "system_qc_id",
    "calibration_id",
    "charge_current_mA",
    "discharge_protocol",
    "soc_start_pct",
    "soc_end_pct",
    "temperature_C",
    "voltage_limits_V",
)


def _finite(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool) and math.isfinite(value)


def _positive(value: object) -> bool:
    return _finite(value) and float(value) > 0


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _metadata_issues(spectrum: Spectrum) -> list[str]:
    acquisition = spectrum.acquisition
    conditions = spectrum.cell_conditions
    issues = [key for key in ACQUISITION_NUMERIC if not _finite(acquisition.get(key))]
    issues.extend(
        key for key in ("sequence", "spectral_reference") if not _nonempty(acquisition.get(key))
    )
    issues.extend(key for key in CELL_NUMERIC if not _finite(conditions.get(key)))
    if not _nonempty(conditions.get("discharge_protocol")):
        issues.append("discharge_protocol")
    limits = conditions.get("voltage_limits_V")
    if (
        not isinstance(limits, (list, tuple))
        or len(limits) != 2
        or not all(_finite(item) for item in limits)
        or limits[0] >= limits[1]
    ):
        issues.append("voltage_limits_V")
    if not _finite(spectrum.relative_time_s) or spectrum.relative_time_s < 0:
        issues.append("relative_time_s")
    return issues


def _check(
    name: str,
    value: str | float | bool | None,
    unit: str,
    threshold: str,
    status: QCStatus,
    owner: Literal["QE", "PM", "DS", "DT", "shared"],
) -> QCCheck:
    return {
        "name": name,
        "value": value,
        "unit": unit,
        "threshold": threshold,
        "status": status,
        "owner": owner,
    }


def assess_qc(
    spectrum: Spectrum,
    metal_fit: PeakFit,
    reference_fit: PeakFit | None,
    config: Config,
    *,
    comparison_acquisition: Mapping[str, JsonValue] | None,
) -> QCResult:
    """Apply acquisition rules separately from the detection classification."""
    issues = _metadata_issues(spectrum)
    checks = [
        _check(
            "metadata_completeness",
            ", ".join(issues) if issues else "complete",
            "1",
            "Required acquisition and cell-condition fields present",
            "FAIL" if issues else "PASS",
            "PM",
        )
    ]
    reasons = [f"Missing or invalid metadata: {', '.join(issues)}."] if issues else []

    fields = {**spectrum.acquisition, **spectrum.cell_conditions}
    changed = []
    if comparison_acquisition is not None:
        changed = [
            key
            for key in COMPARABILITY_KEYS
            if key in comparison_acquisition and comparison_acquisition[key] != fields.get(key)
        ]
    match = None if issues else not changed
    if changed:
        reasons.append(f"Acquisition or cell protocol differs from baseline: {', '.join(changed)}.")
    checks.append(
        _check(
            "protocol_comparability",
            ", ".join(changed) if changed else match,
            "1",
            "Exact match to baseline protocol fields when baseline evidence is available",
            "WARN" if changed or issues else "PASS",
            "PM",
        )
    )

    fit_converged = metal_fit.fit_status == "converged"
    checks.append(
        _check("fit_convergence", fit_converged, "1", "Optimizer converged", "PASS" if fit_converged else "FAIL", "QE")
    )
    if not fit_converged:
        reasons.append("Metal-region fit did not converge.")

    snr = metal_fit.fitted_snr
    snr_valid = _finite(snr) and snr >= 0
    censor_threshold = float(setting(config, "qc", "censor_snr_candidate"))
    detect_threshold = float(setting(config, "qc", "detect_snr_candidate"))
    checks.append(
        _check(
            "fitted_snr",
            float(snr) if snr_valid else None,
            "1",
            f"Finite nonnegative SNR, with detection thresholds {censor_threshold:g} and {detect_threshold:g}",
            "PASS" if snr_valid else "FAIL",
            "QE",
        )
    )
    if not snr_valid:
        reasons.append("Fitted signal-to-noise ratio is unavailable.")

    center = metal_fit.peak_center_ppm
    window_low, window_high = metal_fit.window_ppm
    center_low, center_high = setting(config, "qc", "metal_center_bounds_ppm")
    center_inside_window = _finite(center) and window_low <= center <= window_high
    above_censor_threshold = snr_valid and snr >= censor_threshold
    plausible = _finite(center) and (not above_censor_threshold or center_low <= center <= center_high)
    center_status = "PASS" if center_inside_window and plausible else "WARN"
    checks.append(
        _check(
            "peak_position",
            float(center) if _finite(center) else None,
            "ppm",
            f"Within fit window and between {center_low:g} and {center_high:g} ppm at SNR ≥ {censor_threshold:g}",
            center_status,
            "QE",
        )
    )
    if center_status == "WARN":
        reasons.append("A fitted peak position falls outside its declared spectral range or is unresolved.")

    residual = np.asarray(metal_fit.residual_au, dtype=float)
    lag_limit = float(setting(config, "qc", "residual_lag1_max"))
    lag1 = None
    if residual.ndim == 1 and residual.size > 2 and np.all(np.isfinite(residual)):
        centered = residual - residual.mean()
        energy = float(centered @ centered)
        if energy > 0:
            lag1 = float(centered[:-1] @ centered[1:] / energy)
    residual_status = "FAIL" if lag1 is None else ("WARN" if abs(lag1) > lag_limit else "PASS")
    checks.append(
        _check(
            "baseline_residual_lag1",
            lag1,
            "1",
            f"Absolute lag-1 correlation ≤ {lag_limit:g} on the native fit grid",
            residual_status,
            "QE",
        )
    )
    if residual_status != "PASS":
        reasons.append("Fit residuals show serial structure or cannot be assessed.")

    if spectrum.stage == "post_discharge":
        reference_min = float(setting(config, "qc", "reference_min_snr"))
        reference_snr = reference_fit.fitted_snr if reference_fit else None
        reference_ok = (
            reference_fit is not None
            and reference_fit.fit_status == "converged"
            and _positive(reference_fit.peak_area_au_ppm)
            and _positive(reference_fit.peak_area_u_au_ppm)
            and _finite(reference_snr)
            and reference_snr >= reference_min
        )
        checks.append(
            _check(
                "reference_fit",
                float(reference_snr) if _finite(reference_snr) else None,
                "1",
                f"Converged positive reference area with quantified uncertainty and SNR ≥ {reference_min:g}",
                "PASS" if reference_ok else "FAIL",
                "QE",
            )
        )
        if not reference_ok:
            reasons.append("The reference fit does not support a normalized RMDI.")

    statuses = {check["status"] for check in checks}
    status = "FAIL" if "FAIL" in statuses else ("WARN" if "WARN" in statuses else "PASS")
    return QCResult(
        status=status,
        checks=tuple(checks),
        reasons=tuple(reasons),
        protocol_match=match,
        comparable=match if status != "FAIL" else None,
    )
