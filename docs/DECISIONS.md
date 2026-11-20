# Decision log

2026-11-20 — Use the authors' saved TopSpin processing number 2 (`pdata/2`) for the Bray et al. (2020) Figure 5 spectra. Do not reprocess the raw FIDs. Reason: the pitch audience does not need processing details, and the team's time goes to the twin update. `pdata/1` is not used for the time series because its processing steps differ between acquisitions (#61 uses a different phase set with automatic baseline; #65 has no phase or baseline correction step). Accepted limitations: the processing parameters are the authors' choices; `pdata/2` uses an automatic 5th-order polynomial baseline (`ABSG = 5`) that may reduce broad metallic and quasi-metallic signals; the paper does not report the full-cell processing parameters. State these limitations in the limitation card.

2026-11-20 — Selected Bray et al. (2020), Birmingham Figure 5, as the measured sodium-ion case under Dossier v1.6. Use the 61 → 63 NMR signal update, retain the provisional status of electrochemistry alignment, and use the organizer's synthetic case as a reference. See [the current project plan](../PROJECT_PLAN.md) for decisions and tasks.

2026-11-14 — Repository is a private preparation workspace. Use official synthetic data only. Keep the scientific solution unimplemented until the hackathon rules and actual dataset are known.

2026-11-14 — Initial working team: one developer/integrator and one teammate with a mathematics background. No third team member assumed.

2026-11-14 — Preferred path is an explainable model with auditable uncertainty, not a large neural network by default.
