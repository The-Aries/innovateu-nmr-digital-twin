# InnovateU 2026 — NMR-Powered Battery Digital Twin

Team submission for the NMR Quantum Engineering challenge (20–21 November 2026, KICU Ulm).

During fast charging, sodium can plate on the anode as metal. Discharge dissolves part of this deposit. The twin asks one question for each cycle of one sodium-ion cell: did the metal dissolve after discharge, or did it remain? A post-discharge ²³Na NMR spectrum supplies the answer. The fitted metallic-sodium peak area, normalized to a reference, is the Residual Metallic Deposition Index (RMDI). The twin accepts an RMDI value only after quality control. It stores weak signals as upper limits, tracks the trend with its uncertainty, and proposes the next measurement.

The measured basis is Bray et al., *Nat. Commun.* 11, 2083 (2020): operando ²³Na NMR of a sodium-ion full cell. The cycling trajectory is **simulated**. Acquisition parameters, line widths, noise and the metal shift range come from the published data.

## Open the demonstrators

| Demonstrator | What it shows | How to open |
| --- | --- | --- |
| RMDI dashboard | Python pipeline output for 12 simulated cycles: guided demo, twin decision, spectrum, fit diagnostics, quality checks, provenance trace, packet download | [Offline dashboard](evidence/rmdi-dashboard/rmdi-dashboard.html) or the [online version](https://innovateu-sodium-ion-twin.rusticarbor4.chatgpt.site) |
| Battery Twin Explorer v1.1 | Browser-only twin over 16 simulated cycles, with published Figure 6 and 7 spectra as measured examples | Open [battery-twin-explorer-v1.1.html](battery-twin-explorer-v1.1.html), select **Load data**, and choose `evidence/explorer-input/`. For the measured spectra, also download Figures 6 and 7 (see [Data sources](#data-sources)). |

## Required deliverables (dossier §9.7)

| Deliverable | Location |
| --- | --- |
| System architecture | [Architecture](rmdi-dashboard/docs/architecture.md) |
| Machine-readable evidence packets (schema v1.0) | [Packet schema](rmdi-dashboard/schema/evidence_packet_v1.0.schema.json) and 24 [example packets](evidence/rmdi-verified-run-20261121/packets/) |
| Data dictionary | Exported as `data-dictionary.json` from the Explorer's **Provenance & export** view |
| Measurement card | [Measurement model](rmdi-dashboard/docs/measurement.md) |
| Uncertainty card | [Uncertainty budget](rmdi-dashboard/docs/uncertainty.md) |
| Prototype with a baseline-to-follow-up update | Both demonstrators. Update logic: [twin](rmdi-dashboard/docs/twin.md) |
| Provenance view | Dashboard **Trust & provenance** and **Trace this result**; Explorer **Provenance & export** |
| Uncertainty and competing explanations | [Quality control and detection](rmdi-dashboard/docs/qc.md) and the dashboard's fit diagnostics and quality checks |
| Next-evidence proposal | Dashboard **Twin decision**; Explorer **What to measure next** |
| Five-minute pitch | [Pitch deck](pitch/Battery-Twin%5FPitch.odp), [workflow slides](pitch/Battery-Twin%5FWorkflow.pptx), [pitch outline](rmdi-dashboard/docs/business.md) |
| Limitations statement | [Scientific limitations](rmdi-dashboard/docs/limitations.md) |

[AI use disclosure](AI_USE_DISCLOSURE.md)

## Reproduce the results

Run from `rmdi-dashboard/` with Python 3.11 or newer.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install numpy scipy jsonschema pytest
.venv/bin/python -m src.run demo --output outputs/demo
.venv/bin/python -m src.run verify --output outputs/demo
.venv/bin/python -m pytest -q
```

The suite has 41 tests. To check the stored run instead of a new one, use `--output ../evidence/rmdi-verified-run-20261121`. See the [verification report](rmdi-dashboard/docs/verification.md) and the [demonstrator README](rmdi-dashboard/README.md).

## Repository layout

| Path | Contents |
| --- | --- |
| `rmdi-dashboard/` | Pipeline source, schema, tests and scientific documentation |
| `battery-twin-explorer-v1.1.html` | Self-contained browser Explorer |
| `evidence/` | Verified run (2026-11-21), offline dashboard and Explorer input packets |
| `pitch/` | Pitch deck and workflow slides |
| `references/` | Bray et al. (2020), [case walkthrough](references/en/birmingham_digital_twin_explained.md), [figure guide](references/en/birmingham_bray_2020_data_guide.md) and [background references](references/en/battery_mr_references_en.md) |
| `docs/` | [Decision log](docs/DECISIONS.md) and preparation notes from before the event |
| `materials/organizer/` | Organizer dossiers, slides and StarterPack v0.3. The tests use its packet schema. |

## Data sources

Git ignores downloaded third-party data. Keep it under `online downloaded data/`.

| Dataset | Download | Local location |
| --- | --- | --- |
| Bray et al. Figure 6 spectra (Explorer v1.1) | [Figure_6.zip](https://edata.bham.ac.uk/456/5/Figure%5F6.zip) | `online downloaded data/Figure_6/` |
| Bray et al. Figure 7 spectra (Explorer v1.1) | [Figure_7.zip](https://edata.bham.ac.uk/456/6/Figure%5F7.zip) | `online downloaded data/Figure_7/` |
| Figure 5 time series and electrochemistry (earlier analysis) | [Figure_5.zip](https://edata.bham.ac.uk/456/4/Figure%5F5.zip) | `online downloaded data/Figure_5/` |
| Supplementary Figures 3 and 8 (measurement review) | [SupplementaryFigure_3.zip](https://edata.bham.ac.uk/456/14/SupplementaryFigure%5F3.zip), [SupplementaryFigure_8.zip](https://edata.bham.ac.uk/456/10/SupplementaryFigure%5F8.zip) | `online downloaded data/Bray_2020_Measure_review/` |
| Supplementary information | [41467_2020_15938_MOESM1_ESM.pdf](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-15938-x/MediaObjects/41467_2020_15938_MOESM1_ESM.pdf) | `online downloaded data/Bray_2020_SI/` |
| Synthetic Na23 RMDI replay v3, full archive | [Na23_RMDI_Replay_v3.zip](https://github.com/The-Aries/innovateu-nmr-digital-twin/raw/d143100a6ab5dbd1502b37e15a48d357d2eec33a/Na23%5FRMDI%5FReplay%5Fv3.zip) (commit `d143100`) | Explorer packets are in `evidence/explorer-input/` |
| All other Birmingham archives | [Birmingham data record](https://edata.bham.ac.uk/456/) | — |

To show the measured spectra in the Explorer, extract Figures 6 and 7 next to `generated_data_set/` and load the parent folder.

Official brief: https://www.uni-ulm.de/en/io/degree-phd/students/fit4u/community/vernetzung/hackathon/
