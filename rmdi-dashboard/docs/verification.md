# M1–M4 verification

The Mac mini run used [configuration 0.2.0](../config.yaml), with 12 simulated cycles of one sodium-ion cell and two spectra per cycle. The full suite passed **41 tests**. The standalone and organizer schemas accepted all 24 emitted evidence packets. [Test log](../../outputs/standalone-na23-rmdi-verified-20261121/gate-results.txt) · [Run manifest](../../outputs/standalone-na23-rmdi-verified-20261121/manifest.json)

## M1 · Known-truth measurement coverage

Each case used 1,000 trials of a strong isolated Gaussian signal at nominal input SNR 40. Both cases had zero fit failures.

| Noise case | Nominal 68% | Nominal 95% |
| --- | ---: | ---: |
| Independent spectral bins | 69.6% | 94.6% |
| Zero-filled simulation, fitted on native bins | 64.9% | 93.9% |

The nominal Monte Carlo standard errors were 1.48 and 0.69 percentage points. The two cases passed the configured test criterion of three sampling standard errors from target. The zero-filled case yielded lower observed coverage at both levels. These checks characterize the strong Gaussian simulation. At low SNR or with another line shape, the fit and reported SD can behave differently. [M1 tests](../tests/test_fit.py) · [Test log](../../outputs/standalone-na23-rmdi-verified-20261121/gate-results.txt)

In the Lorentzian stress case, the simulated true area was 299.83 a.u.·ppm and the Gaussian fit returned 119.91 ± 5.88 a.u.·ppm. The Gaussian–pseudo-Voigt area difference was 60.57 a.u.·ppm and the largest window shift was 5.19 a.u.·ppm. Neither the fit SD nor these local perturbations accounted for the full observed bias. [Measurement model](measurement.md)

## M2 · Detection and upper limits

Each input SNR used 1,000 trials. Fractions are given as percentages. The SNR 0 row describes false positives. The remaining rows describe detections at the specified fitted-SNR threshold.

| Injected SNR | Raw ≥3 | With QC ≥3 | Raw ≥5 | With QC ≥5 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 26.1% | 0.2% | 13.4% | 0.0% |
| 3 | 59.2% | 34.2% | 25.9% | 9.3% |
| 5 | 99.7% | 74.5% | 60.3% | 39.2% |
| 8 | 100.0% | 84.7% | 99.8% | 84.5% |

The free center and width let the fitter search for apparent peaks in noise. The QC-filtered result at threshold 5 was 0 false positives in 1,000 trials, with a 95% Wilson upper endpoint of 0.38%. This threshold also missed many weak injected peaks. The conditional upper-limit method covered 400 of 402 bounded censored observations at input SNR 3 and 3 of 3 at input SNR 5. The latter count is too small to characterize coverage there. These are simulation results for the configured search and noise model. [QC rationale](qc.md) · [Calibration output with Wilson intervals](../../outputs/standalone-na23-rmdi-verified-20261121/detection.json)

## M3–M4 · Gated state, regression and provenance

| Synthetic observation | Verified behavior |
| --- | --- |
| Cycle 1 | Censored. RMDI remains null, with upper limit 0.0488. |
| Cycle 2 | First accepted quantitative RMDI, 0.164. |
| Cycle 6 | Uncertain. The audit preserves the qualified observation without a new quantitative estimate. |
| Cycle 8 | Rejected on acquisition QC. Accepted state remains intact. |
| Cycle 12 | RMDI 1.569 ± 0.052 fit SD. The increase from cycle 11 was 0.410. It exceeded the combined guard of 0.309, so the twin issued an accumulation warning. |
| Cycle 13 | Forecast 1.734 with a nominal 95% prediction interval of 1.084 to 2.384. The next-evidence recommendation is a matched post-discharge repeat with checks on reference stability and fit residuals. |

The audit retains each forecast before its target arrives, checks subsequent eligible observations, and records updated and rejected decisions. The verifier checked all 24 source-to-packet-to-state chains and found zero matches in the unsupported-claim scan of generated text. Tests also covered wrong units, missing provenance, a tampered fit artifact, and a censored value incorrectly set to zero. [Persistent twin and event log](../../outputs/standalone-na23-rmdi-verified-20261121/twin.json) · [Cycle 12 packet](../../outputs/standalone-na23-rmdi-verified-20261121/packets/E-t12-rmdi.json) · [Regression tests](../tests/test_regression.py)
