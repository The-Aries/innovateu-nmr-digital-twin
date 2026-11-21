"""Verify persistent state decisions with controlled evidence observations."""

from concurrent.futures import ThreadPoolExecutor
import json
from math import sqrt
from pathlib import Path

import pytest
from scipy.stats import t

from src import twin
from src.common import canonical_bytes, load_config, sha256_bytes


@pytest.fixture
def config():
    return load_config(Path(__file__).resolve().parents[1] / "config.yaml")


@pytest.fixture(autouse=True)
def isolate_state_logic(monkeypatch):
    # The M4 packet and golden-path tests cover schema and semantic validation.
    monkeypatch.setattr(twin, "validate_packet", lambda packet: packet)


def evidence(cycle, value, *, uncertainty=0.01, model_sensitivity=0.0, status="PASS",
             detection="detected", upper_limit=None, cell="cell-1", version="1.0.0", config):
    action = "update" if status == "PASS" and detection == "detected" else "update_with_warning"
    if status == "FAIL":
        action = "reject"
    return {
        "packet_id": f"E-t{cycle}-rmdi", "cell_id": cell, "cycle_n": cycle, "origin": "SIMULATED",
        "relative_time": {"value": cycle * 60, "unit": "s"}, "measurement_stage": "post_discharge",
        "value": value, "unit": "1", "upper_limit": upper_limit,
        "upper_limit_method": "test-fixture bound" if upper_limit is not None else None,
        "uncertainty": {"type": "SD" if uncertainty is not None else "category", "value": uncertainty},
        "model_sensitivity": model_sensitivity, "comparable": True, "protocol_match": True,
        "qc_status": status, "detection_class": detection, "normalization_method": "external_reference_area",
        "processing": {"pipeline": "spectral-fit", "version": version,
                       "config_version": config["config_version"]["value"]},
        "calibration_id": "simulated-reference", "acquisition_context": {"spectral_reference": "NaCl"},
        "source_object": f"data/cycle-{cycle}.json", "source_sha256": "0" * 64,
        "twin_action": {"recommended": action, "reason": f"{status} {detection} evidence."},
    }


def test_forecast_is_saved_prior_to_target_and_compared_on_replay(tmp_path, config):
    snapshot = tmp_path / "state.json"
    for cycle in range(1, 4):
        state, event = twin.update_twin(evidence(cycle, cycle * 0.05, config=config), config, state_path=snapshot)
        if cycle < 3:
            assert state.forecast_next_cycle.estimate is None
    prior = state.forecast_next_cycle
    assert prior.target_cycle == 4
    assert prior.estimate == pytest.approx(0.2)
    # x=4, x_bar=2, Sxx=2, n=3, common future-observation SD=0.01.
    half_width = t.ppf(0.975, 1) * 0.01 * sqrt(1 + 1 / 3 + 4 / 2)
    assert prior.upper == pytest.approx(0.2 + half_width)
    assert prior.lower == pytest.approx(0.2 - half_width)
    packet = evidence(4, 0.21, config=config)
    state, event = twin.update_twin(packet, config, state_path=snapshot)
    assert event.forecast_before == prior
    assert event.forecast_comparison["residual"] == pytest.approx(0.01)
    assert event.forecast_comparison["within_interval"] is True
    assert event.packet_sha256 == sha256_bytes(canonical_bytes(packet))
    assert event.origin == "SIMULATED"
    restored, repeated = twin.update_twin(packet, config, state_path=snapshot)
    assert (restored, repeated) == (state, event)
    assert len(json.loads(snapshot.read_text())["events"]) == 4


def test_forecast_is_archived_even_if_target_is_skipped(tmp_path, config):
    snapshot = tmp_path / "state.json"
    for cycle in (1, 2, 3, 5):
        state, event = twin.update_twin(evidence(cycle, cycle * 0.05, config=config), config, state_path=snapshot)
    assert event.forecast_before is None
    assert event.forecast_comparison is None
    assert state.forecast_next_cycle.target_cycle == 6
    archived = json.loads(snapshot.read_text())["events"][2]["forecast_issued"]
    assert archived["target_cycle"] == 4
    assert archived["estimate"] == pytest.approx(0.20)


def test_forecast_disagreement_recommends_confirmation(tmp_path, config):
    snapshot = tmp_path / "state.json"
    for cycle in (1, 2, 3):
        twin.update_twin(evidence(cycle, 0.45, config=config), config, state_path=snapshot)
    state, event = twin.update_twin(evidence(4, 0.10, config=config), config, state_path=snapshot)
    assert state.health_trend == "undetermined"
    assert event.forecast_comparison["residual"] == pytest.approx(-0.35)
    assert event.forecast_comparison["within_interval"] is False
    assert "repeat and check reference stability" in event.next_evidence


