# Standalone ²³Na RMDI demonstrator

## Present and explore the twin

Open the [online dashboard](https://innovateu-sodium-ion-twin.rusticarbor4.chatgpt.site) or use the [offline dashboard](../evidence/rmdi-dashboard/rmdi-dashboard.html). **Guided demo** walks through the upper limit, first accepted value, rejected acquisition and supported increase. **Explore** lets visitors select any cycle, compare end-of-charge and post-discharge spectra, inspect QC, and download the selected evidence packet. The offline HTML contains the plots, interface and verified simulated replay.

Rebuild the dashboard from a verified run with the existing Python environment. Run this from the standalone directory.

```sh
.venv/bin/python -m src.build_dashboard --run outputs/demo --output ../evidence/rmdi-dashboard/rmdi-dashboard.html
```

## Run the standalone demonstrator

Use Python 3.11 or newer from this directory. Use a fresh output path for each replay.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install numpy scipy jsonschema pytest
.venv/bin/python -m src.run demo --output outputs/demo
.venv/bin/python -m src.run verify --output outputs/demo
.venv/bin/python -m src.run calibrate-detection --output outputs/detection.json
.venv/bin/python -m pytest -q -s
```

The replay writes one spectrum and packet per measurement, linked processing artifacts, the persistent twin and an audit manifest. The separate truth file is available for validation. Run the verifier from the same working directory as the replay so relative provenance paths resolve. See [the Mac mini verification results](docs/verification.md) and [the architecture](docs/architecture.md).

## Approved M0 contract

Build one auditable synthetic cycling case for an individual sodium-ion cell. Each simulated cycle supplies an end-of-charge spectrum and a standardized post-discharge spectrum. Only the post-discharge observation can update the Residual Metallic Deposition Index (RMDI). Define RMDI as the fitted metallic-sodium peak area divided by the fitted area of a simulated external ²³Na reference, with unit `1`. Retain standalone peak area in `[arb'U].ppm`. The value represents relative NMR signal intensity. The normalization, simulation and acquisition assumptions travel with the evidence.

M0 established this layout, [config.yaml](config.yaml), the [packet schema](schema/evidence_packet_v1.0.schema.json), and [typed signatures](interfaces.pyi). The YAML uses JSON syntax so Python's standard library can load it. Each config entry carries a value, status and source. Review the empirical threshold and upper-limit scope before changing the simulation or applying the method to another acquisition.

## Layout and ownership

| Owner | Milestone | Paths |
| --- | --- | --- |
| Integrator | M0 and integration | `README.md`, `config.yaml`, `interfaces.pyi`, CLI and gate review |
| A | M1 simulation and fitting | `src/sim.py`, `src/fit.py`, `tests/test_fit.py` |
| B | M2 detection and QC | `src/detect.py`, `src/qc.py`, `tests/test_detect.py` |
| C | M3 twin state and forecast | `src/twin.py`, `tests/test_twin.py` |
| D | M4 packet, provenance and regression | `src/packet.py`, `schema/`, `tests/test_regression.py` |
| E | Scientific documentation | `docs/` excluding `docs/business.md` |
| F | Business concept | `docs/business.md` |

Generated spectra, truth, packets, state and logs belong in an ignored `outputs/` directory. The team specification and the organizer's dossier are reference documents for the standalone implementation. The organizer's v1.0 packet is the shared interface. This project's schema adds cycling stage, detection, sample support and provenance constraints. The documentation covers the [measurement model](docs/measurement.md), [uncertainty budget](docs/uncertainty.md), [QC](docs/qc.md), [twin](docs/twin.md), [limitations](docs/limitations.md) and [business concept and pitch](docs/business.md).

## Measurement and evidence handover

1. **Simulation.** Produce reproducible spectra from the versioned config. Assign independent deterministic random streams to stages and cycles. If testing zero filling, start with time-domain noise and transform it through the same processing as the signal. Store latent truth in a separate artifact for validation. The fit and twin entry points receive spectra or evidence only.
2. **Fit.** Use a Gaussian with a local baseline as the primary empirical estimator. Define area as the integral of the full fitted line. Keep the integration definition fixed when varying the fitting window or line shape. Use the fit covariance, including the height–width cross term, to propagate random area uncertainty. Fit the external reference independently in its declared spectral window. For the ratio, use the Jacobian for numerator and denominator and state any covariance assumption. Report window and Gaussian-versus-pseudo-Voigt shifts as model sensitivity. Treat correlated noise and nonlinear behavior near the detection boundary in coverage checks.
3. **QC and detection.** Record acquisition and fit QC independently of detection. Use at least five machine-readable checks, including metadata, comparability, fit validity, SNR and residuals. Report false-positive and detection rates for the full search as configured, including the free peak center. A censored result has a null value and may carry a positive upper limit with a documented construction. If a validated upper limit is unavailable, keep it null. An uncertain or invalid result also has a null value. SNR candidates in the config require simulation evidence before adoption.
4. **Packet.** Serialize one packet per spectrum. Use `eoc_metal_area` for end-of-charge and `rmdi` for post-discharge. Retain source SHA-256, processing and config revisions, input digests, parent references, QC reasons and an interpretation limit. Link the ordered stages from source spectrum through preprocessing, fit, area and QC. Failed or incomplete source input remains visible in the run log. A dossier-format packet requires an identifiable source. Validate stage, unit, state eligibility, comparison and provenance semantics after JSON Schema validation.
5. **State and audit.** Store the state and decisions together in a persistent JSON snapshot. Commit via atomic replacement. A replay of the same packet is idempotent. A conflicting duplicate or out-of-order post-discharge packet gets an explicit rejection. Only comparable, detected `PASS` post-discharge values enter the reliable history. `WARN` can record qualified evidence but cannot advance the reliable estimate or drive a new health classification. `FAIL` is logged and leaves the accepted state alone. A censored or uncertain follow-up leaves the numerical estimate in place and reports the latest comparison as undetermined. End-of-charge packets offer context. A forecast is stored before its target observation is ingested.
6. **Interpretation.** Propose the next measurement based on the evidence gap. Label the forecast as a short-horizon statistical result for a simulated cell. Use an independent-error change rule only under its stated assumptions. Declare how uncertainty affects the change decision and exclude imprecise observations from claims of stability.

## Scientific reference points

- Bray et al. Figure 5 documents one formation cycle. Supplementary Table 6 lists a 1109 ppm fitted component after 1.5 hours of charge, width 12,632 Hz, 20% fitted fraction and 0% Gaussian. The width is approximately 119 ppm. Under DMfit's mixing convention the fitted component is Lorentzian. The fitted fraction is specific to that spectrum. [Bray et al. and supplement](https://pmc.ncbi.nlm.nih.gov/articles/PMC7190614/#Sec12) · [DMfit convention](https://nmr.cemhti.cnrs-orleans.fr/Dmfit/Howto/1D_GLlines.aspx)
- The reported acquisition spans about 2360 ppm with 512 points and zero filling to 2048. The simulated point count describes the simulator's grid. Zero filling increases grid density without creating independent measurements. [Bray et al., Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC7190614/)
- The simulated post-discharge trajectory, reference strength and noise are scenario parameters. Figure 5 informs the spectral model. Figure 6 supplies selected spectra and Figure 7 supplies a different protocol. The measured formation cycle and simulated cycling trajectory support different claims. [Birmingham archives](https://edata.bham.ac.uk/456/) · [Team specification](../references/external/innovateu_nmr_battery_health_proposal.md)

## Review gates

M1 verifies known-integral recovery, uncertainty coverage and peak-model sensitivity. M2 evaluates false-positive behavior, detection performance and censoring. M3–M4 verify the team specification's regression cases and the dossier's applicable integration checks. The integrated replay traces baseline, later evidence, QC-gated update, forecast, next measurement and provenance. A dashboard is a subsequent milestone.
