"""Persist evidence decisions and update a single-cell RMDI state."""

from __future__ import annotations

from dataclasses import asdict, replace
import fcntl
import json
from math import hypot, isfinite, sqrt
from pathlib import Path
from typing import TypedDict

import numpy as np
from scipy.stats import t

from .common import canonical_bytes, setting, sha256_bytes, write_json
from .contracts import Config, EvidencePacket, Forecast, HealthTrend, TwinState, UpdateEvent
from .packet import validate_packet


class Observation(TypedDict):
    packet_id: str
    cycle: int
    relative_time_s: float
    value: float
    standard_uncertainty: float
    model_sensitivity: float


def _restore_state(data: dict) -> TwinState:
    history = tuple(data["rmdi_history"])
    evidence_ids = tuple(data["evidence_ids"])
    forecast_data = data["forecast_next_cycle"]
    forecast = _restore_forecast(forecast_data)
    return TwinState(**{**data, "rmdi_history": history, "evidence_ids": evidence_ids,
                        "forecast_next_cycle": forecast})


def _restore_forecast(data: dict | None) -> Forecast | None:
    if data is None:
        return None
    return Forecast(**{**data, "source_packet_ids": tuple(data["source_packet_ids"])})


def _fit_forecast(observations: list[Observation], target: int, config: Config) -> Forecast:
    points_needed = int(setting(config, "twin", "forecast_min_points"))
    window = int(setting(config, "twin", "forecast_window"))
    level = float(setting(config, "twin", "forecast_interval_level"))
    if not 3 <= points_needed <= window or not 0 < level < 1:
        raise ValueError("Forecast requires 3 <= minimum points <= window and a level in (0, 1)")

    selected = observations[-window:]
    packet_ids = tuple(point["packet_id"] for point in selected)
    if len(selected) < points_needed:
        return Forecast(target, None, None, None, None, packet_ids,
                        f"Forecast unavailable with fewer than {points_needed} reliable observations.")

    # Center at the forecast target so the design intercept is its prediction.
    cycle_offset = np.array([point["cycle"] - target for point in selected], dtype=float)
    design = np.column_stack((np.ones(len(selected)), cycle_offset))
    values = np.array([point["value"] for point in selected])
    sd = np.array([point["standard_uncertainty"] for point in selected])
    weighted_design = design / sd[:, None]
    coefficients, _, _, _ = np.linalg.lstsq(weighted_design, values / sd, rcond=None)
    parameter_covariance = np.linalg.inv(weighted_design.T @ weighted_design)
    degrees_of_freedom = len(selected) - 2
    standardized_residuals = (values - design @ coefficients) / sd
    # Inflate parameter and future-observation variance by the same excess-scatter factor.
    # The floor prevents a near-perfect short fit from erasing known measurement noise.
    scale = max(1.0, float(standardized_residuals @ standardized_residuals) / degrees_of_freedom)
    next_observation_variance = float(np.median(sd**2))
    prediction_sd = sqrt(scale * (parameter_covariance[0, 0] + next_observation_variance))
    half_width = float(t.ppf((1 + level) / 2, degrees_of_freedom)) * prediction_sd
    estimate = float(coefficients[0])
    return Forecast(target, estimate, estimate - half_width, estimate + half_width, level, packet_ids,
                    "Local weighted line with a Student-t interval for one future observation.")


def _assess_change(current: Observation, previous: Observation, z_threshold: float,
                   sensitivity_margin: float | None) -> tuple[HealthTrend, dict[str, float]]:
    delta = current["value"] - previous["value"]
    uncertainty = hypot(current["standard_uncertainty"], previous["standard_uncertainty"])
    model_guard = current["model_sensitivity"] + previous["model_sensitivity"]
    random_guard = z_threshold * uncertainty
    threshold = random_guard + model_guard
    if delta > threshold:
        classification = "deteriorating"
    elif sensitivity_margin is not None and abs(delta) + threshold <= sensitivity_margin:
        classification = "stable"
    else:
        classification = "undetermined"
    return classification, {
        "delta": delta,
        "standard_uncertainty": uncertainty,
        "z_score": delta / uncertainty,
        "z_threshold": z_threshold,
        "random_threshold": random_guard,
        "model_sensitivity_guard": model_guard,
        "significance_threshold": threshold,
    }


def _accelerating(history: list[Observation], z_threshold: float) -> bool:
    if len(history) < 3:
        return False
    first, middle, last = history[-3:]
    first_gap = middle["cycle"] - first["cycle"]
    last_gap = last["cycle"] - middle["cycle"]
    # Both slopes contain the middle measurement. Apply its combined coefficient once.
    coefficients = (1 / first_gap, -1 / first_gap - 1 / last_gap, 1 / last_gap)
    acceleration = sum(weight * point["value"]
                       for weight, point in zip(coefficients, (first, middle, last)))
    random_sd = hypot(*(weight * point["standard_uncertainty"]
                        for weight, point in zip(coefficients, (first, middle, last))))
    model_guard = sum(abs(weight) * point["model_sensitivity"]
                      for weight, point in zip(coefficients, (first, middle, last)))
    return acceleration > z_threshold * random_sd + model_guard


