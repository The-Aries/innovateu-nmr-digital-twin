# Quality control and detection

Acquisition QC and interpretation of peak evidence are separate decisions. Each check records an observed value, unit, threshold, status and owner. The overall QC status is the most severe check result. A finite, low SNR can pass acquisition QC and yield a censored observation. [`assess_qc`](../src/qc.py) · [`classify`](../src/detect.py)

| Check | Rule |
| --- | --- |
| Metadata | Require usable acquisition settings, timing and cell-condition metadata. |
| Comparability | Compare matching stages against their baseline protocol, including sensitivity-related settings and the reference. |
| Fit and SNR | Require successful fit convergence and a finite, nonnegative fitted SNR. SNR is the fitted peak height divided by residual SD. |
| Position | Require a center inside the fit window. At or above fitted SNR 3, require the configured 1050–1115 ppm range. |
| Residual structure | Flag absolute lag-one correlation above 0.4 on the independent native grid. Unavailable residual diagnostics fail this check. |
| Reference | For post-discharge normalization, require a converged positive reference area, positive fit SD and fitted SNR ≥5. |

Sources for the check table are [`assess_qc`](../src/qc.py), [`fit_peak`](../src/fit.py), and [`qc`](../config.yaml).

For a usable fit and acceptable location and residual checks, the candidate rules are `censored` below fitted SNR 3, `uncertain` from 3 to below 5, and `detected` from 5 if the required areas and SDs are positive. A failed QC assessment is `invalid`. Convergence alone is insufficient. Null estimates preserve censored, uncertain and invalid observations. [`classify`](../src/detect.py) · [Packet schema](../schema/evidence_packet_v1.0.schema.json) · [`qc` thresholds](../config.yaml)

## Censoring and calibration

For the simulated Gaussian noise model, the upper-limit calculation fits a unit-area fixed-width Gaussian and a linear baseline at each candidate center on a finite bank. With *n* independent bins and α* the one-sided tail, use the largest bound across templates.

```text
A_UL = max_j [max(0, Â_j) + t_(1−α*, n−3) u_j]
```

For a post-discharge ratio, split the nominal tail between the metal and reference bounds and divide `A_UL` by the positive lower reference bound. The bound is conditional on the configured widths, center bank, background and native-grid noise model. The packet can retain a null bound when that construction is unavailable. [`upper_limit`](../src/detect.py) · [`qc.upper_limit_*`](../config.yaml)

The calibration runs 1,000 trials at each configured input SNR of 0, 3, 5 and 8. It records the rate above each threshold for the full free-center, free-width search before and after the fit-QC checks. Searching over multiple candidate peaks increases the chance of a noise fit crossing a threshold. The table reports observed fractions and Wilson intervals. Upper-limit coverage is reported before the detection decision and separately within bounded censored trials. The thresholds and coverage apply to these simulated inputs. [`run_detection_calibration`](../src/detect.py) · [`qc.calibration_*`](../config.yaml)
