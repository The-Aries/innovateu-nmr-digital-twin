# MRI + Local Spectroscopy Hackathon — Data Science Starter Pack v0.3

This is **synthetic teaching data**. It contains no real patient information and is not intended for clinical use.

## Why four formats?

- **DICOM**: acquisition/clinical object format. Rich metadata, many tags, one or more instances per series.
- **NIfTI**: compact n-dimensional array plus geometry. Excellent for analysis, but intentionally carries far less acquisition metadata than DICOM.
- **BIDS**: a dataset organisation and metadata convention around standard files such as NIfTI + JSON/TSV sidecars.
- **MRS-BIDS**: the BIDS modality for MR spectroscopy. Spectroscopy source data are represented in **NIfTI-MRS**, which stores complex time-domain data and spectroscopy metadata.

The teaching pipeline is:

`DICOM / NIfTI / NIfTI-MRS -> BIDS / MRS-BIDS -> QC + provenance -> features.csv / evidence packet (packets/*.json) -> Digital Twin update`

## What the Data Science team is expected to learn

Do **not** teach a full database course. Focus on the interface:
1. recognise the source formats and what information each one does or does not carry;
2. transform metadata/features into a small, explicit JSON/CSV data contract;
3. detect missing/invalid values and preserve quality flags;
4. preserve units, time, coordinate references and provenance;
5. hand a validated evidence packet to the Digital Twin layer.

### Data-quality boundary

- **Quantum Engineering** decides what a measurement physically means and which physics-level QC metrics matter.
- **Precision Mechanics / Metrology** provides calibration, traceability, geometry/repeatability and uncertainty.
- **Data Science** checks structure, types, missingness, validity ranges, identifiers, units, metadata, de-identification, lineage and harmonisation. It **flags** questionable data; it does not silently repair or impute evidence.
- **Digital Twins** defines the input contract and acceptance policy required for state updates. It may accept `WARN` evidence with uncertainty, but should reject `FAIL` evidence according to the shared contract.

## Suggested 60–75 minute partner lecture

1. **5 min** — Why data format is part of scientific evidence.
2. **15 min** — DICOM -> NIfTI -> BIDS/MRS-BIDS: what changes, what is retained, what can be lost.
3. **15 min** — JSON and CSV as small interface formats; inspect `05_TwinReady_JSON_CSV/`.
4. **10 min** — Quality flags, missing values, invalid values, units and de-identification.
5. **10 min** — Provenance and lineage; link every feature to source file + processing step.
6. **15–20 min hands-on** — build/modify one `evidence packet (packets/*.json)` from the supplied examples.

## Suggested student assignment

Using the baseline and follow-up examples:
1. inventory the available files and metadata;
2. produce or revise `features.csv`;
3. run a simple validity/missingness check and produce `qc_report.json`;
4. produce one `evidence packet (packets/*.json)` that satisfies `data_contract.json`;
5. state which fields come from Quantum Engineering, Precision Mechanics / Metrology, and Data Science;
6. explain whether the Digital Twin should `update`, `update_with_warning`, or `reject` the packet.

A detailed database schema is **optional**, not required.

## Recommended external tools

- DICOM: pydicom, dcmtk; conversion with dcm2niix.
- NIfTI: nibabel, FSL, AFNI, MRIcroGL.
- BIDS: BIDS Validator and BIDS Starter Kit.
- NIfTI-MRS/MRS-BIDS: spec2nii, FSL-MRS, Osprey.

## Standards used for the examples

- DICOM PS3.3/PS3.5 current 2026 edition: https://dicom.nema.org/medical/dicom/current/output/chtml/
- NIfTI-1: https://nifti.nimh.nih.gov/nifti-1/
- BIDS 1.11.x: https://bids-specification.readthedocs.io/en/stable/
- MRS-BIDS: https://bids-specification.readthedocs.io/en/stable/modality-specific-files/magnetic-resonance-spectroscopy.html
- NIfTI-MRS 0.3: https://wtclarke.github.io/mrs_nifti_standard/

**Production note:** These files are deliberately small and synthetic. Before using real clinical/research data, apply local governance, de-identification, consent and data-protection requirements and validate the dataset with current tools.

## What changed in v0.3 (2026-10-20)

See `CHANGELOG_v0.3.md`. In short: correct chemical-shift positions of the synthetic spectra with a documented convention,
a frontal VOI, consistent DICOM/NIfTI geometry, a T1-weighted protocol that matches the images, reproducible ROI volumes,
session dates six months apart, evidence packets v1.0 with thresholds v1.0, T1w images with T1-weighted contrast and
an unchanged anatomy at follow-up, and MRS noise calibrated on its expected value.

## Spectroscopy convention (NIfTI-MRS files)

- Time-domain model: s(t) = sum_j a_j exp(-pi LW t) exp(+i 2 pi f_j t), with f_j = (delta_j - 4.65 ppm) x nu0 and nu0 = 123.25 MHz.
- Spectrum: fftshift(FFT(s)); frequency f increases with the point index; ppm = 4.65 + f / nu0 (4.65 ppm at the receiver frequency,
  as FSL-MRS uses for 1H). Plot with ppm decreasing to the right.
- Dwell time 0.5 ms (pixdim[4]), 1024 points, spectral width 2000 Hz (16.2 ppm).
- SNR: height of the NAA peak in the real spectrum / SD of the real spectrum between -3.0 and 0.0 ppm (peak height / noise SD).
- Nominal field 3.0 T; the spectrometer frequency gives the actual field 123.25 / 42.577 = 2.895 T. Keep both.
