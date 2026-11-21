"""Shared types for the standalone ²³Na RMDI workflow."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, NotRequired, TypeAlias, TypedDict

import numpy as np
from numpy.typing import NDArray

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
Config: TypeAlias = Mapping[str, JsonValue]
Stage: TypeAlias = Literal["end_of_charge", "post_discharge"]
Origin: TypeAlias = Literal["MEASURED", "SIMULATED"]
QCStatus: TypeAlias = Literal["PASS", "WARN", "FAIL"]
Detection: TypeAlias = Literal["detected", "uncertain", "censored", "invalid"]
Action: TypeAlias = Literal["update", "update_with_warning", "reject"]
HealthTrend: TypeAlias = Literal["deteriorating", "stable", "undetermined"]
PpmWindow: TypeAlias = tuple[float, float]
FloatArray: TypeAlias = NDArray[np.float64]

class ObjectRef(TypedDict):
    path: str
    sha256: str

class ProvenanceStep(TypedDict):
    step: Literal["preprocessing", "fit", "area", "qc"]
    artifact: ObjectRef

class Provenance(TypedDict):
    parents: list[ObjectRef]
    activities: list[ProvenanceStep]

class MeasurementTime(TypedDict):
    value: float
    unit: Literal["s"]

class Uncertainty(TypedDict):
    type: Literal["SD", "category"]
    value: float | str | None
    budget_ref: str

class QCCheck(TypedDict):
    name: str
    value: str | float | bool | None
    unit: str
    threshold: str
    status: QCStatus
    owner: Literal["QE", "PM", "DS", "DT", "shared"]

class TwinAction(TypedDict):
    recommended: Action
    reason: str

class EvidencePacket(TypedDict):
    packet_version: Literal["1.0"]
    packet_id: str
    subject_id: str
    cell_id: str
    session_id: str
    cycle_n: int
    relative_time: MeasurementTime
    modality: Literal["MRS"]
    nucleus: Literal["23Na"]
    measurement_stage: Stage
    observable: Literal["rmdi", "eoc_metal_area"]
    value: float | None
    unit: Literal["1", "[arb'U].ppm"]
    valid_range: NotRequired[list[float]]
    detection_class: Detection
    upper_limit: float | None
    upper_limit_method: str | None
    model_sensitivity: NotRequired[float | None]
    uncertainty: Uncertainty
    qc_checks: list[QCCheck]
    qc_status: QCStatus
    qc_reasons: list[str]
    protocol_match: bool | None
    comparable: bool | None
    normalization_method: Literal["external_reference_area", "none"]
    origin: Origin
    value_epistemic: Literal["DERIVED"]
    decision_epistemic: Literal["INFERRED"]
    source_object: str
    source_sha256: str
    spatial_reference: dict[str, str]
    acquisition_context: dict[str, JsonValue]
    cell_conditions: dict[str, JsonValue]
    system_qc_id: str | None
    calibration_id: str | None
    thresholds_ref: str
    processing: dict[str, str]
    provenance: Provenance
    twin_action: TwinAction
    interpretation_limit: str

@dataclass(frozen=True)
class Spectrum:
    cell_id: str
    session_id: str
    cycle_n: int
    stage: Stage
    relative_time_s: float
    origin: Origin
    ppm: FloatArray
    intensity_au: FloatArray
    acquisition: Mapping[str, JsonValue]
    cell_conditions: Mapping[str, JsonValue]
    source: ObjectRef

@dataclass(frozen=True)
class SimulationRun:
    spectrum_sources: tuple[ObjectRef, ...]
    truth_source: ObjectRef
    config_version: str
    config_sha256: str

@dataclass(frozen=True)
class PeakFit:
    fit_status: Literal["converged", "failed"]
    window_ppm: PpmWindow
    parameter_order: tuple[str, ...]
    parameters: FloatArray | None
    covariance: FloatArray | None
    residual_au: FloatArray
    peak_center_ppm: float | None
    peak_center_u_ppm: float | None
    peak_area_au_ppm: float | None
    peak_area_u_au_ppm: float | None
    fitted_snr: float | None
    line_shape_area_shift_au_ppm: float | None
    window_area_shift_au_ppm: float | None
    reason: str | None

@dataclass(frozen=True)
class QCResult:
    status: QCStatus
    checks: tuple[QCCheck, ...]
    reasons: tuple[str, ...]
    protocol_match: bool | None
    comparable: bool | None

@dataclass(frozen=True)
class DetectionResult:
    classification: Detection
    value: float | None
    standard_uncertainty: float | None
    upper_limit: float | None
    upper_limit_method: str | None
    reason: str

@dataclass(frozen=True)
class Forecast:
    target_cycle: int
    estimate: float | None
    lower: float | None
    upper: float | None
    interval_level: float | None
    source_packet_ids: tuple[str, ...]
    reason: str

@dataclass(frozen=True)
class TwinState:
    cell_id: str
    cycle_n: int | None
    rmdi_history: tuple[str, ...]
    rmdi_current: float | None
    rmdi_uncertainty: float | None
    health_trend: HealthTrend
    safety_warning: str
    forecast_next_cycle: Forecast | None
    last_valid_cycle: int | None
    evidence_ids: tuple[str, ...]
    state_version: int

@dataclass(frozen=True)
class UpdateEvent:
    packet_id: str
    packet_sha256: str
    action: Action
    reason: str
    previous_state_version: int
    resulting_state_version: int
    comparison: HealthTrend
    forecast_before: Forecast | None
    next_evidence: str
    config_version: str
    change: dict[str, float] | None = None
    forecast_comparison: dict[str, float | bool] | None = None
    origin: Origin | None = None
    evidence: dict[str, JsonValue] | None = None
    forecast_issued: Forecast | None = None
