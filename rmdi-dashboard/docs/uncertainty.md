# Uncertainty budget

For a detected post-discharge peak, `R = Ametal / Aref`. The packet reports its fit-based standard uncertainty in unit `1`. The numerator and denominator occupy disjoint native bins under the simulator's noise model. The implementation uses this independence to propagate both contributions. [`classify`](../src/detect.py) · [Evidence fields](../src/packet.py)

```text
u(R)² = [u(Ametal)/Aref]² + [R × u(Aref)/Aref]²
```

| Contributor | Treatment |
| --- | --- |
| Metal peak and local background | Compute its random contribution from `metal_area_sd` and `reference_area` in each `area.json` trace. [Fit covariance](../src/fit.py) · [Trace fields](../src/run.py) |
| Reference fit | Includes the reference area's Gaussian fit SD. A failed or weak reference fit blocks the normalized observation. [`classify`](../src/detect.py) · [`assess_qc`](../src/qc.py) |
| Line shape and fitted window | The sum of the two absolute shifts gives each fitted area's perturbation. For RMDI the packet builder propagates these through the extremes of the numerator and denominator. The largest resulting ratio shift is stored as `model_sensitivity` when the perturbed reference stays positive and all shifts are available. The comparison adds the two cycles' sensitivities as a separate guard. [`model_sensitivity`](../src/packet.py) · [`_assess_change`](../src/twin.py) |
| Time, protocol and shared instrument effects | The simulated protocol is explicit, and the QC gate checks comparability. A real repeated-measurement study is needed to estimate drift, reference coupling and run-to-run reproducibility. [`trajectory_protocol_and_noise`](../config.yaml) · [`COMPARABILITY_KEYS`](../src/qc.py) |

At cycle 12 of the verified run, the metallic area was 391.65 ± 12.90 a.u.·ppm and the reference was 249.69 ± 0.81 a.u.·ppm. They contributed about 0.05165 and 0.00506 respectively to the RMDI fit SD of 0.05189. Thus the metal fit dominates random uncertainty at that cycle. The separate 0.08107 ratio model perturbation is larger than the fit SD. [Trace fields](../src/run.py) · [Mac mini verification](verification.md)

An improvement for a physical experiment is to acquire independent, matched post-discharge repeats at a fixed delay, with a stable external reference, to estimate repeatability and shared drift. In the strong isolated Gaussian coverage check, 1,000 trials per noise case yielded 69.6% and 94.6% coverage for the nominal 68% and 95% intervals with independent noise. With the zero-filled native grid, coverage was 64.9% and 93.9%. Both cases completed without fit failure. Detection calibration evaluates near-threshold behavior separately. [Coverage test](../tests/test_fit.py) · [`run_detection_calibration`](../src/detect.py) · [`measurement_delay_s`](../config.yaml) · [Mac mini verification](verification.md)
