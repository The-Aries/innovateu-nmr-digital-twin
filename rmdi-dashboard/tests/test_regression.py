"""Team specification §8.2 and the standalone source-to-state replay."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from src.common import load_config
from src.packet import validate_packet, verify_provenance
from src.run import run_demo, scan_claims, verify_run
from src.twin import update_twin

ROOT = Path(__file__).resolve().parents[1]
ORGANIZER_SCHEMA = (
    ROOT.parent / "materials" / "organizer" / "MRI_Hackathon_DataScience_StarterPack_v0.3"
    / "05_TwinReady_JSON_CSV" / "evidence_packet_v1.0.schema.json"
)


@pytest.fixture(scope="module")
def config():
    return load_config(ROOT / "config.yaml")


@pytest.fixture(scope="module")
def replay(tmp_path_factory, config):
    output = tmp_path_factory.mktemp("cycling")
    manifest = run_demo(config, output_dir=output)
    records = {
        packet["packet_id"]: packet
        for ref in manifest["packets"]
        if (packet := json.loads(Path(ref["path"]).read_text(encoding="utf-8")))
    }
    return output, manifest, records


def observation(replay, cycle, value, uncertainty, **overrides):
    packet = copy.deepcopy(next(
        item for item in replay[2].values()
        if item["measurement_stage"] == "post_discharge" and item["twin_action"]["recommended"] == "update"
    ))
    packet.update(
        packet_id=f"E-t{cycle}-rmdi",
        cycle_n=cycle,
        session_id=f"ses-{cycle}P",
        relative_time={"value": 86400 * cycle, "unit": "s"},
        value=value,
        uncertainty={"type": "SD", "value": uncertainty, "budget_ref": "controlled-test"},
        model_sensitivity=0.001,
    )
    packet.update(overrides)
    return packet


def test_reliable_rmdi_increase(replay, config, tmp_path):
    path = tmp_path / "state.json"
    update_twin(observation(replay, 1, 0.15, 0.01), config, state_path=path)
    state, event = update_twin(observation(replay, 2, 0.27, 0.01), config, state_path=path)
    assert state.rmdi_current == 0.27
    assert state.health_trend == event.comparison == "deteriorating"
    assert event.change["z_score"] > 1.96


def test_change_smaller_than_uncertainty(replay, config, tmp_path):
    path = tmp_path / "state.json"
    update_twin(observation(replay, 1, 0.15, 0.06), config, state_path=path)
    _, event = update_twin(observation(replay, 2, 0.17, 0.06), config, state_path=path)
    assert event.comparison == "undetermined"


def test_censored_measurement_has_no_numeric_rmdi(replay, config, tmp_path):
    packet = replay[2]["E-t1-rmdi"]
    assert packet["detection_class"] == "censored"
    assert packet["value"] is None
    assert packet["upper_limit"] > 0
    assert packet["upper_limit_method"]
    state, event = update_twin(packet, config, state_path=tmp_path / "state.json")
    assert state.rmdi_current is None
    assert event.comparison == "undetermined"
    assert event.evidence["upper_limit"] == packet["upper_limit"]
    with pytest.raises(ValueError):
        validate_packet({**packet, "value": 0})


def test_invalid_measurement_does_not_update_accepted_state(replay, config, tmp_path):
    path = tmp_path / "state.json"
    prior, _ = update_twin(observation(replay, 1, 0.15, 0.01), config, state_path=path)
    packet = replay[2]["E-t8-rmdi"]
    assert packet["qc_status"] == "FAIL"
    state, event = update_twin(packet, config, state_path=path)
    assert state == prior
    assert event.action == "reject"
    assert event.packet_id in {item["packet_id"] for item in json.loads(path.read_text())["events"]}


def test_uncertain_measurement_is_qualified_only(replay, config, tmp_path):
    path = tmp_path / "state.json"
    update_twin(observation(replay, 1, 0.15, 0.01), config, state_path=path)
    packet = replay[2]["E-t6-rmdi"]
    assert packet["detection_class"] == "uncertain"
    assert packet["value"] is None
    state, event = update_twin(packet, config, state_path=path)
    assert state.rmdi_current == 0.15
    assert event.action == "update_with_warning"
    assert event.comparison == "undetermined"


def test_changed_sensitivity_blocks_reliable_update(replay, config, tmp_path):
    path = tmp_path / "state.json"
    update_twin(observation(replay, 1, 0.15, 0.01), config, state_path=path)
    packet = observation(replay, 2, 0.30, 0.01, qc_status="WARN", protocol_match=False, comparable=False)
    packet["qc_checks"][1]["status"] = "WARN"
    packet["qc_reasons"] = ["Averages changed."]
    packet["acquisition_context"]["averages"] *= 2
    packet["twin_action"] = {"recommended": "update_with_warning", "reason": "Averages changed."}
    state, event = update_twin(packet, config, state_path=path)
    assert event.action == "update_with_warning"
    assert event.comparison == "undetermined"
    assert state.rmdi_current == 0.15


def test_processing_version_remains_visible(replay, config, tmp_path):
    path = tmp_path / "state.json"
    _, first = update_twin(observation(replay, 1, 0.15, 0.01), config, state_path=path)
    second = observation(replay, 2, 0.20, 0.01)
    second["processing"]["version"] = "alternative-1"
    state, event = update_twin(second, config, state_path=path)
    assert event.packet_sha256 != first.packet_sha256
    assert event.evidence["processing_version"] == second["processing"]["version"] == "alternative-1"
    assert state.rmdi_current == 0.15


@pytest.mark.parametrize("problem", ["missing source", "wrong units"])
def test_packet_rejects_missing_source_or_wrong_units(replay, problem):
    packet = observation(replay, 1, 0.27, 0.03)
    if problem == "missing source":
        del packet["source_object"]
    else:
        packet["unit"] = "ppm"
    with pytest.raises(ValueError):
        validate_packet(packet)


def test_forecast_unavailable_with_too_few_observations(replay, config, tmp_path):
    state, event = update_twin(observation(replay, 1, 0.15, 0.01), config, state_path=tmp_path / "state.json")
    assert event.forecast_before is None
    assert state.forecast_next_cycle is None or state.forecast_next_cycle.estimate is None


def test_simulated_origin_is_exported(replay):
    output, manifest, records = replay
    assert manifest["origin"] == "SIMULATED"
    assert {packet["origin"] for packet in records.values()} == {"SIMULATED"}
    assert {event["origin"] for event in json.loads((output / "twin.json").read_text())["events"]} == {"SIMULATED"}
    with pytest.raises(ValueError):
        validate_packet({**next(iter(records.values())), "value_epistemic": "MEASURED"})


def test_forbidden_claim_scan_covers_all_generated_text(replay, tmp_path):
    output, _, _ = replay
    scan = scan_claims(output)
    assert scan["files_scanned"] >= 24
    assert scan["matches"] == []
    (tmp_path / "bad.txt").write_text("The cell is safe. Capacity loss: 8%.", encoding="utf-8")
    assert len(scan_claims(tmp_path)["matches"]) == 2


def test_source_to_state_golden_path(replay):
    output, manifest, records = replay
    assert len(records) == 24
    assert verify_run(output)["verified_packets"] == 24
    organizer = Draft202012Validator(json.loads(ORGANIZER_SCHEMA.read_text(encoding="utf-8")))
    for packet in records.values():
        organizer.validate(packet)
    snapshot = json.loads(Path(manifest["state"]["path"]).read_text())
    events = {item["packet_id"]: item for item in snapshot["events"]}
    assert events["E-t2-rmdi"]["action"] == "update"
    assert events["E-t8-rmdi"]["action"] == "reject"
    assert snapshot["state"]["last_valid_cycle"] == 12
    assert snapshot["state"]["rmdi_current"] > records["E-t2-rmdi"]["value"]
    assert any(item["comparison"] == "deteriorating" for item in events.values())
    assert any(item.get("forecast_comparison") is not None for item in events.values())
    assert all(item["next_evidence"] for item in events.values())


def test_changed_artifact_breaks_the_provenance_trace(replay):
    packet = replay[2]["E-t2-rmdi"]
    artifact = Path(packet["provenance"]["activities"][1]["artifact"]["path"])
    original = artifact.read_bytes()
    try:
        artifact.write_bytes(original + b" ")
        with pytest.raises(ValueError, match="digest mismatch"):
            verify_provenance(packet)
    finally:
        artifact.write_bytes(original)
