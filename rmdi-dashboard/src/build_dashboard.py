"""Package a verified cycling replay as one offline HTML document."""

import argparse
import json
from pathlib import Path

from .fit import independent_points
from .run import verify_run
from .sim import load_spectrum

ASSETS = Path(__file__).resolve().parents[1] / "dashboard"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _spectral_view(spectrum, fit: dict) -> dict:
    low, high = fit["window_ppm"]
    mask = (spectrum.ppm >= low) & (spectrum.ppm <= high)
    native_ppm, _ = independent_points(spectrum, (low, high))
    return {
        "ppm": spectrum.ppm[mask].round(5).tolist(),
        "intensity": spectrum.intensity_au[mask].round(6).tolist(),
        "native_ppm": native_ppm.round(5).tolist(),
        "residual": fit["residual_au"],
        "window": fit["window_ppm"],
        "parameters": fit["parameters"],
        "center": fit["peak_center_ppm"],
        "center_sd": fit["peak_center_u_ppm"],
        "area": fit["peak_area_au_ppm"],
        "area_sd": fit["peak_area_u_au_ppm"],
        "snr": fit["fitted_snr"],
        "shape_shift": fit["line_shape_area_shift_au_ppm"],
        "window_shift": fit["window_area_shift_au_ppm"],
    }


def build_dashboard(run_dir: Path, output: Path) -> None:
    verify_run(run_dir)
    manifest = _read(run_dir / "manifest.json")
    if manifest["origin"] != "SIMULATED":
        raise ValueError("This dashboard presents the standalone simulated cell replay")
    snapshot = _read(Path(manifest["state"]["path"]))
    events = {event["packet_id"]: event for event in snapshot["events"]}
    cycles: dict[int, dict] = {}
    for reference in manifest["packets"]:
        packet_text = Path(reference["path"]).read_text(encoding="utf-8")
        packet = json.loads(packet_text)
        spectrum = load_spectrum(Path(packet["source_object"]))
        fit_activity = next(item for item in packet["provenance"]["activities"] if item["step"] == "fit")
        fit = _read(Path(fit_activity["artifact"]["path"]))["result"]
        stage = packet["measurement_stage"]
        cycle = cycles.setdefault(packet["cycle_n"], {"cycle": packet["cycle_n"]})
        cycle[stage] = {
            "packetText": packet_text,
            "event": events[packet["packet_id"]],
            "metal": _spectral_view(spectrum, fit["metal"]),
            "reference": _spectral_view(spectrum, fit["reference"]) if fit["reference"] else None,
        }

    payload = {
        "origin": manifest["origin"],
        "configVersion": manifest["config_version"],
        "cellId": snapshot["state"]["cell_id"],
        "cycles": [cycles[number] for number in sorted(cycles)],
    }
    document = (ASSETS / "index.html").read_text(encoding="utf-8")
    for token, replacement in (
        ("<!-- dashboard-css -->", (ASSETS / "app.css").read_text(encoding="utf-8")),
        ("<!-- dashboard-js -->", (ASSETS / "app.js").read_text(encoding="utf-8")),
        ("<!-- dashboard-data -->", json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")),
    ):
        if document.count(token) != 1:
            raise ValueError(f"Missing or duplicated template marker {token}")
        document = document.replace(token, replacement, 1)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    build_dashboard(args.run, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
