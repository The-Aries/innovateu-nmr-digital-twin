# Battery Magnetic Resonance: Literature and Data Sources

InnovateU Hackathon 2026, NMR Quantum Engineering challenge. Research date: 2026-11-20.

## Contents

- [Summary](#summary)
- [How to use these sources](#how-to-use-these-sources)
- [A. Measurement physics](#a-measurement-physics)
- [B. Fast charging and lithium plating](#b-fast-charging-and-lithium-plating)
- [C. Downloadable data](#c-downloadable-data)
- [D. Key numbers for the measurement model](#d-key-numbers-for-the-measurement-model)
- [E. Verification status](#e-verification-status)

## Summary

- Public raw battery MRI data are almost non-existent. The main MRI papers state that data are "available from the corresponding author upon reasonable request" or give no data statement.
- One public raw ⁷Li NMR dataset is confirmed: Cambridge Apollo, DOI 10.17863/CAM.46593 (CC BY-NC-SA 4.0). Its topic is the SEI–lithium-metal interface, not fast-charge plating.
- Recommended approach: take physical parameters and value ranges from the literature, generate our own synthetic data with a known truth, and use public battery cycling datasets for degradation trends and process noise.
- Do not use any internal BMW or subsidiary data or parameters. The challenge permits only synthetic, public or de-identified data.

## How to use these sources

| Need | Source | Section |
|---|---|---|
| Measurement model: chemical shifts, skin depth, morphology confounder | Benders 2020, Bhattacharyya 2010, Trease/Köster/Grey review | [A](#a-measurement-physics) |
| Alternative observation: field map around the cell (state of charge, defects) | Ilott 2018, Romanenko & Jerschow 2019 | [A](#a-measurement-physics) |
| Fast-charge plating scenario and onset detection | Märker/Xu/Grey, McMaster group, HAL 0 °C study | [B](#b-fast-charging-and-lithium-plating) |
| Realistic ⁷Li noise, linewidth and peak shape | Apollo dataset (Hope et al. 2020) | [C](#c-downloadable-data) |
| Capacity fade trend, prior and process noise Q | Severson 2019, NASA PCoE, CALCE | [C](#c-downloadable-data) |
| Limitation statement for the pitch | RSC Sustainable Energy & Fuels 2025 | [B](#b-fast-charging-and-lithium-plating) |

Label all generated data as `SIMULATED` and record which publication informed each parameter.

## A. Measurement physics

| Reference | What it provides | Data |
|---|---|---|
| Bhattacharyya R, Key B, Chen H, et al. In situ NMR observation of the formation of metallic lithium microstructures in lithium batteries. *Nat Mater* 9:504–510 (2010). [doi:10.1038/nmat2764](https://dx.doi.org/10.1038/nmat2764) | Time-resolved quantitative in situ ⁷Li NMR of metallic lithium. Uses the RF skin depth and bulk magnetic susceptibility to distinguish mossy (high surface area) from dense deposits. | Not found |
| Chandrashekar S, Trease NM, Chang HJ, Du LS, Grey CP, Jerschow A. ⁷Li MRI of Li batteries reveals location of microstructural lithium. *Nat Mater* 11:311–315 (2012). doi:10.1038/nmat3246 ([record](https://ouci.dntb.gov.ua/works/4NoNmwYl)). Dossier reference [41]. | ⁷Li MRI locates lithium microstructures (dendrites) in the cell. | Not found |
| Benders S, Mohammadi M, Klug CA, Jerschow A. Nuclear magnetic resonance spectroscopy of rechargeable pouch cell batteries: beating the skin depth by excitation and detection via the casing. *Sci Rep* 10:13781 (2020). [PMC7426951](https://pmc.ncbi.nlm.nih.gov/articles/PMC7426951/) | ⁷Li NMR of a commercial 600 mAh graphite/NMC pouch cell; the cell casing is used as the RF coil. 9.4 T, 155.5 MHz. Shifts: electrolyte Li ≈ 0 ppm, metallic Li ≈ 260 ppm, graphite-intercalated Li ≈ 30 ppm. | No statement |
| Ilott AJ, Mohammadi M, Schauerman CM, Ganter MJ, Jerschow A. Rechargeable lithium-ion cell state of charge and defect detection by in-situ inside-out magnetic resonance imaging. *Nat Commun* 9:1776 (2018). [PMC5934497](https://pmc.ncbi.nlm.nih.gov/articles/PMC5934497/). Dossier reference [42]. | Inside-out MRI: ¹H MRI of water around the cell maps the susceptibility-induced field, which indicates state of charge and defects. 9.4 T, 400 µm isotropic resolution, field change across the cell 1–2 ppm, resolvable difference about 0.1 ppm. | On request |
| Romanenko K, Jerschow A. Distortion-free inside-out imaging for rapid diagnostics of rechargeable Li-ion cells. *PNAS* 116:18783–18789 (2019). [PMC6754580](https://pmc.ncbi.nlm.nih.gov/articles/PMC6754580/) | SPRITE-based inside-out imaging of commercial cells, including damaged phone batteries. About 1 mm resolution; charging changed the field by up to about 4 ppm. | Not found |
| Trease NM, Köster TKJ, Grey CP. In situ NMR studies of lithium ion batteries. *Electrochem Soc Interface* (Fall 2011). [PDF](https://www.electrochem.org/dl/interface/fal/fal11/fal11_p069-073.pdf) | Skin depth: only about the first 15 µm of lithium metal is excited at 77 MHz. | — |
| Pecher O, Carretero-González J, Griffith KJ, Grey CP. Materials' methods: NMR in battery research. *Chem Mater* 29:213 (2017). doi:10.1021/acs.chemmater.6b03183 ([Apollo](https://www.repository.cam.ac.uk/handle/1810/262008)) | Method review of in situ and ex situ battery NMR. Good entry point for the measurement card. | — |
| Hu Y, Iwata GZ, Mohammadi M, et al. Sensitive magnetometry reveals inhomogeneities in charge storage and weak transient internal currents in Li-ion cells. *PNAS* 117:10667–10672 (2020). [PMC7245122](https://pmc.ncbi.nlm.nih.gov/articles/PMC7245122/) | Not NMR: atomic magnetometers map the field around a pouch cell (local state of charge, internal currents). A possible "next measurement" modality. | OSF (see C) |

## B. Fast charging and lithium plating

- **Märker K, Xu C, Grey CP.** Operando NMR of NMC811/graphite lithium-ion batteries: structure, dynamics, and lithium metal deposition. [Apollo record](https://www.repository.cam.ac.uk/items/f6f318ad-cb57-4fa5-b843-9df7e4ac478e). Operando ⁷Li NMR in full cells, including lithium metal deposition. Closest to the question "is fast charging still safe?".
- **Krachkovskiy et al., *J Electrochem Soc* 2020.** [Record](https://experts.mcmaster.ca/scholarly-works/3593110). In situ monitoring of Li deposition on graphite in a single-layer cell made from harvested commercial EV electrodes; distinguishes a surface film from dendrites.
- **Sanders et al., *Carbon* 2022.** [Record](https://experts.mcmaster.ca/scholarly-works/2159077). Graphite/NMC622 at ≥1C: direct transition to concentrated LixC6 phases and Li accumulation on graphite surfaces, which facilitates plating.
- **Sadighi et al. 2025 (preprint, not peer reviewed).** [ChemRxiv](https://chemrxiv.org/engage/chemrxiv/article-details/6827763050018ac7c58c6726). Operando ⁷Li NMR combined with three-electrode electrochemistry on SiO–graphite anodes during fast charge; estimates the reversible plating fraction.
- **Operando ⁷Li NMR at 0 °C, NMC622/graphite.** [HAL 04272140](https://hal.archives-ouvertes.fr/hal-04272140). Detection of the onset of metastable lithium deposits under fast charge.
- **Post-mortem study of commercial pouch cells, *Sustainable Energy & Fuels* 2025.** [PDF](https://pubs.rsc.org/en/content/articlepdf/2025/se/d5se00509d). ⁷Li NMR + ICP-OES + SEM on graphite–SiOx/NMC cells. States that in situ methods cannot be applied to commercial cells because of their design. Use this for the limitation statement.

## C. Downloadable data

| Dataset | Content | Licence | Use |
|---|---|---|---|
| Apollo, [doi:10.17863/CAM.46593](https://www.repository.cam.ac.uk/handle/1810/304633). Supporting data for Hope et al., *Nat Commun* 11:2224 (2020) | `Li_DNP_NMR_data.zip`, 60.7 MB: ¹H, ⁷Li and ¹⁹F FIDs, spectra and metadata in TopSpin format | CC BY-NC-SA 4.0 | Only confirmed public raw ⁷Li FIDs. Reference for noise, linewidth and peak shape. Topic is DNP/SEI, not fast-charge plating. |
| OSF [cw8zv](https://osf.io/cw8zv/), cited by Hu et al. 2020 | Magnetometry data (field around a pouch cell) | Unknown | Contents not verified; the page needs a browser. |
| Severson KA et al., Data-driven prediction of battery cycle life before capacity degradation. *Nat Energy* 4:383 (2019). [doi:10.1038/s41560-019-0356-8](https://www.doi.org/10.1038/S41560-019-0356-8); data at data.matr.io/1 | 124 LFP/graphite cells, 72 fast-charge protocols, cycle life about 150–2,300 cycles, end of life at 80 % capacity | Public | Capacity fade prior and process noise Q |
| [NASA PCoE repository](https://www.nasa.gov/Intelligent-Systems-Division/Discovery-and-Systems-Health/Pcoe/Pcoe-Data-Set-Repository/) | Li-ion aging at different temperatures; charge, discharge and impedance profiles | Check per dataset | Same as above |
| [CALCE battery data](https://calce.umd.edu/data) | Cycling, storage, OCV and impedance data | Citation required | Same as above |
| [Battery Imaging Library](https://zenodo.org/records/17011440) | X-ray micro-CT of an 18650 cell (not MRI) | Public | Candidate cross-check modality |

## D. Key numbers for the measurement model

| Quantity | Value | Source |
|---|---|---|
| ⁷Li gyromagnetic ratio γ/2π | ≈ 16.55 MHz/T | Standard constant |
| ⁷Li frequency at 2.895 T (StarterPack field) | ≈ 47.9 MHz | Derived: 16.55 × 2.895 |
| Electrolyte / diamagnetic Li shift | ≈ 0 ppm | Benders 2020 |
| Metallic Li shift (Knight shift) | ≈ 260 ppm | Benders 2020 |
| Graphite-intercalated Li shift | ≈ 30 ppm | Benders 2020 |
| RF skin depth in Li metal | ≈ 15 µm at 77 MHz; larger at lower frequency | Trease/Köster/Grey 2011 |
| Susceptibility field change across a cell | 1–2 ppm; about 0.1 ppm resolvable | Ilott 2018 |
| Field change on charging | up to about 4 ppm | Romanenko & Jerschow 2019 |

Main confounder: the metallic Li signal scales with the accessible surface (skin depth), not only with mass. An increase in signal can come from a change in morphology (mossy versus dense lithium) rather than more plated lithium. Other confounders: state of charge and temperature at measurement time, cell orientation relative to B0, and coil tuning.

## E. Verification status

- Read in full or in large part: Benders 2020, Ilott 2018, Romanenko & Jerschow 2019, Hu 2020 (PMC pages), and the Apollo dataset page.
- Not read in full: Bhattacharyya 2010, Chandrashekar 2012, Märker/Xu/Grey and the McMaster papers. Their quantitative methods and values are not confirmed here.
- The Hu 2020 data statement (OSF) comes from a model-extracted summary of the PMC page, not a verbatim reading.
- Download links for NASA and CALCE were not tested.
- Sadighi 2025 is a preprint.
