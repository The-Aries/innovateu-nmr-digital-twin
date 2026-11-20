# Birmingham sodium-ion battery NMR data guide

Bray et al., *Nature Communications* 11, 2083 (2020). This guide describes the 17 archives published by the University of Birmingham and explains how to use Figure 5 for a data-driven battery digital-twin prototype. [Birmingham data record](https://edata.bham.ac.uk/456/) · [Original paper](https://doi.org/10.1038/s41467-020-15938-x)

## Contents

- [Why start with Figure 5?](#why-start-with-figure-5)
- [Archive catalogue](#archive-catalogue)
- [Inside the Figure 5 archive](#inside-the-figure-5-archive)
- [What the digital twin can demonstrate](#what-the-digital-twin-can-demonstrate)

## Why start with Figure 5?

Figure 5 combines **16 operando ²³Na NMR acquisitions** with **99,841 electrochemical samples** from the same sodium-ion full cell during its first formation cycle at 30 mA/g. The archive contains the raw NMR signals, processed spectra, acquisition logs and the electrochemical time series. This combination lets the prototype replay a real experiment and update an estimate when a new spectrum becomes available. [Original paper, Figure 5 and Methods](https://doi.org/10.1038/s41467-020-15938-x) · [Figure 5 archive](https://edata.bham.ac.uk/456/4/Figure%5F5.zip)

**60–75 are Bruker TopSpin experiment numbers (`EXPNO`).** Each number identifies one spectrum acquisition on the same full cell. For example, the audit logs identify the original instrument paths as `c_20_2/60` and `c_20_2/61`. The repository does not explain why this export begins at 60. Each acquisition window lasts about 30 minutes. Numbers are identifiers. Use audit timestamps for timing. [Bruker TopSpin processing reference](https://nmr.chem.ucsb.edu/docs/Bruker_NMR_Manuals/processing-reference_v007.pdf)

| Acquisition | UTC start, 20 November 2019 | UTC end, 20 November 2019 |
|---|---|---|
| 60 | 19:23:08 | 19:52:47 |
| 61 | 19:57:47 | 20:27:20 |

The audit log provides absolute UTC times for NMR. The electrochemical file stores elapsed time. Its zero point has only a tentative alignment to the NMR clock. Use the full NMR acquisition window when relating a spectrum to the electrochemical trace. Exact event timing depends on the clock offset and the duration of the acquisition.

## Archive catalogue

The repository groups archives by paper figure or supplementary item. The descriptions below combine the ZIP directory listings with the published figure captions. [Birmingham data record](https://edata.bham.ac.uk/456/) · [Original paper, Figures 1–7](https://doi.org/10.1038/s41467-020-15938-x) · [Supplementary information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-15938-x/MediaObjects/41467_2020_15938_MOESM1_ESM.pdf)

### Main figures

| Archive | Contents and purpose |
|---|---|
| [Figure_1.zip](https://edata.bham.ac.uk/456/1/Figure%5F1.zip) | Pristine sodium-metal cell. ²³Na spectra, 2D MRI and 1D spatial profiles for metallic and electrolyte sodium. |
| [Figure_2.zip](https://edata.bham.ac.uk/456/2/Figure%5F2.zip) | Sodium-metal cell after a single cycle. ²³Na spectra, 2D MRI and 1D spatial profiles. |
| [Figure_3.zip](https://edata.bham.ac.uk/456/16/Figure%5F3.zip) | Two stages of galvanostatic plating in a sodium-metal cell. ²³Na spectra, 2D MRI and 1D spatial profiles at the 150 and 600 mA/g stages. |
| [Figure_4.zip](https://edata.bham.ac.uk/456/3/Figure%5F4.zip) | 3D ¹H MRI before and after plating. Includes raw acquisition files and `2dseq` reconstructions. Changes in electrolyte signal reveal where deposits occupy space. |
| [Figure_5.zip](https://edata.bham.ac.uk/456/4/Figure%5F5.zip) | Operando formation-cycle series. Contains acquisitions 60–75 and the matching electrochemical record. |
| [Figure_6.zip](https://edata.bham.ac.uk/456/5/Figure%5F6.zip) | Three selected ²³Na spectra. Acquisition 10 supplies the pristine baseline. The audit logs match acquisitions 63 and 67 to Figure 5. The paper shows peak fits for these spectra. |
| [Figure_7.zip](https://edata.bham.ac.uk/456/6/Figure%5F7.zip) | Three in situ ²³Na spectra from a different full cell at 86 mA/g. Measurements were taken immediately after charging to 4.18 V, four hours later, and after discharge. |

### Supplementary figures and table

| Archive | Contents and purpose |
|---|---|
| [SupplementaryFigure_2.zip](https://edata.bham.ac.uk/456/15/SupplementaryFigure%5F2.zip) | Two electrochemical text files for a sodium-metal cell. The first cycle was run at 30 mA/g outside the magnet and the second at 20 mA/g inside it. |
| [SupplementaryFigure_3.zip](https://edata.bham.ac.uk/456/14/SupplementaryFigure%5F3.zip) | Two full-cell electrochemical records. The 30 mA/g record is identical to the one in Figure 5. The 86 mA/g record corresponds to Figure 7. |
| [SupplementaryFigure_4.zip](https://edata.bham.ac.uk/456/13/SupplementaryFigure%5F4.zip) | Two ²³Na acquisitions used to compare fitted peaks in the solvated-sodium region before and after cycling. |
| [SupplementaryFigure_5.zip](https://edata.bham.ac.uk/456/17/SupplementaryFigure%5F5.zip) | The sodium-metal cell's second cycle. Includes electrochemistry and ²³Na spectra, 2D MRI and 1D profiles before, during and after cycling. |
| [SupplementaryFigure_6.zip](https://edata.bham.ac.uk/456/12/SupplementaryFigure%5F6.zip) | Two electrolyte-sodium spectra used for peak fitting at the start of and after continued plating. |
| [SupplementaryFigure_7.zip](https://edata.bham.ac.uk/456/11/SupplementaryFigure%5F7.zip) | Two metallic-sodium spectra used for peak fitting at the start of and after continued plating. |
| [SupplementaryFigure_8.zip](https://edata.bham.ac.uk/456/10/SupplementaryFigure%5F8.zip) | Three early-charge acquisitions highlighting the metallic-sodium region. The audit logs match Figure 5 acquisitions 63–65. The nominal hours in the folder names differ from those in the supplementary caption. |
| [SupplementaryFigure_9.zip](https://edata.bham.ac.uk/456/9/SupplementaryFigure%5F9.zip) | Hard-carbon electrochemical performance data for the first two cycles and tests at different current densities. Contains an Excel workbook and an Origin project. |
| [SupplementaryFigure_10.zip](https://edata.bham.ac.uk/456/8/SupplementaryFigure%5F10.zip) | Three `.mpr` electrochemistry files for the hard-carbon anode half-cell, cathode half-cell and full cell. |
| [SupplementaryTable_1.zip](https://edata.bham.ac.uk/456/7/SupplementaryTable%5F1.zip) | Four Bruker experiments used to measure T₁ and T₂ relaxation of metallic sodium and dissolved sodium in the separator. |

## Inside the Figure 5 archive

The archive contains 498 files after excluding macOS metadata. One file holds the electrochemical series. The other 497 files are distributed among the 16 `Na_fullSpectrum_*` folders. Each folder contains one acquisition and two processed versions under `pdata/1` and `pdata/2`. [Figure 5 archive](https://edata.bham.ac.uk/456/4/Figure%5F5.zip) · [Bruker TopSpin processing reference](https://nmr.chem.ucsb.edu/docs/Bruker_NMR_Manuals/processing-reference_v007.pdf)

| File or group | Role |
|---|---|
| `Electrochemistry_30mAhg-1.txt_1` | Headerless text. The columns are interpreted as elapsed time (s), current (A) and terminal voltage (V) from the numeric scales and published electrochemical curve. |
| `fid` | Raw time-domain NMR signal. |
| `acqu`, `acqus` | Acquisition settings and the recorded acquisition parameters. Use `acqus` to confirm the parameters used for the acquisition. |
| `audita.txt` | Acquisition audit trail with UTC start and end times and the instrument path. |
| `pulseprogram`, `fq1list` | Pulse sequence and frequency list. The archive includes the frequency list in acquisition 60. |
| `format.temp`, `preemp_default_T121292_00024`, `scon2`, `shimvalues`, `specpar`, `uxnmr.info`, `uxnmr.par` | Supporting files for the parameter display, probe and instrument configuration, and shim settings. |
| `pdata/1/1r`, `pdata/1/1i`, `pdata/2/1r`, `pdata/2/1i` | Real and imaginary parts of the two processed spectra. The Birmingham Explorer uses processing number 2. |
| `proc`, `procs`, `auditp.txt`, `base_info`, `outd`, `assocs` | Within the processing folders, these files store processing settings and status, processing history, and supporting information for display and linked datasets. |
| `title`, `thumb.png`, `parm.txt` | Within the processing folders, these are the title, thumbnail and readable parameter export. The archive includes `parm.txt` for both processed versions of acquisition 62. |

## What the digital twin can demonstrate

1. **Replay the external measurements.** Use the current and terminal voltage to follow the cell through formation.
2. **Update the internal state estimate.** When a spectrum becomes available, extract the relative area, peak position and detection status in the metallic-sodium region. Update the estimate when the spectral quality checks support it.
3. **Make the update traceable.** Record the acquisition ID, UTC window, processing version, spectral uncertainty and assumed clock offset with each update.

The paper reports that a metallic-sodium peak appeared near 1050 ppm during early charging, shifted toward 1115 ppm and then fell below detection. This feature gives the prototype a physical observation to check against. Figure 6 adds the pristine reference, and Figure 7 provides a comparison under a different charging condition. [Original paper, Figures 5–7](https://doi.org/10.1038/s41467-020-15938-x)

Figure 5 supports **offline replay and measurement-driven state updates for one cell and one cycle**. The spectrum provides a relative metallic-sodium signal. Absolute sodium mass requires a separate calibration, spatial morphology requires imaging, and prediction across cells requires independent validation.
