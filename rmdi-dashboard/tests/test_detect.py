"""Regression checks for detection eligibility and the reported censoring bound."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from src.common import load_config, setting
from src.detect import classify, upper_limit
from src.fit import fit_peak
from src.qc import assess_qc
from src.sim import simulate_spectrum


@pytest.fixture(scope="module")
def measurement():
    config = load_config(Path(__file__).resolve().parents[1] / "config.yaml")
    spectrum, truth = simulate_spectrum(config, metal_snr=40)
    metal_window = tuple(setting(config, "fit", "metal_window_ppm"))
    ref_window = tuple(setting(config, "fit", "reference_window_ppm"))
    metal = fit_peak(spectrum, config, window_ppm=metal_window, sensitivity=False)
    reference = fit_peak(spectrum, config, window_ppm=ref_window, sensitivity=False)
    return config, spectrum, truth, metal, reference


def test_detected_ratio_uncertainty_uses_metal_and_reference(measurement):
    config, spectrum, _, metal, reference = measurement
    qc = assess_qc(spectrum, metal, reference, config, comparison_acquisition=None)
    result = classify(spectrum, metal, reference, qc, config)
    area, ref_area = metal.peak_area_au_ppm, reference.peak_area_au_ppm
    assert qc.status == "PASS"
    assert len({check["name"] for check in qc.checks}) >= 5
    assert all({"value", "unit", "threshold", "status", "owner"} <= check.keys() for check in qc.checks)
    assert result.classification == "detected"
    assert result.value == pytest.approx(area / ref_area)
    assert result.standard_uncertainty == pytest.approx(
        np.hypot(metal.peak_area_u_au_ppm / ref_area, area * reference.peak_area_u_au_ppm / ref_area**2)
    )


@pytest.mark.parametrize(
    ("snr", "classification"),
    [(2.99, "censored"), (3.0, "uncertain"), (4.99, "uncertain"), (5.0, "detected")],
)
def test_snr_boundaries_preserve_qc_and_do_not_quantify_weak_peaks(measurement, snr, classification):
    config, spectrum, _, metal, reference = measurement
    assessed_fit = replace(metal, fitted_snr=snr)
    qc = assess_qc(spectrum, assessed_fit, reference, config, comparison_acquisition=None)
    result = classify(spectrum, assessed_fit, reference, qc, config)
    assert qc.status == "PASS"
    assert result.classification == classification
    if classification in {"censored", "uncertain"}:
        assert result.value is None
        assert result.standard_uncertainty is None
    if classification == "censored":
        assert result.upper_limit > 0
        assert "RMDI_UL" in result.upper_limit_method


def test_missing_acquisition_metadata_is_invalid(measurement):
    config, spectrum, _, metal, reference = measurement
    incomplete = replace(spectrum, acquisition={**spectrum.acquisition, "sequence": None})
    qc = assess_qc(incomplete, metal, reference, config, comparison_acquisition=None)
    result = classify(incomplete, metal, reference, qc, config)
    assert qc.status == "FAIL"
    assert result.classification == "invalid"
    assert result.value is None
    assert result.upper_limit is None


def test_change_in_sensitivity_marks_comparability_warning(measurement):
    config, spectrum, _, metal, reference = measurement
    baseline = {**spectrum.acquisition, **spectrum.cell_conditions, "averages": 512}
    qc = assess_qc(spectrum, metal, reference, config, comparison_acquisition=baseline)
    result = classify(spectrum, metal, reference, qc, config)
    assert qc.status == "WARN"
    assert qc.protocol_match is False
    assert qc.comparable is False
    assert any("averages" in reason for reason in qc.reasons)
    assert result.classification == "detected"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"peak_center_ppm": 1195.0}, "range"),
        ({"residual_au": np.linspace(-1, 1, 30)}, "serial structure"),
    ],
)
def test_implausible_fit_keeps_result_uncertain(measurement, changes, reason):
    config, spectrum, _, metal, reference = measurement
    implausible = replace(metal, **changes)
    qc = assess_qc(spectrum, implausible, reference, config, comparison_acquisition=None)
    result = classify(spectrum, implausible, reference, qc, config)
    assert qc.status == "WARN"
    assert any(reason in entry for entry in qc.reasons)
    assert result.classification == "uncertain"
    assert result.value is None


def test_upper_limit_model_scope(measurement):
    config, spectrum, truth, _, _ = measurement
    limit, method = upper_limit(spectrum, config)
    assert limit >= truth["rmdi"]
    assert "finite-bank Gaussian" in method
    assert upper_limit(replace(spectrum, origin="MEASURED"), config) == (None, None)
