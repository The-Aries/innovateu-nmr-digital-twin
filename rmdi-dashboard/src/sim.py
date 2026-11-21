"""Reproducible ²³Na spectra for the synthetic cycling case."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import numpy as np

from .common import canonical_bytes, setting, sha256_bytes, write_json
from .contracts import Config, ObjectRef, SimulationRun, Spectrum, Stage

FWHM_PER_SIGMA = 2 * np.sqrt(2 * np.log(2))
GAUSSIAN_AREA_FACTOR = np.sqrt(2 * np.pi)
LineShape = Literal["gaussian", "lorentzian"]


def _spectral_noise(
    rng: np.random.Generator, acquired: int, size: int, sd: float, correlated: bool
) -> np.ndarray:
    if not correlated:
        return rng.normal(0, sd, size)
    # Complex IID time noise generates a real spectrum with the requested
    # marginal SD. Native FFT points remain independent after zero filling.
    time_noise = rng.normal(size=acquired) + 1j * rng.normal(size=acquired)
    return np.fft.fftshift(np.fft.fft(time_noise, n=size)).real * sd / np.sqrt(acquired)


def _spectrum_from_document(document: dict[str, Any], source: ObjectRef) -> Spectrum:
    ppm = np.asarray(document["ppm"], dtype=float)
    intensity = np.asarray(document["intensity_au"], dtype=float)
    if ppm.ndim != 1 or ppm.shape != intensity.shape:
        raise ValueError("Spectrum and ppm axis must be equal-length vectors")
    return Spectrum(
        cell_id=document["cell_id"],
        session_id=document["session_id"],
        cycle_n=document["cycle_n"],
        stage=document["stage"],
        relative_time_s=document["relative_time_s"],
        origin=document["origin"],
        ppm=ppm,
        intensity_au=intensity,
        acquisition=document["acquisition"],
        cell_conditions=document["cell_conditions"],
        source=source,
    )


def _generate_document(
    config: Config,
    cycle_n: int,
    stage: Stage,
    metal_snr: float | None,
    seed: int | None,
    correlated_noise: bool | None,
    line_shape: LineShape,
    invalid: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if cycle_n < 1 or stage not in ("end_of_charge", "post_discharge"):
        raise ValueError("Expected a positive cycle number and a valid measurement stage")
    if line_shape not in ("gaussian", "lorentzian"):
        raise ValueError("Unsupported synthetic metal line shape")

    scenario = setting(config, "simulation", "trajectory_protocol_and_noise")
    stage_index = int(stage == "post_discharge")
    schedule = scenario["post_snr" if stage_index else "eoc_snr"]
    if metal_snr is None:
        metal_snr = schedule[cycle_n - 1]
    if not np.isfinite(metal_snr) or metal_snr < 0:
        raise ValueError("Synthetic SNR must be finite and nonnegative")

    seed = setting(config, "simulation", "seed") if seed is None else seed
    rng = np.random.default_rng(np.random.SeedSequence([seed, cycle_n, stage_index]))
    correlated = scenario["correlated_noise"] if correlated_noise is None else correlated_noise
    acquired = setting(config, "simulation", "acquired_complex_points")
    size = setting(config, "simulation", "fourier_points") if correlated else acquired
    if acquired < 1 or size < acquired or size % acquired:
        raise ValueError("Simulation requires an integral zero-fill factor")
    span = setting(config, "simulation", "spectral_width_ppm")
    ppm = scenario["ppm_axis_center"] + np.fft.fftshift(np.fft.fftfreq(size, d=1 / span))
    noise_sd = scenario["noise_sd_au"]

    metal_center = setting(config, "simulation", "metal_center_ppm")
    metal_fwhm = setting(config, "simulation", "metal_fwhm_ppm")
    metal_sigma = metal_fwhm / FWHM_PER_SIGMA
    metal_height = metal_snr * noise_sd
    if line_shape == "lorentzian":
        metal = metal_height / (1 + ((ppm - metal_center) / (metal_fwhm / 2)) ** 2)
        metal_area = metal_height * np.pi * metal_fwhm / 2
    else:
        metal = metal_height * np.exp(-0.5 * ((ppm - metal_center) / metal_sigma) ** 2)
        metal_area = metal_height * GAUSSIAN_AREA_FACTOR * metal_sigma

    reference_center = setting(config, "simulation", "reference_center_ppm")
    reference_sigma = scenario["reference_fwhm_ppm"] / FWHM_PER_SIGMA
    reference_area = scenario["reference_area_au_ppm"]
    reference_height = reference_area / (GAUSSIAN_AREA_FACTOR * reference_sigma)
    reference = reference_height * np.exp(-0.5 * ((ppm - reference_center) / reference_sigma) ** 2)
    baseline = scenario["baseline_offset_au"] + scenario["baseline_slope_au_per_ppm"] * ppm
    intensity = baseline + metal + reference + _spectral_noise(rng, acquired, size, noise_sd, correlated)
    delay = scenario["measurement_delay_s"]
    period = scenario["cycle_period_s"]
    relative_time = (cycle_n - 1 + (1 if stage_index else 0.5)) * period + delay
    config_version = setting(config, "config_version")
    config_digest = sha256_bytes(canonical_bytes(config))
    session_id = f"ses-{cycle_n}{'P' if stage_index else 'E'}"
    document = {
        "config_version": config_version,
        "config_sha256": config_digest,
        "cell_id": "cell-na23-sim",
        "session_id": session_id,
        "cycle_n": cycle_n,
        "stage": stage,
        "relative_time_s": relative_time,
        "origin": "SIMULATED",
        "ppm": ppm.tolist(),
        "intensity_au": intensity.tolist(),
        "acquisition": {
            "field_strength_T": scenario["field_strength_T"],
            "spectrometer_frequency_MHz": scenario["spectrometer_frequency_MHz"],
            "sequence": None if invalid else scenario["sequence"],
            "TE_s": scenario["TE_s"],
            "TR_s": scenario["TR_s"],
            "averages": scenario["averages"],
            "spectral_width_ppm": span,
            "spectral_reference": "simulated external aqueous NaCl",
            "measurement_delay_s": delay,
            "acquired_complex_points": acquired,
            "fourier_points": size,
            "noise_kind": "zero_filled" if correlated else "white",
            "system_qc_id": "simulated-system-qc",
            "calibration_id": "simulated-reference",
        },
        "cell_conditions": {
            "charge_current_mA": scenario["charge_current_mA"],
            "discharge_protocol": scenario["discharge_protocol"],
            "soc_start_pct": scenario["soc_start_pct"],
            "soc_end_pct": scenario["discharge_end_soc_pct"] if stage_index else scenario["charge_end_soc_pct"],
            "temperature_C": scenario["temperature_C"],
            "voltage_limits_V": scenario["voltage_limits_V"],
        },
    }
    truth = {
        "origin": "SIMULATED",
        "session_id": session_id,
        "cycle_n": cycle_n,
        "stage": stage,
        "line_shape": line_shape,
        "metal_peak_area_au_ppm": float(metal_area),
        "reference_area_au_ppm": reference_area,
        "rmdi": float(metal_area / reference_area) if stage_index else None,
        "nominal_metal_snr": metal_snr,
        "noise_sd_au": noise_sd,
        "invalid_metadata": invalid,
    }
    return document, truth


def simulate_spectrum(
    config: Config,
    *,
    cycle_n: int = 1,
    stage: Stage = "post_discharge",
    metal_snr: float | None = None,
    seed: int | None = None,
    correlated_noise: bool | None = None,
    line_shape: LineShape = "gaussian",
    invalid: bool = False,
) -> tuple[Spectrum, dict[str, Any]]:
    """Return an in-memory observation and its separate validation truth."""
    document, truth = _generate_document(
        config, cycle_n, stage, metal_snr, seed, correlated_noise, line_shape, invalid
    )
    source = {
        "path": f"memory/{document['session_id']}.json",
        "sha256": sha256_bytes(canonical_bytes(document)),
    }
    return _spectrum_from_document(document, source), truth


def load_spectrum(path: Path) -> Spectrum:
    raw = path.read_bytes()
    return _spectrum_from_document(json.loads(raw), {"path": str(path), "sha256": sha256_bytes(raw)})


def simulate(config: Config, *, output_dir: Path) -> SimulationRun:
    """Write source spectra and a separately stored truth artifact."""
    scenario = setting(config, "simulation", "trajectory_protocol_and_noise")
    count = setting(config, "simulation", "cycle_count")
    if len(scenario["eoc_snr"]) != count or len(scenario["post_snr"]) != count:
        raise ValueError("Each simulated stage needs one SNR entry per cycle")
    sources: list[ObjectRef] = []
    rows = []
    for cycle in range(1, count + 1):
        for stage in ("end_of_charge", "post_discharge"):
            invalid = stage == "post_discharge" and cycle == scenario["invalid_cycle"]
            data, truth = _generate_document(config, cycle, stage, None, None, None, "gaussian", invalid)
            filename = f"{data['session_id']}.json"
            source = write_json(output_dir / "spectra" / filename, data)
            sources.append(source)
            rows.append({**truth, "source": {"path": f"spectra/{filename}", "sha256": source["sha256"]}})
    version = setting(config, "config_version")
    digest = sha256_bytes(canonical_bytes(config))
    truth_source = write_json(
        output_dir / "truth" / "deposition.json",
        {"origin": "SIMULATED", "config_version": version, "config_sha256": digest, "observations": rows},
    )
    return SimulationRun(tuple(sources), truth_source, version, digest)
