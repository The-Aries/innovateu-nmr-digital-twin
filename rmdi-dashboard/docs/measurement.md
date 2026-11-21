# Measurement model card

The standalone demonstration estimates the *Residual Metallic Deposition Index* (RMDI) for one simulated sodium-ion cell. An end-of-charge spectrum yields `eoc_metal_area` in `[arb'U].ppm`. For the matched post-discharge spectrum, divide the fitted metallic area by the fitted simulated external ²³Na reference area. The resulting `rmdi` has unit `1`. [Packet fields](../src/packet.py) · [Normalization in `classify`](../src/detect.py)

## Signal and fit

The simulator samples a Gaussian reference and a configurable Gaussian or Lorentzian metal peak on a linear background. The default run uses Gaussian metal peaks. The synthetic schedule sets the signal-to-noise ratio (SNR), noise level, acquisition context and operating conditions. The metallic center and width are informed by Bray et al. Supplementary Table 6. The spectra and the separate truth artifact carry `SIMULATED` origin. [`simulate` and `_generate_document`](../src/sim.py) · [`simulation`](../config.yaml) · [Published basis](../README.md#scientific-reference-points)

`fit_peak` uses bounded nonlinear least squares through SciPy's `curve_fit`. For chemical shift *x* in ppm, it fits height *H*, center μ, width σ, and a local linear background. The default metal and reference windows are 1000–1200 ppm and −40–40 ppm. The code checks for finite, increasing and uniformly spaced points. For simulated zero-filled noise, the independent fit grid comes from every fourth point of the default 2048-point display grid. The simulator applies its FFT to complex white time-domain noise and samples the analytic peak separately. [`fit_peak` and `independent_points`](../src/fit.py) · [`_spectral_noise`](../src/sim.py) · [`fit` and `simulation`](../config.yaml)

```text
I(x) = b₀ + b₁(x − x₀) + H exp[−(x − μ)² / (2σ²)]
A = H σ √(2π)
u(A) = √(gᵀ C g), where g = √(2π) (σ, 0, H, 0, 0)
u(μ) = √C[μ, μ]
```

The area describes the entire fitted line above its baseline. *C* is the full fitted parameter covariance in the order height, center, width, background intercept and background slope. The area calculation includes height–width covariance. A fit failure makes the fitted area and its standard uncertainty unavailable. [`gaussian_area_uncertainty` and `fit_peak`](../src/fit.py)

## Model sensitivity

The fitter reports the absolute area difference from a pseudo-Voigt fit with a shared full width at half maximum. It also reports the largest absolute area shift when the fitted window width changes by ±10%, keeping its center fixed. Broad tails and background can trade off within a finite window. A Lorentzian signal can therefore produce a biased Gaussian area even when its fit SD is small. The two shifts remain separate from fit SD. [`_pseudo_voigt_area` and `fit_peak`](../src/fit.py) · [`fit.window_sensitivity_fraction`](../config.yaml) · [Known-truth checks](../tests/test_fit.py)

In the Lorentzian stress case, the truth was 299.83 a.u.·ppm and the Gaussian estimate was 119.91 ± 5.88 a.u.·ppm. The pseudo-Voigt and window perturbations were 60.57 and 5.19 a.u.·ppm, respectively. Their combined shift was smaller than the roughly 180 a.u.·ppm Gaussian bias. These diagnostics quantify the tested perturbations. Broader shape mismatch can require a different peak model or additional data. [Stress-case test](../tests/test_fit.py) · [Mac mini verification](verification.md)
