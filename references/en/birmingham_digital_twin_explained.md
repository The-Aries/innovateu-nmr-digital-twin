# A battery digital twin from Birmingham NMR data

A practical guide to using Bray et al.'s sodium-ion full-cell data for the NMR Hackathon. [中文版本](../zh/birmingham%5Fdigital%5Ftwin%5Fexplained%5Fzh.html) · [Archive catalogue and file guide](birmingham%5Fbray%5F2020%5Fdata%5Fguide.html)

## Quick answers

| Question | Short answer |
|---|---|
| What are the data useful for? | Replay a real formation cycle and relate the electrical response to observed changes in the chemical environment of sodium. |
| What kind of twin can we build? | An offline state twin of one sodium-ion full cell during its first formation cycle. It updates a relative metallic-sodium signal when a spectrum becomes available. |
| How do we build it? | Combine current and voltage with time-windowed NMR observations. Extract spectral features, check their quality, update the state and record the evidence behind each update. |
| What can we predict? | Test a five-minute terminal-voltage forecast on the recorded cycle. A forecast of the next spectrum's signal is exploratory. Reliable onset, lifetime and cross-cell forecasts need additional measurements. |
| Do we need all the archives? | Figure 5 is sufficient for the core prototype. Figure 6, Figure 7 and selected supplementary archives answer specific follow-up questions. |

