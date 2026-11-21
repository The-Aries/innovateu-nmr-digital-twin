"""Build and validate dossier-compatible cycling evidence packets."""

import json
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match

from .common import canonical_bytes, file_ref, setting, sha256_bytes
from .contracts import (
    Config, DetectionResult, EvidencePacket, JsonValue, ObjectRef, PeakFit,
    ProvenanceStep, QCResult, Spectrum, TwinAction,
)

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema/evidence_packet_v1.0.schema.json"
CHAIN_STEPS = ("preprocessing", "fit", "area", "qc")
ACQUISITION_FIELDS = (
    "field_strength_T", "spectrometer_frequency_MHz", "sequence", "TE_s", "TR_s",
    "averages", "spectral_width_ppm", "spectral_reference", "measurement_delay_s",
    "acquired_complex_points", "fourier_points", "noise_kind",
)
CONDITION_FIELDS = (
    "charge_current_mA", "discharge_protocol", "soc_start_pct", "soc_end_pct",
    "temperature_C", "voltage_limits_V",
)


def _area_sensitivity(fit: PeakFit) -> float | None:
    components = (fit.line_shape_area_shift_au_ppm, fit.window_area_shift_au_ppm)
    if any(component is None for component in components):
        return None
    return sum(component for component in components if component is not None)


def model_sensitivity(metal_fit: PeakFit, reference_fit: PeakFit | None) -> float | None:
    """Return model perturbation in the reported unit, separate from the fit SD."""
    metal_shift = _area_sensitivity(metal_fit)
    if reference_fit is None or metal_shift is None:
        return metal_shift
    ref_shift = _area_sensitivity(reference_fit)
    metal = metal_fit.peak_area_au_ppm
    ref = reference_fit.peak_area_au_ppm
    if metal is None or ref is None or ref_shift is None or ref <= ref_shift:
        return None
    central = metal / ref
    lower = max(0.0, metal - metal_shift) / (ref + ref_shift)
    upper = (metal + metal_shift) / (ref - ref_shift)
    return max(central - lower, upper - central)


def _recommended(spectrum: Spectrum, qc: QCResult, detection: DetectionResult) -> TwinAction:
    if spectrum.stage == "end_of_charge":
        return {"recommended": "reject", "reason": "End-of-charge context for the post-discharge twin"}
    if qc.status == "FAIL":
        return {"recommended": "reject", "reason": " ".join(qc.reasons) or detection.reason}
    if qc.status == "PASS" and qc.comparable is True and qc.protocol_match is True and detection.classification == "detected":
        return {"recommended": "update", "reason": detection.reason}
    return {"recommended": "update_with_warning", "reason": " ".join((*qc.reasons, detection.reason))}


