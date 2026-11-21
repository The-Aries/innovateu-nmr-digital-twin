"""Known-truth checks for the standalone simulator and fitter."""

import json
from math import sqrt
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pytest
from scipy.integrate import quad

from src.common import load_config, setting
from src.fit import fit_peak, gaussian_area, gaussian_area_uncertainty, independent_points
from src.sim import load_spectrum, simulate, simulate_spectrum

CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"


def test_gaussian_area_and_full_covariance():
    height, sigma = 2.5, 4.0
    expected, _ = quad(lambda x: height * np.exp(-0.5 * (x / sigma) ** 2), -np.inf, np.inf)
    assert gaussian_area(height, sigma) == pytest.approx(expected)
    covariance = np.zeros((5, 5))
    covariance[0, 0], covariance[2, 2] = 0.16, 0.25
    covariance[0, 2] = covariance[2, 0] = -0.10
    relative_variance = (
        covariance[0, 0] / height**2
        + covariance[2, 2] / sigma**2
        + 2 * covariance[0, 2] / (height * sigma)
    )
    assert gaussian_area_uncertainty(height, sigma, covariance) == pytest.approx(
        expected * sqrt(relative_variance)
    )


def test_simulation_reproducibility_and_truth_isolation(tmp_path):
    config = load_config(CONFIG)
    original = simulate(config, output_dir=tmp_path / "first")
    repeated = simulate(config, output_dir=tmp_path / "second")
    assert len(original.spectrum_sources) == 2 * setting(config, "simulation", "cycle_count")
    assert [ref["sha256"] for ref in original.spectrum_sources] == [
        ref["sha256"] for ref in repeated.spectrum_sources
    ]
    assert original.truth_source["sha256"] == repeated.truth_source["sha256"]
    example = Path(original.spectrum_sources[1]["path"])
    document = json.loads(example.read_text())
    assert document["origin"] == "SIMULATED"
    assert {"rmdi", "nominal_metal_snr", "true_area", "truth", "metal_peak_area_au_ppm"}.isdisjoint(document)
    assert load_spectrum(example).source == original.spectrum_sources[1]
    truth = json.loads(Path(original.truth_source["path"]).read_text())
    assert truth["observations"][1]["metal_peak_area_au_ppm"] == 0
    assert truth["observations"][1]["origin"] == "SIMULATED"


@pytest.mark.parametrize("correlated", [False, True], ids=["iid", "zero-filled"])
def test_gaussian_area_coverage(correlated):
    config = load_config(CONFIG)
    window = tuple(setting(config, "fit", "metal_window_ppm"))
    base_seed = setting(config, "simulation", "seed")
    trials = setting(config, "fit", "coverage_trials_per_case")
    targets = setting(config, "fit", "coverage_targets")
    assert trials >= 1000
    factors = [NormalDist().inv_cdf((1 + target) / 2) for target in targets]
    counts = np.zeros(len(targets), dtype=int)
    fit_failures = 0
    for trial in range(trials):
        # Strong isolated Gaussian signal is the regime where the local delta
        # method is expected to work. Threshold behavior is checked in M2.
        spectrum, truth = simulate_spectrum(
            config, metal_snr=40, seed=base_seed + trial, correlated_noise=correlated
        )
        fitted = fit_peak(spectrum, config, window_ppm=window, sensitivity=False)
        if fitted.peak_area_au_ppm is None or not fitted.peak_area_u_au_ppm:
            fit_failures += 1
            continue
        standardized = abs(fitted.peak_area_au_ppm - truth["metal_peak_area_au_ppm"]) / fitted.peak_area_u_au_ppm
        counts += standardized <= np.asarray(factors)

    # Treat a failed fit as uncovered rather than dropping it from the sample.
    print(f"M1 {'zero-filled native grid' if correlated else 'IID'} trials={trials} fit_failures={fit_failures}")
    for target, count in zip(targets, counts):
        observed = count / trials
        sampling_se = sqrt(target * (1 - target) / trials)
        print(f"  target={target:.2%} observed={observed:.2%} MC_SE={sampling_se:.2%}")
        assert abs(observed - target) <= 3 * sampling_se


def test_window_and_line_shape_sensitivity_and_center_uncertainty():
    config = load_config(CONFIG)
    window = tuple(setting(config, "fit", "metal_window_ppm"))
    spectrum, truth = simulate_spectrum(config, metal_snr=40, line_shape="lorentzian")
    fitted = fit_peak(spectrum, config, window_ppm=window)
    assert fitted.fit_status == "converged"
    assert fitted.peak_center_u_ppm == pytest.approx(np.sqrt(fitted.covariance[1, 1]))
    assert fitted.line_shape_area_shift_au_ppm > 0
    assert fitted.window_area_shift_au_ppm > 0
    thin_window = (window[0] + 5, window[1] - 5)
    changed = fit_peak(spectrum, config, window_ppm=thin_window, sensitivity=False)
    assert changed.fit_status == "converged"
    assert changed.peak_area_au_ppm != pytest.approx(fitted.peak_area_au_ppm)
    x, _ = independent_points(spectrum, window)
    assert len(fitted.residual_au) == len(x)
    assert len(x) < count_in_window(spectrum.ppm, window)
    print(
        f"M1 Lorentzian truth={truth['metal_peak_area_au_ppm']:.2f} "
        f"Gaussian area={fitted.peak_area_au_ppm:.2f} ± {fitted.peak_area_u_au_ppm:.2f} a.u.·ppm "
        f"|Gaussian−pseudo-Voigt|={fitted.line_shape_area_shift_au_ppm:.2f} "
        f"max window shift={fitted.window_area_shift_au_ppm:.2f} a.u.·ppm "
        f"(independent bins={len(x)})"
    )


def count_in_window(ppm, window):
    return np.count_nonzero((ppm >= window[0]) & (ppm <= window[1]))
