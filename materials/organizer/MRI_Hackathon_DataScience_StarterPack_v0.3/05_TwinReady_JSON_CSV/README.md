# Twin-ready interface (StarterPack v0.3)

- `packets/` — evidence packets v1.0, one per observable: `E-t0-*` (baseline, month 0), `E-t1-*` (follow-up, month 6) and
  `E-t1-chobad` (an intentionally invalid FAIL example that must never update the twin).
- `evidence_packet_v1.0.schema.json` — JSON Schema 2020-12 of the packet (Hackathon Dossier v1.0, section 8.2).
- `thresholds-v1.0.json` — machine-readable gates and the twin policy (dossier section 5.8).
- `data_contract.json` — what the twin layer requires.
- `features.csv`, `data_dictionary.csv` — compact feature table with units, owners and epistemic labels.
- `qc_report.json` — follow-up QC; note `not_run_by_pipeline`.
- `legacy_v0.2/` — the v0.2 files, kept for the migration exercise (v0.2 packet -> v1.0 packets).

Teaching rule: never turn FAIL evidence into PASS by silently filling a value. Preserve the issue and route it to the owning track.
The follow-up ROI packet is stored as PASS because its pipeline did not run the consistency rule `roi_u_consistency` of
thresholds v1.0. Run the rule (the MRI Data Explorer does) and decide what the twin should do.
