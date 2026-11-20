# NMR Hackathon project plan

## Aim and decisions

**Aim.** Decide whether the change in a metal-region ²³Na spectral signal during the formation cycle of one sodium-ion full cell is sufficient to update a signal state. Use two audited acquisitions from Birmingham Figure 5. Show the effect of measurement choices, the gate decision, and the next measurement that would reduce uncertainty.

| Decision | Scope |
| --- | --- |
| Main study | Bray et al. (2020), Figures 5 and 6. Use the public Figure 5 files for the demonstration. [Paper](references/papers/Bray_et_al_2020_Operando_Sodium_Ion_Battery_NMR.pdf) · [Data](https://edata.bham.ac.uk/456/) |
| System and data | One sodium-ion full cell during its first formation cycle. Figure 5 has 16 ²³Na NMR acquisitions (60–75) and 99,841 electrochemistry rows. Figure 6 supplies published time context. |
| State variable | Latest accepted signed integral of the 1020–1150 ppm metal region, in a.u.·ppm. This is a relative signal indicator for one cell. Physical claims about mass, morphology, SOC, SOH, or charging safety require independent validation. |
| Comparison | Use acquisitions 61 and 63 and the same saved processing number 2. The signed baseline integral includes background. Its negative value is valid as a signed feature. |
| Timing | Use TopSpin audit start and end times for NMR. Mark each acquisition window. The electrochemistry zero point is provisional relative to NMR. The state update uses confirmed NMR timing. |
| Update policy | Apply the Birmingham gate. A FAIL leaves the state unchanged. A WARN requires explicit acceptance. The latest accepted observation then becomes the state. |
| Evidence interface | Read the original local files in the browser. Generate challenge v1.0 evidence packets from the measured inputs. Keep the update event separate within the export bundle. |
| Reference and scope | Keep the organizer's MRI/MRS case for reproducing the worked example. The Bruker workbench and Cambridge data support independent spectroscopy checks. The Birmingham pitch uses the Bray study as its research case. |

The authoritative requirements are in [Dossier v1.6](MRI_Local_Spectroscopy_Health_Digital_Twin_Hackathon_Dossier_v1.6.pdf), especially §§1.4, 4.10, 5.11, 6.11, 7.10, 8.2–8.7, 9.6–9.10 and Appendix J.6. [The Quantum Engineering slides](NMR_QE_InnovateU_Conclusion_v2.3_2026-11-20.pdf) map the four tracks to device and biomedical examples.

## Tasks and acceptance

The four tracks perform one connected update. The outputs below serve as handovers and as material for the pitch.

| Stage | Task and deliverable | Birmingham acceptance |
| --- | --- | --- |
| **Measure · Quantum Engineering** | Write the measurement card and specify the observation model, units, settings, physical meaning, and failure modes. | Link the acquisition to its FID. Recompute the feature from the saved Bruker spectrum using ppm referencing, intensity scaling, baseline correction, and signed integration. Explain why the signal can change with phase or background. |
| **Measure · Quantum Engineering** | Prepare a known-truth reference for checking the method. | Show a synthetic peak with a declared integral or reproduce the organizer's known-truth reference. Label synthetic inputs and outputs and keep them separate from the measured Birmingham result. |
| **Validate · Metrology** | Write the uncertainty card, including calibration status, repeatability evidence, and the dominant contributors. | Report the per-acquisition method-sensitivity allowances. The sideband residual term is the largest of the three implemented terms in both acquisitions. Report unverified calibration and repeatability as open. The allowance has no established statistical coverage. |
| **Validate · Metrology** | Define the comparison checks and explain the competing interpretations. | Show chronological windows, comparable acquisition and processing settings, stored phase, baseline and follow-up detection, and the change relative to the combined allowance. Show that a phase or background difference can change the reported area. Record provisional electrochemistry alignment separately. |
| **Represent · Data Science** | Deliver a standalone machine-readable dictionary and one schema v1.0 evidence example. | Export 61 → 63 in Explorer, extract the dictionary and follow-up packet from the bundle, and run schema and semantic validation. Record source paths, settings, analysis version, units, measurement window, and QC reasons. Mark the raw source `MEASURED`, the spectral feature `DERIVED`, and the decision `INFERRED`. |
| **Represent · Data Science** | Demonstrate normalization, at least five checks, and end-to-end provenance. | Show how TopSpin values and identifiers are mapped, including the intensity scale and relative seconds. Display all seven comparison checks and their reasons. Trace #63 back to its `1r`, `1i`, `procs`, `acqus`, `fid`, and audit log. Export the processing version. Record the source digest as unavailable if needed. |
| **Integrate · Digital Twins** | Demonstrate prior, evidence, gate, and updated state. Record the update. | Open the local [Birmingham Explorer](MRI_Data_Explorer_Birmingham.html), load Figure 5, and run the default 61 → 63 update. Show both WARN reasons and explicitly accept them. Export the bundle after updating. Use a failing comparison to verify that it cannot change the state. |
| **Integrate · Digital Twins** | Present a scenario or prediction, a competing-explanations view, and the next-evidence proposal. | Use the measured change and its allowance to explain why the update can be accepted with warning and what stronger uncertainty would imply for the gate. Propose a repeat under matched phase and acquisition settings, with one trigger shared by NMR and electrochemistry. Present any voltage forecast as a separately labelled within-cycle analysis. |
| **Integration and submission** | Prepare the one-page challenge canvas and architecture. Rehearse the five-minute pitch, limitations statement, and audit. | Include the aim, one measurement, one state, the four handovers, and a source-to-state diagram. Each team member should trace the state to the raw evidence and explain the two warnings. Check eligibility and disclosure requirements with the mentor. Add an individual reflection if seeking course credit. |

## Reproduce the default update

1. Download and extract [Figure_5.zip](https://edata.bham.ac.uk/456/4/Figure_5.zip). Use the path in the [README](README.md#experimental-data-downloads).
2. Open the [Birmingham Explorer](MRI_Data_Explorer_Birmingham.html) and select the extracted `Figure_5` directory.
3. Compare acquisitions 61 and 63. Verify the expected values below.
4. Accept the warning and apply the update. Inspect the updated state, then export the evidence and update JSON.
5. Verify that the exported follow-up packet passes the [v1.0 schema](MRI_Hackathon_DataScience_StarterPack_v0.3/05_TwinReady_JSON_CSV/evidence_packet_v1.0.schema.json). Replay from the source data before the pitch.

| Quantity | Expected value |
| --- | --- |
| Baseline #61 | −3.96 × 10⁶ a.u.·ppm, allowance 5.85 × 10⁶ a.u.·ppm |
| Follow-up #63 | +8.51 × 10⁶ a.u.·ppm, allowance 4.07 × 10⁶ a.u.·ppm |
| Change and combined allowance | +12.47 × 10⁶ and 9.92 × 10⁶ a.u.·ppm |
| Decision | WARN for baseline signal unresolved and stored phase difference. Explicit acceptance updates the signal state to #63. |

The Explorer reads the original files and exports the two packet objects, dictionary, alignment, and update record. Both default packets passed the challenge schema and semantic validation in a local check. The organizer's MRI update engine has different requirements for numerical standard uncertainty and system QC. Use the Birmingham gate for this case. See the [case walkthrough](references/en/birmingham_digital_twin_explained.md) for the data, method, and replay limits.

## Before the pitch

- Package the standalone evidence example and dictionary. Keep generated outputs and raw experimental downloads in their ignored local directories.
- Finish the canvas, measurement card, uncertainty card, and five-minute pitch. Show the alternative explanation and the repeat with synchronization.
- Run the offline 61 → 63 demonstration from the source files. Test FAIL rejection and WARN acceptance. Confirm that each presented result links back to the correct acquisition and processing method.
- Confirm submission and pre-work rules and disclose the use of AI tools as required. The demonstration supports a within-cell change in a spectral signal. Absolute sodium deposition, long-term behavior, and safety would need independent measurements and validation.