def test_warning_failure_and_censoring_respect_reliable_state(tmp_path, config):
    snapshot = tmp_path / "state.json"
    original, _ = twin.update_twin(evidence(1, 0.07, config=config), config, state_path=snapshot)
    warning, event = twin.update_twin(evidence(2, 0.40, status="WARN", config=config), config, state_path=snapshot)
    assert warning == original
    assert event.action == "update_with_warning"
    assert event.comparison == "undetermined"
    failed, event = twin.update_twin(
        evidence(3, None, uncertainty=None, status="FAIL", detection="invalid", config=config),
        config, state_path=snapshot,
    )
    assert failed == original
    assert event.action == "reject"
    assert event.evidence["qc_status"] == "FAIL"
    censored, event = twin.update_twin(
        evidence(4, None, uncertainty=None, detection="censored", upper_limit=0.04, config=config),
        config, state_path=snapshot,
    )
    assert event.evidence["value"] is None
    assert event.evidence["upper_limit"] == 0.04
    assert censored.rmdi_current == original.rmdi_current
    assert censored.rmdi_history == original.rmdi_history
    assert censored.health_trend == "undetermined"
    later, event = twin.update_twin(evidence(5, 0.20, config=config), config, state_path=snapshot)
    assert later.last_valid_cycle == 5
    assert later.rmdi_history == ("E-t1-rmdi", "E-t5-rmdi")
    assert event.change["delta"] == pytest.approx(0.13)
    assert event.comparison == "deteriorating"


def test_model_sensitivity_can_veto_an_increase(tmp_path, config):
    snapshot = tmp_path / "state.json"
    twin.update_twin(evidence(1, 0.15, model_sensitivity=0.03, config=config), config, state_path=snapshot)
    state, event = twin.update_twin(evidence(2, 0.22, model_sensitivity=0.03, config=config),
                                    config, state_path=snapshot)
    assert event.change["z_score"] > event.change["z_threshold"]
    assert event.change["model_sensitivity_guard"] == pytest.approx(0.06)
    assert event.change["significance_threshold"] > event.change["delta"]
    assert state.health_trend == "undetermined"


@pytest.mark.parametrize("omit_field", [False, True])
def test_quantitative_packet_without_model_sensitivity_stays_qualified(tmp_path, config, omit_field):
    snapshot = tmp_path / "state.json"
    baseline, _ = twin.update_twin(evidence(1, 0.15, config=config), config, state_path=snapshot)
    packet = evidence(2, 0.40, model_sensitivity=None, config=config)
    if omit_field:
        del packet["model_sensitivity"]
    state, event = twin.update_twin(packet, config, state_path=snapshot)
    assert state == baseline
    assert event.action == "update_with_warning"
    assert event.comparison == "undetermined"
    assert event.change is None


def test_packet_config_digest_must_match_when_supplied(tmp_path, config):
    snapshot = tmp_path / "state.json"
    baseline, _ = twin.update_twin(evidence(1, 0.15, config=config), config, state_path=snapshot)
    packet = evidence(2, 0.40, config=config)
    packet["processing"]["config_sha256"] = "0" * 64
    state, event = twin.update_twin(packet, config, state_path=snapshot)
    assert state == baseline
    assert event.action == "reject"
    assert "configuration differs" in event.reason
    current = evidence(3, 0.45, config=config)
    current["processing"]["config_sha256"] = sha256_bytes(canonical_bytes(config))
    state, event = twin.update_twin(current, config, state_path=snapshot)
    assert state.rmdi_current == 0.45
    assert event.action == "update"


def test_stability_requires_adequate_sensitivity(tmp_path, config):
    for noise, expected in ((0.005, "stable"), (0.05, "undetermined")):
        snapshot = tmp_path / f"state-{noise}.json"
        twin.update_twin(evidence(1, 0.150, uncertainty=noise, config=config), config, state_path=snapshot)
        state, _ = twin.update_twin(evidence(2, 0.151, uncertainty=noise, config=config),
                                    config, state_path=snapshot)
        assert state.health_trend == expected


def test_identity_and_order_guards_preserve_state(tmp_path, config):
    snapshot = tmp_path / "state.json"
    original, _ = twin.update_twin(evidence(1, 0.12, config=config), config, state_path=snapshot)
    foreign = evidence(2, 0.50, cell="other-cell", config=config)
    state, event = twin.update_twin(foreign, config, state_path=snapshot)
    assert state == original
    assert event.action == "reject"
    progressed, event = twin.update_twin(evidence(2, 0.19, config=config), config, state_path=snapshot)
    assert event.action == "update"
    assert progressed.rmdi_current == 0.19
    conflict = evidence(2, 0.20, config=config)
    state, event = twin.update_twin(conflict, config, state_path=snapshot)
    assert state == progressed
    assert "Conflicting payload" in event.reason
    changed_version = evidence(4, 0.30, version="2.0.0", config=config)
    state, event = twin.update_twin(changed_version, config, state_path=snapshot)
    assert state == progressed
    assert event.action == "update_with_warning"
    assert event.evidence["processing_version"] == "2.0.0"
    state, event = twin.update_twin(evidence(3, 0.25, config=config), config, state_path=snapshot)
    assert state == progressed
    assert event.action == "reject"
    assert "out of order" in event.reason


def test_accelerating_increase_recommends_review(tmp_path, config):
    snapshot = tmp_path / "state.json"
    for cycle, value in enumerate((0.10, 0.11, 0.35), start=1):
        state, event = twin.update_twin(evidence(cycle, value, config=config), config, state_path=snapshot)
    assert state.health_trend == "deteriorating"
    assert "Elevated concern" in state.safety_warning
    assert "expert review" in event.next_evidence


def test_duplicate_callbacks_commit_once(tmp_path, config):
    snapshot = tmp_path / "state.json"
    packet = evidence(1, 0.15, config=config)

    def ingest(_):
        return twin.update_twin(packet, config, state_path=snapshot)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(ingest, (0, 1)))
    assert results[0] == results[1]
    assert results[0][0].state_version == 1
    assert len(json.loads(snapshot.read_text())["events"]) == 1
