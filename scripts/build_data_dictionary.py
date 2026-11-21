"""Build the RMDI evidence-packet data dictionary from schema v1.0.

Usage: python3 scripts/build_data_dictionary.py
Writes evidence/data-dictionary.json. Field constraints come from the schema;
groups follow the team specification §6.1; examples come from one stored packet.
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "rmdi-dashboard/schema/evidence_packet_v1.0.schema.json"
EXAMPLE = ROOT / "evidence/rmdi-replay/packets/E-t5-rmdi.json"
OUTPUT = ROOT / "evidence/data-dictionary.json"

GROUPS = {
    "Identification": ["packet_version", "packet_id", "subject_id", "cell_id", "session_id", "cycle_n", "relative_time"],
    "Measurement": ["modality", "nucleus", "measurement_stage", "observable", "value", "unit", "valid_range",
                    "detection_class", "upper_limit", "upper_limit_method", "model_sensitivity"],
    "Acquisition": ["acquisition_context"],
    "Cell conditions": ["cell_conditions"],
    "Sample support": ["spatial_reference"],
    "Trust": ["uncertainty", "qc_checks", "qc_status", "qc_reasons", "system_qc_id", "calibration_id", "thresholds_ref"],
    "Comparability": ["protocol_match", "comparable", "normalization_method"],
    "Provenance": ["source_object", "source_sha256", "processing", "provenance"],
    "Interpretation": ["origin", "value_epistemic", "decision_epistemic", "interpretation_limit"],
    "Twin response": ["twin_action"],
}
CONSTRAINT_KEYS = ["type", "const", "enum", "pattern", "minimum", "exclusiveMinimum", "minItems", "maxItems", "minLength"]


def resolve(node, defs):
    while isinstance(node, dict) and "$ref" in node:
        node = defs[node["$ref"].split("/")[-1]]
    return node


def describe(name, node, defs, required, example):
    node = resolve(node, defs)
    entry = {"field": name, "required": name in required}
    entry.update({k: node[k] for k in CONSTRAINT_KEYS if k in node})
    if "description" in node:
        entry["description"] = node["description"]
    if node.get("type") == "object" and "properties" in node:
        child_required = set(node.get("required", []))
        child_example = example if isinstance(example, dict) else {}
        entry["fields"] = [describe(k, v, defs, child_required, child_example.get(k))
                           for k, v in node["properties"].items()]
    elif example is not None and not isinstance(example, (dict, list)):
        entry["example"] = example
    return entry


def main():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    defs, props, required = schema.get("$defs", {}), schema["properties"], set(schema["required"])
    grouped = {name for names in GROUPS.values() for name in names}
    missing = sorted(set(props) - grouped)
    if missing:
        raise SystemExit(f"Fields without a group: {missing}")
    dictionary = {
        "dictionary_version": "1.0",
        "title": "Evidence-packet data dictionary, standalone 23Na RMDI demonstrator",
        "schema": str(SCHEMA.relative_to(ROOT)),
        "schema_id": schema.get("$id"),
        "example_packet": str(EXAMPLE.relative_to(ROOT)),
        "origin_of_example": example.get("origin"),
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "generator": "scripts/build_data_dictionary.py",
        "scope_note": "Lists top-level and nested object fields with their schema constraints. "
                      "Array item structures and the conditional rules in the schema's allOf are defined in the schema itself.",
        "groups": [
            {"group": group, "fields": [describe(n, props[n], defs, required, example.get(n)) for n in names if n in props]}
            for group, names in GROUPS.items()
        ],
    }
    OUTPUT.write_text(json.dumps(dictionary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