def build_packet(
    spectrum: Spectrum,
    metal_fit: PeakFit,
    reference_fit: PeakFit | None,
    qc: QCResult,
    detection: DetectionResult,
    config: Config,
    *,
    provenance_steps: Sequence[ProvenanceStep],
) -> EvidencePacket:
    post_discharge = spectrum.stage == "post_discharge"
    observable = "rmdi" if post_discharge else "eoc_metal_area"
    packet_id = f"E-t{spectrum.cycle_n}-{observable}"
    subject = "".join(part for part in spectrum.cell_id if part.isascii() and part.isalnum())
    sensitivity = None
    if detection.classification == "detected" and (reference_fit is not None or not post_discharge):
        sensitivity = model_sensitivity(metal_fit, reference_fit if post_discharge else None)
    packet: EvidencePacket = {
        "packet_version": "1.0",
        "packet_id": packet_id,
        "subject_id": f"sub-{subject}",
        "cell_id": spectrum.cell_id,
        "session_id": spectrum.session_id,
        "cycle_n": spectrum.cycle_n,
        "relative_time": {"value": spectrum.relative_time_s, "unit": "s"},
        "modality": "MRS",
        "nucleus": "23Na",
        "measurement_stage": spectrum.stage,
        "observable": observable,
        "value": detection.value,
        "unit": "1" if post_discharge else "[arb'U].ppm",
        "detection_class": detection.classification,
        "upper_limit": detection.upper_limit,
        "upper_limit_method": detection.upper_limit_method,
        "model_sensitivity": sensitivity,
        "uncertainty": {
            "type": "SD" if detection.classification == "detected" else "category",
            "value": detection.standard_uncertainty,
            "budget_ref": "docs/uncertainty.md",
        },
        "qc_checks": list(qc.checks),
        "qc_status": qc.status,
        "qc_reasons": list(qc.reasons),
        "protocol_match": qc.protocol_match,
        "comparable": qc.comparable,
        "normalization_method": "external_reference_area" if post_discharge else "none",
        "origin": spectrum.origin,
        "value_epistemic": "DERIVED",
        "decision_epistemic": "INFERRED",
        "source_object": spectrum.source["path"],
        "source_sha256": spectrum.source["sha256"],
        "spatial_reference": {"frame": "named_region", "region": "coil-sensitive cell"},
        "acquisition_context": {
            key: spectrum.acquisition[key] for key in ACQUISITION_FIELDS
            if spectrum.acquisition.get(key) is not None
        },
        "cell_conditions": {key: spectrum.cell_conditions.get(key) for key in CONDITION_FIELDS},
        "system_qc_id": cast(str | None, spectrum.acquisition.get("system_qc_id")),
        "calibration_id": cast(str | None, spectrum.acquisition.get("calibration_id")),
        "thresholds_ref": f"config:{setting(config, 'config_version')}#qc",
        "processing": {
            "pipeline": "standalone-na23-rmdi",
            "version": setting(config, "pipeline_version"),
            "config_version": setting(config, "config_version"),
            "config_sha256": sha256_bytes(canonical_bytes(config)),
        },
        "provenance": {"parents": [spectrum.source], "activities": list(provenance_steps)},
        "twin_action": _recommended(spectrum, qc, detection),
        "interpretation_limit": (
            "Derived from a simulated spectrum. The observable describes relative NMR signal."
            if spectrum.origin == "SIMULATED"
            else "Derived from a measured spectrum. The observable describes relative NMR signal."
        ),
    }
    return validate_packet(cast(Mapping[str, JsonValue], packet))


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_packet(packet: Mapping[str, JsonValue]) -> EvidencePacket:
    canonical_bytes(packet)
    error = best_match(_validator().iter_errors(packet))
    if error:
        location = ".".join(map(str, error.absolute_path)) or "packet"
        raise ValueError(f"{location}: {error.message}")
    result = cast(EvidencePacket, packet)
    if result["packet_id"] != f"E-t{result['cycle_n']}-{result['observable']}":
        raise ValueError("Packet identifier disagrees with the cycle or observable")
    if len({check["name"] for check in result["qc_checks"]}) != len(result["qc_checks"]):
        raise ValueError("QC check names must be unique")
    if "valid_range" in result and result["valid_range"][0] >= result["valid_range"][1]:
        raise ValueError("Invalid observable range")
    parent = {"path": result["source_object"], "sha256": result["source_sha256"]}
    if parent not in result["provenance"]["parents"]:
        raise ValueError("The source spectrum is missing from the provenance parents")
    steps = [item["step"] for item in result["provenance"]["activities"]]
    if steps != [step for step in CHAIN_STEPS if step in steps]:
        raise ValueError("Duplicate or unordered provenance activities")
    if result["qc_status"] != "FAIL" and tuple(steps) != CHAIN_STEPS:
        raise ValueError("Usable evidence requires the complete provenance chain")
    levels = {"PASS": 0, "WARN": 1, "FAIL": 2}
    if max(levels[check["status"]] for check in result["qc_checks"]) != levels[result["qc_status"]]:
        raise ValueError("QC summary disagrees with the individual check results")
    return result


def verify_provenance(packet: EvidencePacket) -> None:
    """Verify artifact bytes and the links between successive stages."""
    parent: ObjectRef = {"path": packet["source_object"], "sha256": packet["source_sha256"]}
    for source in packet["provenance"]["parents"]:
        if file_ref(Path(source["path"])) != source:
            raise ValueError(f"Source digest mismatch at {source['path']}")
    for item in packet["provenance"]["activities"]:
        artifact = item["artifact"]
        path = Path(artifact["path"])
        data = path.read_bytes()
        if sha256_bytes(data) != artifact["sha256"]:
            raise ValueError(f"Artifact digest mismatch at {path}")
        entry = json.loads(data)
        if (
            entry["step"] != item["step"] or entry["input"] != parent
            or entry["origin"] != packet["origin"]
            or entry["config_version"] != packet["processing"]["config_version"]
            or entry["config_sha256"] != packet["processing"]["config_sha256"]
        ):
            raise ValueError(f"Broken provenance link at {path}")
        parent = artifact
