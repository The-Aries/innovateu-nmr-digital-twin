# Industrial concept and five-minute pitch

## Intended use

**Target users.** Sodium-ion battery ageing labs and cell-design teams evaluating fast-charge robustness.

**Problem.** Electrical measurements describe cell performance. Early plating-related deterioration may remain hidden in those measurements, leaving teams with limited evidence about whether residual metallic sodium is accumulating across cycles.

**Value.** Add a post-discharge ²³Na NMR measurement to the electrical test workflow. The Residual Metallic Deposition Index (RMDI) follows a metal-related NMR signal over time with an estimate of measurement uncertainty. A supported increase can flag accumulation for investigation and help the lab choose a confirmatory measurement. Comparing the signal under controlled protocols could inform fast-charge validation. [Team specification §1.1](../../references/external/innovateu_nmr_battery_health_proposal.md#11-aim-contract--confirmed)

**Claim boundaries.** Quantitative capacity loss, remaining useful life, deposit thickness, short-circuit probability, and certified safety assessment are outside the industrial claim. The demonstrator illustrates the evidence workflow for one simulated cell. [Team specification §1.1](../../references/external/innovateu_nmr_battery_health_proposal.md#11-aim-contract--confirmed) · [Demonstrator scope](../README.md)

## Five-minute pitch

| Time | What to say and show |
| --- | --- |
| 0:00–0:45 | Introduce the lab question. Is there evidence that the residual metallic-sodium signal is increasing after standardized discharge? Explain how an NMR measurement complements electrical monitoring. |
| 0:45–1:40 | Show the first accepted post-discharge observation and a later accepted increase. Label both `SIMULATED`. Identify the fitted metal peak, the simulated reference peak, and the ratio used for RMDI. |
| 1:40–3:20 | Open the evidence packet. Trace the value to the spectrum and fit, then show the uncertainty, QC decision, and recorded update. Use a censored or rejected observation to show how the record preserves incomplete evidence. |
| 3:20–4:15 | Explain the change decision and show the short-horizon forecast with its prediction interval. Describe the warning as a reason to investigate the simulated accumulation. |
| 4:15–5:00 | Propose the next measurement. Repeat the post-discharge spectrum with the same discharge protocol, acquisition settings, and reference. Use the repeat to assess whether the increase persists within measurement uncertainty. |

Pitch sequence follows the standalone implementation and its recorded evidence. [Evidence packets](../src/packet.py) · [Twin update and next measurement](../src/twin.py)