[What the measurements tell us](#section-1) · [How to build the twin](#section-2) · [How to forecast and check the result](#section-3) · [Which archives should enter the model?](#section-4)

## 1. What the measurements tell us

Figure 5 follows one full cell through formation at 30 mA/g. It contains **99,841 electrochemical samples** and **16 operando ²³Na spectra**. Terminal voltage and current describe the electrical response. NMR adds evidence about the chemical environments of sodium. The authors report an early-charge metallic-sodium peak near 1050 ppm that shifted toward 1115 ppm before falling below detection. [Bray et al. (2020), Figures 5–6 and Methods](https://doi.org/10.1038/s41467-020-15938-x)

Acquisition numbers 60–75 label NMR observations of the same cell. Each spectrum integrates signal over about 30 minutes, with roughly five minutes between acquisition windows. The instrument logs give UTC start and end times. The electrochemical file gives elapsed time, and the offset between the two clocks remains tentative. Retain each NMR window and the assumed offset when associating a spectrum with voltage, current or accumulated charge.

## 2. How to build the twin

| Component | Implementation |
|---|---|
| Inputs | Current, terminal voltage, raw or processed ²³Na data, and NMR acquisition logs. |
| State | Track net charge passed through the terminals from a defined reference time, plus a relative metallic-sodium signal. Obtain net charge by integrating current. Conversion to state of charge requires an initial condition and capacity calibration. |
| Observation model | Scale the processed spectrum, estimate a local background, and integrate the signed signal over 1020–1150 ppm. Save the peak position, detection status and the signal's sensitivity to processing choices. |
| State update | Use comparable spectra that pass the quality checks. Record warnings and the review decision. Keep unresolved observations visible, including the time of the last reliable observation. |
| Evidence record | Save acquisition ID, UTC window, assumed offset, processing version, quality checks, source paths and states before and after the update. |

### A real update in the Explorer

The current Explorer compares acquisition **61** with **63**. Using its processing number 2 and the same integration rule, the result can be reproduced from the supplied Bruker files. [Birmingham Explorer](../../MRI%5FData%5FExplorer%5FBirmingham.html)

| Acquisition | Signed area (×10⁶ a.u.·ppm) | Method sensitivity allowance (×10⁶ a.u.·ppm) | Detection |
|---|---:|---:|---|
| 61 | −3.96 | 5.85 | Unresolved |
| 63 | 8.51 | 4.07 | Detected by the Explorer's rule |

The increase is **12.47 × 10⁶ a.u.·ppm**, above the combined allowance of **9.92 × 10⁶ a.u.·ppm**. The Explorer flags the unresolved baseline and the difference in stored phase, so the update carries a warning and requires explicit acceptance. The negative baseline is the signed result after background correction. The allowance is a method-sensitivity measure, so statistical coverage would require separate calibration. The current state takes the latest accepted observation. Forecasting would add a separate rule for how that state evolves before a measurement arrives. [Hackathon Dossier v1.6, §8.5, §9.7 and Appendix J.6](../../MRI%5FLocal%5FSpectroscopy%5FHealth%5FDigital%5FTwin%5FHackathon%5FDossier%5Fv1.6.pdf)

## 3. How to forecast and check the result

1. **Choose a target and a horizon.** Forecast terminal voltage five minutes ahead, or forecast the relative signal in the next NMR acquisition window. If the forecast depends on future current, use the scheduled current or state the assumed current profile.
2. **Start with a baseline.** Use the latest observed voltage or spectral estimate as a persistence forecast. For voltage, compare it with a local trend extrapolation. For NMR, compare more elaborate models against persistence and keep detection status separate from the signed area.
3. **Run the test in time order.** At each forecast origin, use only observations already available. An NMR spectrum becomes available at the end of acquisition or later if processing takes time. Save the forecast before inspecting the target. Examine startup and current transitions separately, and use whole held-out cells for cross-cell claims.

### What the voltage test showed

The test used **98 forecast origins**, spaced five minutes apart from 300 s to 29,400 s on the electrochemical clock. The predictors used the latest recorded voltage at or before each required input time. Targets were evaluated five minutes after each origin, with interpolation used only for scoring when needed. The local trend multiplied the preceding 60-second voltage change by five and added it to the latest voltage. [Figure 5 source data](https://edata.bham.ac.uk/456/4/Figure%5F5.zip)

| Five-minute predictor | Mean absolute error | Median absolute error | Largest absolute error |
|---|---:|---:|---:|
| Keep the latest voltage | 17.7 mV | 13.0 mV | 173.9 mV |
| Extrapolate the recent 60-second trend | 13.8 mV | 1.2 mV | 1,165.9 mV |

The trend had a lower average error and a much larger startup miss. At the first origin (300 s), it predicted **3.193 V** at 600 s, where the recorded voltage was **2.027 V**. This test supports comparing short-horizon baselines and examining errors by operating phase. It covers a single trace. Its 98 origins share the same physical experiment. Voltage scoring uses the electrochemical clock, so this test does not validate the NMR time offset.

### What is predictable with the current evidence?

| Target | Evidence and remaining work |
|---|---|
| Terminal voltage in a few minutes | Supports within-cycle backtesting. Other cells, temperatures and current programs need separate validation. |
| Relative metallic-sodium area or detection in the next spectrum | Supports an exploratory one-window forecast. A single sequence of 16 spectra offers limited evidence about the first detectable peak or its probability. |
| Absolute deposited sodium or its location | Absolute mass needs a calibration that accounts for the measurement response. Spatial claims require aligned imaging of the relevant cell. |
| State of charge, state of health, lifetime or failure risk | State of charge needs a reference and usable-capacity calibration. Aging and failure forecasts need multi-cell, long-term cycling and the relevant outcome labels. |

## 4. Which archives should enter the model?

| Project objective | Use |
|---|---|
| Core state update and short-horizon voltage test | **Figure 5** only. It already contains the paired electrochemical and NMR series required for this prototype. |
| Pristine reference or peak interpretation | Figure 6 adds pristine acquisition 10. Acquisitions 63 and 67 are already in Figure 5. Supplementary Figure 8 reuses 63–65 and helps inspect early peak shapes. |
| Comparison under a different operating condition | Figure 7 and Supplementary Figure 3 provide spectra and electrochemistry for the 86 mA/g condition in a different full cell. Treat the three spectra as a sparse comparison. The 30 mA/g record in Supplementary Figure 3 duplicates Figure 5. |
| Spatial imaging or measurement physics | Figures 1–4 and the relevant supplements allow separate studies of sodium-metal cells, including plating morphology. Supplementary Table 1 provides relaxation experiments for measurement modelling. |
| Robust prediction across cells or protocols | Collect repeated, time-synchronised current, voltage and NMR records from independent full cells under comparable and varied conditions. Keep entire cells separate for evaluation. |

[University of Birmingham data record](https://edata.bham.ac.uk/456/) · [Original paper and supplementary information](https://doi.org/10.1038/s41467-020-15938-x) · [Download folder](../../online%20downloaded%20data/Birmingham%5FBray%5F2020/)
