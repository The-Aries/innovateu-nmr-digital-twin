# Small, high-value reference set

These are public learning materials, **not** the organizer's dataset.

1. [Oxford FSL-MRS practical](https://pages.fmrib.ox.ac.uk/fslcourse/practicals/fsl_mrs/index.html): illustrates raw-data conversion, spectral preprocessing, model fitting and quality reports. Read the overview first; no need to install the full stack yet.
2. [NiBabel getting started](https://nipy.org/nibabel/gettingstarted.html): load NIfTI and related neuroimaging images in Python **if** the organizer supplies imaging files.
3. [SciPy bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html): confidence intervals when sufficient independent observations and assumptions allow resampling.
4. [FSL-MRS documentation](https://pages.fmrib.ox.ac.uk/fsl/fsl_mrs/): optional specialized spectroscopy toolkit if the actual task requires raw or fitted MRS.

## Minimal scientific concepts

- Observation is not the same as latent true state.
- Random noise, drift/systematic bias, and actual biological/physical changes must not be conflated.
- Two observations do not identify a noise distribution or complex state dynamics on their own.
- Measurement uncertainty should be propagated into the state update and next-measurement recommendation.
- Benchmark against known ground truth *only if* the organizers provide it.

Do not optimize an invented dataset or promise a generic percentage accuracy.