def _comparison_identity(packet: EvidencePacket) -> dict:
    return {
        "pipeline": packet["processing"]["pipeline"],
        "processing_version": packet["processing"]["version"],
        "normalization": packet["normalization_method"],
        "spectral_reference": packet["acquisition_context"].get("spectral_reference"),
        "calibration_id": packet["calibration_id"],
    }


def _next_evidence(comparison: HealthTrend, *, out_of_interval: bool = False,
                   acceleration: bool = False, initial: bool = False) -> str:
    if acceleration:
        return "Refer the accumulation pattern for expert review and request a matched post-discharge repeat."
    if comparison == "deteriorating" or out_of_interval:
        return "Request a matched post-discharge repeat and check reference stability and fit residuals."
    if comparison == "stable" or initial:
        return "Repeat the measurement after the next standardized discharge."
    return "Improve signal-to-noise and repeat the matched post-discharge measurement."


def update_twin(packet: EvidencePacket, config: Config, *,
                state_path: Path) -> tuple[TwinState, UpdateEvent]:
    """Validate and log one packet, then commit state and audit together under a file lock."""
    packet = validate_packet(packet)
    packet_sha = sha256_bytes(canonical_bytes(packet))
    config_version = str(setting(config, "config_version"))
    config_sha = sha256_bytes(canonical_bytes(config))
    state_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = state_path.with_name(f".{state_path.name}.lock")
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if state_path.exists():
            snapshot = json.loads(state_path.read_text(encoding="utf-8"))
            if snapshot.get("snapshot_version") != "1.0":
                raise ValueError("Unsupported RMDI snapshot version")
        else:
            initial = TwinState(packet["cell_id"], None, (), None, None, "undetermined",
                                "Assessment unavailable or uncertain.", None, None, (), 0)
            snapshot = {
                "snapshot_version": "1.0", "config_version": config_version,
                "config_sha256": config_sha, "origin": packet["origin"], "state": asdict(initial),
                "events": [], "reliable_observations": [], "comparison_identity": None,
                "processed_post_cycle": None, "processed_post_time_s": None,
            }

        state = _restore_state(snapshot["state"])
        matching_events = [
            event for event in snapshot["events"]
            if event["packet_id"] == packet["packet_id"] and event["origin"] == packet["origin"]
            and event["evidence"]["cell_id"] == packet["cell_id"]
        ]
        for event in matching_events:
            if event["packet_sha256"] == packet_sha:
                return state, UpdateEvent(**{
                    **event,
                    "forecast_before": _restore_forecast(event["forecast_before"]),
                    "forecast_issued": _restore_forecast(event["forecast_issued"]),
                })

        state, event = _apply_packet(state, snapshot, packet, config, packet_sha, config_sha,
                                     config_version, conflict=bool(matching_events))
        snapshot["state"] = asdict(state)
        snapshot["events"].append(asdict(event))
        write_json(state_path, snapshot)
        return state, event


