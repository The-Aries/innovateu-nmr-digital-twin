# InnovateU 2026 — NMR-Based Battery Health Digital Twin

**Project specification and implementation handover**

**Version:** 1.0 — concept finalized, implementation pending\
**Reference:** *From Spins to a Health Digital Twin*, challenge dossier v1.6

**Status conventions**

- **CONFIRMED:** Explicitly agreed project decision.

- **REQUIRED:** Challenge-dossier requirement.

- **PROPOSED:** Recommended implementation detail, to be validated or adapted by the coding agent.

- **BONUS:** Optional functionality outside the core prototype.

---

## 1. Project mission

### 1.1 Aim contract — CONFIRMED

**Develop an NMR-informed digital twin of an individual sodium-ion battery cell that monitors plating-related health deterioration over repeated charge–discharge cycles.**

The system uses ²³Na NMR spectroscopy to track the metallic-sodium signal remaining after discharge. It maintains a persistent estimate of residual metallic deposition, updates that estimate as measurements arrive, predicts its near-term evolution and provides qualitative warnings when accumulation becomes significant.

The demonstrator must distinguish genuine changes from measurement uncertainty and identify the most useful next measurement.

**Primary output:** An uncertainty-aware longitudinal **Residual Metallic Deposition Index (RMDI)**, together with health-trend and qualitative safety-warning indicators.

**Intended industrial value:** Support battery ageing research and early identification of plating-related deterioration that may otherwise remain hidden in purely electrical measurements. Assess robustness of cell design with respect to fast charging conditions, and trigger safety warnings in case accelerated plating is observed.

**Not claimed:** Quantitative capacity loss, remaining useful life, deposit thickness, short-circuit probability or a certified safety assessment.

**Dossier mapping:** §2.8, §9.2; Appendix J.6.

### 1.2 Physical counterpart and operating conditions — CONFIRMED

The physical counterpart is **one individual sodium-ion full cell**, initially modeled after the hard-carbon-based full cell studied by Bray et al. (2020).

The cell undergoes repeated charge–discharge cycles under standardized conditions:

- Fixed charging current.

- Fixed discharge protocol.

- Consistent initial and final states of charge.

- Controlled nominal temperature.

- Defined voltage and other experimental safety limits.

- NMR measurements after **every cycle** in the synthetic demonstration.

The model must retain cycle number, charge/discharge protocol and cell identity, but it does **not** need to model cell-to-cell variation.

**MRI imaging is not required.** The selected measurement modality is ²³Na NMR spectroscopy, but its methodology is expected to be transferable to Li-7.

---

## 2. Scientific foundation and data strategy

### 2.1 Real experimental data — CONFIRMED

**Reference:** Bray et al., *Operando visualisation of battery chemistry in a sodium-ion battery by ²³Na magnetic resonance imaging*, Nature Communications 11, 2083 (2020).

