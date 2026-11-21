#!/usr/bin/env python3
"""validate_pack.py — structural, hash and packet checks of StarterPack v0.3 (Python standard library only).
usage: python 00_START_HERE/validate_pack.py"""
import csv, gzip, hashlib, json, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RANK = {"PASS": 0, "WARN": 1, "FAIL": 2}
ALLOWED = {"PASS": {"update"}, "WARN": {"update_with_warning", "reject"}, "FAIL": {"reject"}}
errors = []

def read_bytes(p):
    return gzip.open(p, "rb").read() if str(p).endswith(".gz") else p.read_bytes()

def check_nifti(p, mrs=False):
    b = read_bytes(p)
    if struct.unpack_from("<i", b, 0)[0] != 348: errors.append(f"{p}: bad sizeof_hdr")
    if b[344:348] not in (b"n+1\x00", b"ni1\x00"): errors.append(f"{p}: bad magic")
    if mrs:
        dim = struct.unpack_from("<8h", b, 40)
        if not (dim[0] >= 4 and dim[1:4] == (1, 1, 1)): errors.append(f"{p}: not an SVS NIfTI-MRS shape")
        if struct.unpack_from("<h", b, 70)[0] not in (32, 1792, 2048): errors.append(f"{p}: not complex")
        esize, ecode = struct.unpack_from("<ii", b, 352)
        if ecode != 44: errors.append(f"{p}: expected header extension code 44")
        meta = json.loads(b[360:352 + esize].rstrip(b"\x00").decode("utf-8"))
        for k in ("SpectrometerFrequency", "ResonantNucleus"):
            if k not in meta: errors.append(f"{p}: missing {k}")

def check_dicom(p):
    b = p.read_bytes()
    if b[128:132] != b"DICM": errors.append(f"{p}: missing DICM marker")

for p in (ROOT / "01_DICOM").glob("*/*.dcm"): check_dicom(p)
for p in (ROOT / "02_NIfTI").glob("*.nii.gz"): check_nifti(p)
for p in (ROOT / "03_BIDS_MRI").rglob("*.nii.gz"): check_nifti(p)
for p in (ROOT / "04_MRS_BIDS").glob("sub-*/ses-*/mrs/*_svs.nii.gz"): check_nifti(p, True)
for p in ROOT.rglob("*.json"): json.load(open(p, encoding="utf-8"))
# manifest
n = 0
for row in csv.DictReader(open(ROOT / "manifest_sha256.csv", encoding="utf-8")):
    fp = ROOT / row["path"]; n += 1
    if not fp.exists(): errors.append(f"manifest: missing {row['path']}"); continue
    if hashlib.sha256(fp.read_bytes()).hexdigest() != row["sha256"]: errors.append(f"manifest: hash mismatch {row['path']}")
# packets: semantic rules of schema v1.0 (dossier section 8.2)
for p in sorted((ROOT / "05_TwinReady_JSON_CSV" / "packets").glob("*.json")):
    k = json.load(open(p, encoding="utf-8"))
    checks = k.get("qc_checks") or []
    if checks:
        w = max(checks, key=lambda c: RANK.get(c.get("status"), 3)).get("status")
        if k.get("qc_status") != w: errors.append(f"{p.name}: qc_status {k.get('qc_status')} but worst check {w}")
    v, r = k.get("value"), k.get("valid_range")
    if isinstance(v, (int, float)) and r and not (r[0] <= v <= r[1]): errors.append(f"{p.name}: value outside valid_range")
    a = (k.get("twin_action") or {}).get("recommended")
    if k.get("qc_status") in ALLOWED and a not in ALLOWED[k["qc_status"]]: errors.append(f"{p.name}: action {a} not allowed")
    if k.get("origin") == "SIMULATED" and k.get("value_epistemic") == "MEASURED": errors.append(f"{p.name}: SIMULATED labelled MEASURED")
    src = k.get("source_sha256")
    if src and (ROOT / k["source_object"]).exists():
        if hashlib.sha256((ROOT / k["source_object"]).read_bytes()).hexdigest() != src: errors.append(f"{p.name}: source hash mismatch")
if errors:
    print("Starter-pack checks FAILED:"); [print("  -", e) for e in errors]; sys.exit(1)
print(f"Starter-pack v0.3 checks passed ({n} manifest entries).")
