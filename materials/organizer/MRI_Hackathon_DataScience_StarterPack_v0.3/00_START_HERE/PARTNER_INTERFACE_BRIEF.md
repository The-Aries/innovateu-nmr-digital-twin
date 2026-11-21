# Partner Interface Brief — one integrated hackathon demonstrator

The four partner lectures are **not four independent mini-courses**. Each lecture should prepare one interface artifact that the mixed hackathon team needs for a single baseline-to-follow-up update.

| Layer | Core question | Lecture emphasis | Required handover |
|---|---|---|---|
| Quantum Engineering | What is physically observed? | MRI/MRS signal meaning, spatial/spectral localisation, quantitative vs contrast-weighted observables, physics QC | Measurement card + interpretable observables |
| Precision Mechanics / Metrology | Can the observation be trusted and reproduced? | geometry, B0/B1/gradient effects, calibration, drift, repeatability, traceability, uncertainty | Calibration/uncertainty card + thresholds |
| Data Science | How is the evidence represented and checked? | DICOM/NIfTI/BIDS/MRS-BIDS, JSON/CSV contract, missing/invalid values, units, identifiers, provenance | `qc_report.json` + `evidence packet (packets/*.json)` |
| Digital Twins | How does accepted evidence update the model? | state vs observation, input contract, time alignment, update logic, uncertainty, scenarios, next-measurement logic | state/update contract + one update event |

## Shared quality gate

Quality is shared but responsibility is explicit:

1. **Quantum Engineering** flags physics/acquisition problems and defines physically meaningful observables.
2. **Precision / Metrology** supplies calibration status, repeatability, geometric/field uncertainty and acceptance thresholds.
3. **Data Science** validates structure, data types, required fields, identifiers, units, missingness, plausible technical ranges, de-identification and lineage. It **must not silently repair or impute scientific evidence**.
4. **Digital Twins** defines which inputs are required for an update and applies `PASS`, `WARN`, `FAIL` acceptance logic.

Every rejected or downgraded item should preserve a machine-readable reason.

## Final integration layer

The minimum integrated demonstration is:

`prior state -> follow-up evidence -> quality gate -> evidence packet -> twin update or rejection -> uncertainty view -> next-measurement recommendation`

The final prototype should show at least one complete trace from a source file to a twin variable.