Article: [https://www.nature.com/articles/s41467-020-15938-x](https://www.nature.com/articles/s41467-020-15938-x)\
Dataset: [https://edata.bham.ac.uk/456/](https://edata.bham.ac.uk/456/)

**Use Figures 5–6** to demonstrate the physical interpretation and fitting of a metallic-sodium-related NMR signal in a sodium-ion full cell.

Relevant findings:

- The full-cell configuration has no sodium-metal counter electrode.

- A transient high-chemical-shift signal appears during the first formation charge at 30 mA/g.

- Its fitted position evolves approximately from 1050 to 1115 ppm before disappearing below detection.

**Figure 7** additionally provides post-charge and post-discharge spectra from another full cell of the same design. It does not experimentally establish the accumulation of persistent metallic sodium after discharge.

**Important source limitation:** The paper does not provide a controlled longitudinal dataset showing irreversible metallic-sodium accumulation over repeated cycles at fixed conditions.

The real data are therefore used for **spectral-method validation**, not as proof of the simulated ageing trajectory.

### 2.2 Synthetic longitudinal data — CONFIRMED

Generate clearly labeled synthetic spectra for a single cell over multiple cycles.

**Required synthetic observations per cycle:**

1. End-of-charge ²³Na NMR spectrum.

2. Post-discharge ²³Na NMR spectrum.

3. Associated experimental and acquisition metadata.

4. Known underlying synthetic deposition state, stored separately from the data exposed to the twin.

**PROPOSED simulation scenarios:**

- Initially negligible or undetectable residual metallic sodium.

- Progressive accumulation of a post-discharge metallic signal.

- Temporary noise-related fluctuations.

- At least one ambiguous detection.

- At least one technically invalid measurement.

- A more rapid accumulation phase for demonstrating safety-warning escalation.

Simulated peak positions and line shapes may be informed by the published real spectra, but the **cycle-dependent accumulation model is an explicit assumption**.

All data visualizations and exported values must distinguish `MEASURED`, `SIMULATED`, `DERIVED` and `INFERRED` information, including the origin of derived values.

**Dossier mapping:** §2.1, §4.8, §6.3; Appendix C.

---

## 3. NMR measurement and health indicator

### 3.1 Spectral analysis — CONFIRMED

Fit the metallic-sodium resonance using an empirical Gaussian model with a suitable baseline:

[\
S(\delta)=B(\delta)+H\exp\left[-\frac{(\delta-\mu)^2}{2\sigma^2}\right]\
]

For each spectrum, derive:

| Quantity | Symbol | Purpose |
| - | - | - |
| Peak amplitude | (H) | Detection relative to spectral noise |
| Peak center | (\mu) | Confirmation of the metallic resonance region |
| Peak width | (\sigma) | Signal characterization and quality control |
| Integrated peak area | (A=H\sigma\sqrt{2\pi}) | Main input to RMDI |
| Fit uncertainty | (u_A), (u\_\mu) | Quantifying confidence |
| Fit residual / SNR | — | Detection and measurement QC |

Peak integration must be consistent with the chosen model, baseline subtraction and spectral representation.

For the fitted center, find the uncertainty as:

[\
u\_\mu=\sqrt{\operatorname{Cov}(\hat\mu,\hat\mu)}\
]

The Gaussian width (\sigma) is **not** the uncertainty of the peak center.

Estimate uncertainty in integrated area using the fit covariance matrix, accounting for the correlation between amplitude and width. Record relevant additional systematic uncertainties separately.

**PROPOSED:** Begin with a fitting region around 1000–1200 ppm, verifying its suitability against the experimental spectra. The fitted position must remain physically plausible, but it should not be fixed to one exact chemical shift.

### 3.2 Metallic-sodium detection — PROPOSED

Use three detection classes:

| Fitted SNR | Preliminary classification |
| - | - |
| ≥ 5 | Detection |
| 3 to below 5 | Uncertain |
| Below 3 | Non-detection, provided acquisition quality is sufficient |

**The colleague must validate the final thresholds**, noise estimation, false-positive behavior and fit-quality criteria.

A measurement can pass acquisition QC while producing a non-detection. Conversely, a fitted peak should not be accepted solely because of its nominal SNR.

**Critical implementation rule:** Non-detection is **not equivalent to zero deposition**. Store an upper detection limit or an explicitly censored value rather than silently assigning RMDI = 0.

### 3.3 Residual Metallic Deposition Index — CONFIRMED

The principal health-related observable is the integrated **post-discharge metallic-deposit peak area**.

**Preferred, reference-normalized definition:**

[\
\boxed{\mathrm{RMDI}*n=*\
*\frac{A*{\mathrm{metal,post-discharge},n}}\
{A\_{\mathrm{reference},n}}}\
]

Here, (n) is the cycle number.

**Preferred reference:** A stable external ²³Na NMR reference, such as a sealed aqueous NaCl capillary, subject to appropriate geometry and intensity calibration.

**Accepted fallback:**

[\
\boxed{\mathrm{RMDI}*n=*\
*A*{\mathrm{metal,post-discharge},n}\
\quad[\mathrm{a.u.}]}\
]

If external-reference normalization is unavailable, maintain consistent measurement sensitivity and track peak area in arbitrary units.

**Implementation requirement:** Store the normalization method, measurement protocol, calibration status and uncertainty with every RMDI value. Values obtained using incompatible normalization methods must not be compared without justified correction.

The reference normalization is preferred, **not mandatory** for the prototype.

### 3.4 Interpretation — CONFIRMED

An increasing RMDI indicates an increasing **persistent NMR-visible metallic-deposition signal**, which is a possible sign of worsening plating-related health.

It is **not** a direct measurement of:

- Total irreversible sodium inventory loss.

- Deposited metal volume or mass.

- Physical deposit thickness.

- Capacity fade or electrochemical state of health.

RF skin-depth effects and deposit morphology can affect metallic NMR intensity. Some irreversible sodium loss may also occur through nonmetallic reaction products that RMDI does not detect.

Residual metallic sodium after discharge is treated as **potentially persistent deposition**, not automatically as proven electrochemically inactive metal.

**Future transferability:** The RMDI concept can be adapted to ⁷Li NMR, but lithium-metal cells may require methods to distinguish new deposits from the existing lithium-metal electrode signal.

**Dossier mapping:** §4.6, §4.10, §5.7.

---

## 4. Digital-twin state and update rules

### 4.1 Persistent state — CONFIRMED

Maintain a state object for the individual cell with the following minimum variables:

| State variable | Definition |
| - | - |
| `cell_id` | Stable physical counterpart identifier |
| `cycle_n` | Latest processed cycle |
| `rmdi_history` | Previous observations, limits, uncertainties and QC |
| `rmdi_current` | Latest accepted quantitative RMDI, if available |
| `rmdi_uncertainty` | Uncertainty of current RMDI |
| `health_trend` | `deteriorating`, `stable`, `undetermined` |
| `safety_warning` | Qualitative deposition-accumulation warning |
| `forecast_next_cycle` | Expected RMDI and prediction interval |
| `last_valid_cycle` | Last accepted quantitative measurement |
| `evidence_ids` | Links to spectra, feature records and packets |
| `state_version` | Incremented on every committed state update |

The complete history, including rejected measurements, remains available for audit.

**Do not fabricate state values when measurements are missing or uncertain.**

### 4.2 Rule-based state assimilation — CONFIRMED

The update algorithm is **rule-based**. No Kalman filter, Bayesian inference engine or machine-learning model is required.

**Required process:**

1. Ingest the new evidence packet.

2. Validate schema, units, experiment identity, acquisition conditions and QC checks.

3. Assess metallic-sodium detection and RMDI uncertainty.

4. Apply the declared update policy.

5. Compare the new accepted RMDI with previous reliable observations.

6. Update health classification and qualitative warning.

7. Generate the next-cycle forecast.

8. Record the update event, reasons and provenance.

**QC policy:**

| Evidence quality | Twin action |
| - | - |
| `PASS` | `update` with quantitative RMDI if detected reliably |
| `WARN` | `update_with_warning`; retain uncertainty and avoid unsupported health conclusions |
| `FAIL` | `reject`; log the evidence without changing the accepted quantitative health state |

**Important:** Detection confidence and acquisition QC are separate classifications. An uncertain or non-detected peak must not be converted into a reliable numerical RMDI simply because acquisition QC passed.

### 4.3 Health-change decision — CONFIRMED / PROPOSED

Compare each new reliable RMDI with the previous reliable value, accounting for uncertainty.

For independent observations:

[\
\Delta_n=\mathrm{RMDI}*n-\mathrm{RMDI}*{n-1}\
]

[\
u\_{\Delta_n}=\sqrt{u_n^2+u\_{n-1}^2}\
]

**PROPOSED demonstrator threshold:** A positive difference greater than (1.96u\_{\Delta_n}) qualifies as statistically significant under an approximate Gaussian-error model.

| Outcome | Classification |
| - | - |
| Significant positive increase | `deteriorating` |
| No significant change, adequate sensitivity | `stable` within measurement resolution |
| Ambiguous, missing, censored or unreliable evidence | `undetermined` |

The coding agent should make the statistical threshold configurable and document its limitations. Correlated errors, especially shared reference errors, must be considered if applicable.

The term `stable` must **not** be presented as proof that no degradation occurred.

**Dossier mapping:** §2.8, §7.2–7.5, §8.5; Appendix E.

---

## 5. Prediction and qualitative safety assessment

### 5.1 Next-cycle RMDI forecast — CONFIRMED

The twin must predict the expected RMDI for the next cycle and display an uncertainty interval.

**PROPOSED minimal algorithm:**

- After at least three suitable quantitative observations, fit a simple local linear trend over recent valid cycles.

- Propagate measurement uncertainty into an approximate prediction interval.

- With insufficient observations, report `insufficient evidence` or use an explicitly assumed constant-state scenario with a broad range.

- Preserve the forecast made *before* the next observation so prediction and measurement can later be compared.

This is a short-horizon statistical expectation, **not a mechanistic ageing model**.

The system should display:

- Current RMDI.

- Predicted next-cycle RMDI.

- Prediction interval.

- Actual next-cycle RMDI when received.

- Prediction discrepancy and possible explanations.

### 5.2 Qualitative safety-warning logic — CONFIRMED

Safety warnings refer to **persistent metallic-deposition accumulation**, not a calibrated probability of failure.

| Condition | Displayed assessment |
| - | - |
| No demonstrable increase | No evidence of increasing residual deposition |
| Significant positive trend | Accumulation warning |
| Rapid or accelerating increase | Elevated concern; further investigation recommended |
| Insufficient measurement confidence | Assessment unavailable or uncertain |

**PROPOSED:** Use trend significance and, when enough observations exist, a significant increase in the local slope to distinguish ordinary accumulation from accelerating accumulation. Thresholds remain configurable and unvalidated.

**Never display:** Percentage probability of short circuit, estimated dendrite thickness, or a claim that a cell is safe.

### 5.3 Next-evidence recommendation — REQUIRED

The twin should propose what measurement is most useful next.

Examples:

- **Reliable stable observation:** Measure again after the next standardized discharge.

- **Large RMDI uncertainty:** Repeat the spectrum, improve SNR or check calibration.

- **Possible instrument drift:** Verify frequency and sensitivity reference before interpreting the trend.

- **Unexpected increase:** Request a confirmatory measurement and inspect competing explanations.

- **Strong accumulation trend:** Flag the result for expert review.

These are scientific evidence recommendations, not automated safety-control commands.

**Dossier mapping:** §7.6–7.10.

---

## 6. Data contract, QC and provenance

### 6.1 Evidence-packet structure — REQUIRED

Implement a machine-readable JSON evidence packet based on the dossier's **schema v1.0**, adapted to battery NMR.

Minimum information:

| Group | Required fields |
| - | - |
| Identification | `packet_version`, `packet_id`, `subject_id`/`cell_id`, `session_id`, `cycle_n`, `relative_time` |
| Measurement | `modality`, `nucleus`, `measurement_stage`, `observable`, `value`, `unit`, `valid_range` |
| Acquisition | Field strength, spectrometer frequency, sequence, acquisition settings, spectral reference, measurement delay |
| Cell conditions | Charging current, discharge protocol, SOC endpoints, temperature and limits |
| Sample support | Named cell or coil-sensitive region; no invented spatial imaging coordinates |
| Trust | `uncertainty`, `qc_checks[]`, `qc_status`, `qc_reasons`, `system_qc_id`, `calibration_id` |
| Comparability | `protocol_match`, `comparable`, normalization method |
| Provenance | `source_object`, `source_sha256`, processing/version information and parent objects |
| Interpretation | `origin`, `value_epistemic`, `decision_epistemic`, `interpretation_limit` |
| Twin response | `twin_action` and update reason |

Use `modality = MRS` or another explicitly documented spectroscopy designation that the adapted schema accepts; do not label a conventional spectrum as an MRI volume.

The packet should be compatible with the dossier's shared interface model rather than inventing an unrelated data format.

### 6.2 Measurement QC — REQUIRED

Implement at least **five explicit machine-readable QC checks**. Recommended checks:

1. **Metadata completeness:** Required nucleus, acquisition, timing and reference information available.

2. **Protocol comparability:** Acquisition conditions and discharge endpoint consistent with the longitudinal baseline.

3. **System calibration:** Frequency and sensitivity/reference status acceptable.

4. **Spectral SNR:** Sufficient sensitivity to support the reported detection classification.

5. **Fit validity:** Peak position, width, residuals and fit convergence plausible.

6. **Uncertainty consistency:** Reported feature uncertainty compatible with fitting and repeatability estimates.

7. **Measurement timing:** Post-discharge acquisition performed within the declared timing window.

8. **Provenance integrity:** Source references, processing versions and hashes valid.

Each check must expose its value, unit, threshold, PASS/WARN/FAIL result and scientific owner.

**The dossier's teaching thresholds for clinical ¹H spectroscopy must not be copied directly to ²³Na battery NMR.** Battery-specific QC limits must be selected and documented.

### 6.3 Uncertainty budget — REQUIRED

Include a compact uncertainty card covering:

- Spectral noise and fit covariance.

- Peak-model and baseline mismatch.

- Frequency referencing and field drift.

- RF sensitivity, coil loading and sample positioning, when available.

- Reference-signal stability, where applicable.

- Test–retest variation.

- Timing differences after discharge.

Identify the dominant contributor and propose at least one improvement.

**PROPOSED metrology improvement:** A reproducible sample-positioning and frequency/reference-calibration procedure.

### 6.4 Provenance — REQUIRED

Maintain this traceable chain:

**Source spectrum → preprocessing → Gaussian fit → derived peak area → QC → RMDI evidence packet → twin update → forecast/warning**

A user must be able to inspect why a particular RMDI point was accepted, rejected or assigned high uncertainty.

Store processing versions and source hashes. Synthetic ground truth must remain separately identifiable.

**Dossier mapping:** Chapters 5, 6 and 8; Appendices B and E.

---

## 7. Minimum dashboard specification

Build one integrated dashboard for the individual-cell demonstrator.

| View | Required functionality |
| - | - |
| **1. Cell overview** | Cell ID, cycling conditions, latest RMDI, health classification, qualitative safety warning |
| **2. Health trajectory** | RMDI versus cycle number, error bars, non-detection limits, accepted/rejected measurements and next-cycle forecast |
| **3. NMR evidence** | Select cycle and measurement stage; display spectrum, Gaussian fit, residuals, peak parameters and uncertainty |
| **4. Twin update** | Show prior state, new evidence, QC gate, update action and resulting state |
| **5. Trust and provenance** | QC checks, uncertainty budget, metadata, origin labels, source and processing history |
| **6. Next evidence** | Recommended next measurement or calibration, with explanation |

**Minimum interaction:**

A user selects a cycle or ingests a new evidence packet. The dashboard visibly updates the twin and explains the result.

Clearly distinguish **measured observations**, **synthetic examples**, **model predictions** and **inferred health assessments**.

A simple Python/Streamlit, Dash or HTML/JavaScript implementation is sufficient. The dossier does not require a particular framework.

---

## 8. Minimum demonstrator and acceptance tests

### 8.1 Required demonstration sequence

The coding agent should provide a reproducible single-cell synthetic dataset with multiple cycles, then demonstrate:

1. Baseline NMR evidence and an initialized twin state.

2. A later valid observation showing increased RMDI.

3. A QC-gated persistent state update.

4. A revised health classification and qualitative warning.

5. A forecast for the subsequent cycle.

6. A next-evidence recommendation.

7. A complete provenance trace back to the source spectrum.

### 8.2 Essential regression tests

| Test | Expected behavior |
| - | - |
| Reliable RMDI increase | Twin records significant deterioration if uncertainty supports it |
| Change smaller than uncertainty | No unsupported deterioration claim |
| No detectable metallic peak | Record non-detection/upper limit, not a fabricated zero |
| Invalid measurement | Reject health update, retain failed evidence |
| Uncertain measurement | Preserve ambiguity without silently creating a precise health state |
| Changed acquisition sensitivity | QC warning or rejection unless comparability is demonstrated |
| Changed processing version | Visible provenance/version change |
| Missing source or wrong units | Packet validation fails |
| Too few observations | Forecast remains explicitly uncertain or unavailable |
| Synthetic evidence | Always displayed and exported with synthetic origin |

**Dossier maturity target:** At least Level 3, demonstrating persistent evidence-driven updating. A simple next-cycle forecast supports Level 4. A justified next-evidence recommendation addresses the dossier's evidence-steering objective.

---

## 9. Required hackathon deliverables and dossier mapping

| Dossier requirement | Implementation artifact |
| - | - |
| **§9.2 — Aim contract** | Project mission and counterpart, §1 of this specification |
| **§4.10 — Measurement model** | ²³Na spectroscopy and Gaussian fitting card |
| **§5.11 — Metrology** | Calibration/repeatability concept, uncertainty budget and QC limits |
| **§6.11 — Data Science** | Data dictionary, schema-compatible packets, at least five QC checks, provenance |
| **§7.10 — Digital Twins** | Persistent state, observation model, gated update, forecast, uncertainty and next evidence |
| **§8.5 — Integration** | One auditable baseline-to-follow-up update |
| **§8.7 — Regression** | Scientific, schema, uncertainty, provenance and update tests |
| **§9.7 — Challenge canvas** | One-page mission and system-architecture diagram |
| **§9.7 — Prototype** | Functional dashboard containing the views in §7 |
| **§9.7 — Interpretation** | Competing explanations and scientific limitations |
| **§9.7 — Pitch** | Five-minute presentation of the working evidence-to-decision chain |
| **Appendix F — Handover** | Traceable interfaces and outputs for the four challenge tracks |

**Recommended prototype priorities:** Measurement correctness, persistent update logic, uncertainty, QC and provenance take precedence over sophisticated visualizations or AI.

---

## 10. Optional functionality and future development

### BONUS A — Adaptive charging-current optimization

Retain our original optimization concept as a separate module:

- Compare charging experiments over a fixed SOC window.

- Use end-of-charge NMR detection as the primary criterion.

- Increase the charging current initially by **0.25C**.

- Reduce the next increment to **0.1C** after an uncertain result.

- Stop increasing current following reliable detection.

- Report the highest previously tested current with reliable non-detection as a **candidate plating-onset boundary**.

This is not a validated safe charging limit, and end-of-charge non-detection cannot exclude transient plating.

**Bayesian optimization** is an additional bonus extension, not part of the baseline implementation.

### BONUS B — More advanced health models

- Measurement-efficient cycling and NMR scheduling.

- Physics-informed forecasting of metallic deposition.

- Correlation of RMDI with measured capacity fade.

- Transfer to other cell chemistries or ⁷Li NMR.

- 3D MRI-based apparent deposit-volume analysis, if appropriate data become available.

Do not implement these before the core evidence-to-state chain works.

---

## 11. Final scientific limitations

The finished code, dashboard and pitch must make the following distinctions explicit.

**RMDI measures an NMR signal, not deposited mass.** Its relationship to the true quantity of metallic sodium depends on morphology and measurement physics.

**Residual metal is not necessarily electrochemically irreversible.** Some residual metal might remain recoverable, while other irreversible sodium losses are invisible to the metallic NMR signal.

**A rising RMDI is not a measured failure probability.** It supports a qualitative plating-related warning, not a quantitative safety certification.

**Synthetic ageing does not validate real degradation kinetics.** The published paper supports metallic-sodium signal interpretation, not the assumed longitudinal accumulation trajectory.

**The twin represents one cell.** It should not claim statistical conclusions about manufacturing populations or other battery designs.

**No autonomous safety control.** The software recommends evidence and highlights uncertainty; experimental decisions remain with the responsible operator.

---

## 12. Implementation instruction for the coding agent

**Build the simplest complete, auditable digital twin satisfying the specifications above.**

The implementation must demonstrate the following complete chain:

**Synthetic/real NMR source → Gaussian peak fitting → quantified measurement uncertainty → QC-gated RMDI evidence → persistent individual-cell state → health assessment → next-cycle forecast → qualitative warning → recommended next evidence.**

Keep raw and derived data separate. Make all experimental assumptions, thresholds and processing versions explicit. Use synthetic longitudinal accumulation to demonstrate functionality, without implying that the published experiment established those results.

**A successful final dashboard lets a reviewer answer three questions:**

1. **What changed in the cell's measured plating-related health indicator?**

2. **Why does the available NMR evidence justify—or fail to justify—that assessment?**

3. **What should we measure next to improve confidence?**

Those three questions define the scientific and digital-twin purpose of the project.