def _apply_packet(state: TwinState, snapshot: dict, packet: EvidencePacket, config: Config,
                  packet_sha: str, config_sha: str, config_version: str, *,
                  conflict: bool) -> tuple[TwinState, UpdateEvent]:
    label: HealthTrend = "undetermined"
    reason = ""
    recommendation = "Check measurement identity and acquisition records before replay."
    action = "reject"
    forecast_before = state.forecast_next_cycle
    cycle = packet["cycle_n"]
    seconds = packet["relative_time"]["value"]
    if forecast_before is not None and forecast_before.target_cycle != cycle:
        forecast_before = None
    history: list[Observation] = snapshot["reliable_observations"]
    identity = _comparison_identity(packet)
    processing = packet["processing"]
    model_sensitivity = packet.get("model_sensitivity")
    prior_version = state.state_version
    change = None
    comparison = None

    if conflict:
        reason = "Conflicting payload for an existing packet identity."
        forecast_before = None
    elif packet["cell_id"] != state.cell_id or packet["origin"] != snapshot["origin"]:
        reason = "Packet cell or evidence origin differs from the snapshot."
        forecast_before = None
    elif (
        config_sha != snapshot["config_sha256"] or processing["config_version"] != config_version
        or processing.get("config_sha256", config_sha) != config_sha
    ):
        reason = "Packet or runtime configuration differs from the snapshot policy."
        forecast_before = None
    elif packet["measurement_stage"] == "end_of_charge":
        reason = "End-of-charge observation recorded as context for the post-discharge measurement."
        recommendation = "Measure after the standardized discharge."
        forecast_before = None
    elif snapshot["processed_post_cycle"] is not None and (
        cycle <= snapshot["processed_post_cycle"] or seconds <= snapshot["processed_post_time_s"]
    ):
        reason = "Post-discharge cycle or time is out of order."
        forecast_before = None
    else:
        snapshot["processed_post_cycle"] = cycle
        snapshot["processed_post_time_s"] = seconds
        requested_action = packet["twin_action"]["recommended"]
        identity_changed = snapshot["comparison_identity"] not in (None, identity)
        if packet["qc_status"] == "FAIL" or requested_action == "reject":
            reason = packet["twin_action"]["reason"]
            recommendation = "Resolve the recorded QC issue and repeat the matched post-discharge acquisition."
        elif packet["detection_class"] in ("censored", "uncertain"):
            action = "update_with_warning"
            reason = packet["twin_action"]["reason"]
            recommendation = _next_evidence(label)
            state = replace(state, cycle_n=cycle, health_trend=label,
                            safety_warning="Assessment unavailable or uncertain.", forecast_next_cycle=None,
                            evidence_ids=(*state.evidence_ids, packet["packet_id"]), state_version=prior_version + 1)
        elif identity_changed or packet["comparable"] is not True or packet["protocol_match"] is not True:
            action = "update_with_warning"
            reason = "Comparison withheld because the protocol, processing or reference identity differs."
            recommendation = "Verify acquisition sensitivity, processing version and reference before comparison."
        elif packet["qc_status"] == "WARN" or requested_action != "update":
            action = "update_with_warning"
            reason = packet["twin_action"]["reason"]
            recommendation = "Review the QC warning and repeat the matched post-discharge acquisition."
        elif model_sensitivity is None:
            action = "update_with_warning"
            reason = "Quantitative evidence lacks a model-sensitivity bound for reliable comparison."
            recommendation = "Evaluate peak-model and fitting-window sensitivity before comparing the RMDI."
        else:
            observation: Observation = {
                "packet_id": packet["packet_id"], "cycle": cycle, "relative_time_s": seconds,
                "value": float(packet["value"]), "standard_uncertainty": float(packet["uncertainty"]["value"]),
                "model_sensitivity": float(model_sensitivity),
            }
            z_threshold = float(setting(config, "twin", "increase_z"))
            margin_setting = setting(config, "twin", "adequate_sensitivity_margin")
            margin = float(margin_setting) if margin_setting is not None else None
            if not isfinite(z_threshold) or z_threshold <= 0 or (
                margin is not None and (not isfinite(margin) or margin <= 0)
            ):
                raise ValueError("Twin comparison thresholds must be finite and positive")
            reason = "Initialized the reliable post-discharge RMDI baseline."
            warning = "Assessment unavailable or uncertain."
            if history:
                label, change = _assess_change(observation, history[-1], z_threshold, margin)
                reason, warning = {
                    "deteriorating": ("Increase exceeds the uncertainty and model-sensitivity guard.",
                                      "Accumulation warning."),
                    "stable": ("The change and its uncertainty fit within the declared resolution margin.",
                               "No evidence of increasing residual deposition within measurement resolution."),
                    "undetermined": ("The observation does not resolve either an increase or stability.",
                                     "Assessment unavailable or uncertain."),
                }[label]
            if forecast_before is not None and forecast_before.estimate is not None:
                actual = observation["value"]
                comparison = {
                    "actual": actual, "residual": actual - forecast_before.estimate,
                    "within_interval": forecast_before.lower <= actual <= forecast_before.upper,
                }
            history.append(observation)
            acceleration = label == "deteriorating" and _accelerating(history, z_threshold)
            if acceleration:
                warning = "Elevated concern. Further investigation recommended."
            recommendation = _next_evidence(label, acceleration=acceleration, initial=len(history) == 1,
                                            out_of_interval=bool(comparison and not comparison["within_interval"]))
            snapshot["comparison_identity"] = identity
            action = "update"
            state = replace(state, cycle_n=cycle, rmdi_history=(*state.rmdi_history, packet["packet_id"]),
                            rmdi_current=observation["value"], rmdi_uncertainty=observation["standard_uncertainty"],
                            health_trend=label, safety_warning=warning,
                            forecast_next_cycle=_fit_forecast(history, cycle + 1, config), last_valid_cycle=cycle,
                            evidence_ids=(*state.evidence_ids, packet["packet_id"]), state_version=prior_version + 1)

    return state, UpdateEvent(
        packet_id=packet["packet_id"], packet_sha256=packet_sha, action=action, reason=reason,
        previous_state_version=prior_version, resulting_state_version=state.state_version,
        comparison=label, forecast_before=forecast_before, next_evidence=recommendation,
        config_version=config_version, change=change, forecast_comparison=comparison, origin=packet["origin"],
        forecast_issued=state.forecast_next_cycle if action == "update" else None,
        evidence={
            "cell_id": packet["cell_id"], "cycle_n": cycle, "measurement_stage": packet["measurement_stage"],
            "source_object": packet["source_object"], "source_sha256": packet["source_sha256"],
            "processing_version": processing["version"], "config_sha256": processing.get("config_sha256"),
            "qc_status": packet["qc_status"],
            "detection_class": packet["detection_class"], "value": packet["value"], "unit": packet["unit"],
            "uncertainty": packet["uncertainty"]["value"], "upper_limit": packet["upper_limit"],
            "upper_limit_method": packet["upper_limit_method"],
            "model_sensitivity": model_sensitivity,
        },
    )
