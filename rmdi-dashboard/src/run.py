"""Reproduce and audit the complete standalone synthetic demonstration."""

import argparse
import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from .common import file_ref, load_config, setting, write_json
from .contracts import Config, ObjectRef, ProvenanceStep
from .detect import classify, run_detection_calibration
from .fit import fit_peak
from .packet import build_packet, model_sensitivity, validate_packet, verify_provenance
from .qc import assess_qc
from .sim import load_spectrum, simulate
from .twin import update_twin

UNSUPPORTED_CLAIMS = {
    "cell-safety verdict": re.compile(
        r"\b(?:cell|battery|charging)\s+(?:is\s+)?(?:safe|certified safe)\b|\bsafety\s+certified\b", re.I
    ),
    "quantified reliability or physical degradation": re.compile(
        r"\b(?:failure probability|short[- ]circuit probability|capacity (?:loss|fade)|"
        r"(?:deposit|dendrite) thickness|deposited (?:sodium )?mass|remaining useful life)"
        r"\s*(?:is|=|of|:)\s*\d", re.I
    ),
}
TEXT_SUFFIXES = {".json", ".jsonl", ".txt", ".csv", ".tsv", ".md", ".yaml", ".html", ".log"}


def scan_claims(root: Path) -> dict:
    """Scan every generated text artifact for specific unsupported claim forms."""
    paths = sorted(path for path in root.rglob("*") if path.is_file() and path.suffix in TEXT_SUFFIXES)
    matches = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for claim, pattern in UNSUPPORTED_CLAIMS.items():
            for match in pattern.finditer(text):
                matches.append({"path": str(path), "claim": claim, "match": match.group()})
    return {"files_scanned": len(paths), "matches": matches}


def _json_fits(fit) -> dict:
    result = asdict(fit)
    for name in ("parameters", "covariance", "residual_au"):
        value = result[name]
        if isinstance(value, np.ndarray):
            result[name] = [row.tolist() for row in value] if value.ndim == 2 else value.tolist()
    return result


def run_demo(config: Config, *, output_dir: Path) -> dict:
    """Generate sources and replay them without reading the separate truth file."""
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError(f"Choose an empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    config_ref = write_json(output_dir / "run-config.json", config)
    simulation = simulate(config, output_dir=output_dir)
    state_path = output_dir / "twin.json"
    packet_refs = []
    updates = []
    stage_baseline = {}
    for source in simulation.spectrum_sources:
        spectrum = load_spectrum(Path(source["path"]))
        if spectrum.source != source:
            raise ValueError(f"Spectrum changed before fitting: {source['path']}")
        metal = fit_peak(spectrum, config, window_ppm=tuple(setting(config, "fit", "metal_window_ppm")))
        reference = None
        if spectrum.stage == "post_discharge":
            reference = fit_peak(spectrum, config, window_ppm=tuple(setting(config, "fit", "reference_window_ppm")))
        qc = assess_qc(
            spectrum, metal, reference, config, comparison_acquisition=stage_baseline.get(spectrum.stage)
        )
        if qc.status == "PASS" and spectrum.stage not in stage_baseline:
            stage_baseline[spectrum.stage] = {**spectrum.acquisition, **spectrum.cell_conditions}
        detection = classify(spectrum, metal, reference, qc, config)
        area = {
            "metal_area": metal.peak_area_au_ppm,
            "metal_area_sd": metal.peak_area_u_au_ppm,
            "reference_area": reference.peak_area_au_ppm if reference else None,
            "reference_area_sd": reference.peak_area_u_au_ppm if reference else None,
            "area_unit": "[arb'U].ppm",
            "model_sensitivity_in_observable_unit": model_sensitivity(metal, reference),
        }
        payloads = (
            ("preprocessing", {
                "method": "Use the stored spectral axis and an independent native fit grid",
                "acquired_complex_points": spectrum.acquisition.get("acquired_complex_points"),
                "fourier_points": int(spectrum.ppm.size),
                "noise_kind": spectrum.acquisition.get("noise_kind"),
                "axis_unit": "ppm",
            }),
            ("fit", {"metal": _json_fits(metal), "reference": _json_fits(reference) if reference else None}),
            ("area", area),
            ("qc", {"qc": asdict(qc), "detection": asdict(detection)}),
        )
        steps: list[ProvenanceStep] = []
        parent: ObjectRef = source
        for step, payload in payloads:
            path = output_dir / "trace" / spectrum.session_id / f"{step}.json"
            artifact = write_json(path, {
                "step": step,
                "input": parent,
                "config": config_ref,
                "config_version": simulation.config_version,
                "config_sha256": simulation.config_sha256,
                "origin": spectrum.origin,
                "result": payload,
            })
            steps.append({"step": step, "artifact": artifact})
            parent = artifact
        packet = build_packet(spectrum, metal, reference, qc, detection, config, provenance_steps=steps)
        packet_ref = write_json(output_dir / "packets" / f"{packet['packet_id']}.json", packet)
        verify_provenance(packet)
        _, event = update_twin(packet, config, state_path=state_path)
        if event.packet_sha256 != packet_ref["sha256"]:
            raise ValueError(f"Twin event did not reference the ingested bytes of {packet['packet_id']}")
        packet_refs.append(packet_ref)
        updates.append({
            "packet": packet_ref,
            "packet_id": event.packet_id,
            "action": event.action,
            "comparison": event.comparison,
            "origin": spectrum.origin,
            "next_evidence": event.next_evidence,
        })
    manifest = {
        "origin": "SIMULATED",
        "config": config_ref,
        "config_version": simulation.config_version,
        "packets": packet_refs,
        "truth": simulation.truth_source,
        "state": file_ref(state_path),
        "updates": updates,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def verify_run(output_dir: Path) -> dict:
    """Check saved digests, source-to-packet links and packet-to-event links."""
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    for reference in (manifest["config"], manifest["state"], *manifest["packets"]):
        if file_ref(Path(reference["path"])) != reference:
            raise ValueError(f"Manifest digest mismatch at {reference['path']}")
    snapshot = json.loads(Path(manifest["state"]["path"]).read_text(encoding="utf-8"))
    event_digests = {event["packet_id"]: event["packet_sha256"] for event in snapshot["events"]}
    for reference in manifest["packets"]:
        packet = validate_packet(json.loads(Path(reference["path"]).read_text(encoding="utf-8")))
        if packet["processing"]["config_sha256"] != manifest["config"]["sha256"]:
            raise ValueError(f"Config digest mismatch for {packet['packet_id']}")
        verify_provenance(packet)
        if event_digests.get(packet["packet_id"]) != reference["sha256"]:
            raise ValueError(f"Missing twin event for {packet['packet_id']}")
    claims = scan_claims(output_dir)
    if claims["matches"]:
        raise ValueError(f"Unsupported claims detected: {claims['matches']}")
    return {"origin": manifest["origin"], "verified_packets": len(manifest["packets"]), **claims}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    operations = parser.add_subparsers(dest="operation", required=True)
    for operation in ("demo", "verify"):
        operations.add_parser(operation).add_argument("--output", type=Path, required=True)
    operations.add_parser("calibrate-detection").add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.operation == "demo":
        result: dict[str, Any] = run_demo(load_config(args.config), output_dir=args.output)
        result = {"origin": result["origin"], "packets": len(result["packets"]), "state": result["state"]}
    elif args.operation == "verify":
        result = verify_run(args.output)
    else:
        result = run_detection_calibration(load_config(args.config))
        result = {"artifact": write_json(args.output, result)}
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
