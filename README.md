# InnovateU 2026 — NMR Digital Twin

Private project workspace for the NMR Quantum Engineering challenge (20–21 November 2026, KICU Ulm).

## Scope

The challenge asks teams to demonstrate a traceable baseline-to-follow-up update, distinguish physical change from measurement effects, communicate uncertainty, and propose the next measurement. The organizer's [dossier v1.6](materials/organizer/MRI_Local_Spectroscopy_Health_Digital_Twin_Hackathon_Dossier_v1.6.pdf) specifies the deliverables and permits public and synthetic data.

[Project plan and decisions](docs/PROJECT_PLAN.md) maps the four tracks and submission tasks to the Birmingham Figure 5 case.

## Project files

- [Battery Twin Explorer v1.1](battery-twin-explorer-v1.1.html) explores simulated cycles and displays published ²³Na spectra from Bray et al. Figures 6 and 7. Use **Load data** to select `generated_data_set`, `Figure_6`, `Figure_7`, or their shared parent folder.
- Open the [Standalone ²³Na RMDI dashboard online](https://innovateu-sodium-ion-twin.rusticarbor4.chatgpt.site) or use the [offline dashboard](outputs/rmdi-dashboard/rmdi-dashboard.html) with the synthetic replay embedded. For a fresh checkout, see the [build and verification instructions](rmdi-dashboard/README.md).
- The [pitch deck](pitch/Battery-Twin%5FPitch.odp) is stored in OpenDocument Presentation format. The [workflow slides](pitch/Battery-Twin%5FWorkflow.pptx) walk through the six twin steps: Measure, Validate, Trace, Update, Predict and Steer.
- [Organizer materials](materials/organizer/) holds the dossiers, slides and the [StarterPack v0.3](materials/organizer/MRI_Hackathon_DataScience_StarterPack_v0.3/00_START_HERE/README.md). Git ignores the StarterPack's NIfTI example images. Restore them from the organizer's StarterPack archive if needed.
- [Bray et al. (2020)](references/papers/Bray_et_al_2020_Operando_Sodium_Ion_Battery_NMR.pdf) describes the measured study. See the [Birmingham case walkthrough](references/en/birmingham_digital_twin_explained.md) and [background references](references/en/battery_mr_references_en.md).

## Experimental data downloads

Keep downloaded archives and extracted third-party experiment data under `online downloaded data/`. Git ignores that directory. Extract the Figure 6 and Figure 7 archives before loading them in Battery Twin Explorer v1.1.

| Dataset | Official download | Local location |
| --- | --- | --- |
| Birmingham ²³Na time series and electrochemistry (earlier Figure 5 analysis) | [Figure_5.zip](https://edata.bham.ac.uk/456/4/Figure%5F5.zip) | `online downloaded data/Figure_5/` |
| Bray et al. Figure 6 spectra (Explorer v1.1) | [Figure_6.zip](https://edata.bham.ac.uk/456/5/Figure%5F6.zip) | `online downloaded data/Figure_6/` |
| Bray et al. Figure 7 spectra (Explorer v1.1) | [Figure_7.zip](https://edata.bham.ac.uk/456/6/Figure%5F7.zip) | `online downloaded data/Figure_7/` |
| Synthetic Na23 RMDI replay v3; Explorer v1.1 uses `evidence_packets/MAIN/` | [Na23_RMDI_Replay_v3.zip](https://github.com/The-Aries/innovateu-nmr-digital-twin/raw/d143100a6ab5dbd1502b37e15a48d357d2eec33a/Na23%5FRMDI%5FReplay%5Fv3.zip) (Git history, commit `d143100`) | `online downloaded data/Na23_RMDI_Replay_v3/`; packets copied to `online downloaded data/generated_data_set/MAIN/` |
| Measure review: Figures 6–7, Supplementary Figures 3 and 8 | [SupplementaryFigure_3.zip](https://edata.bham.ac.uk/456/14/SupplementaryFigure%5F3.zip), [SupplementaryFigure_8.zip](https://edata.bham.ac.uk/456/10/SupplementaryFigure%5F8.zip), Figures 6–7 as above | `online downloaded data/Bray_2020_Measure_review/` |
| Supplementary information PDF | [41467_2020_15938_MOESM1_ESM.pdf](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-020-15938-x/MediaObjects/41467_2020_15938_MOESM1_ESM.pdf) | `online downloaded data/Bray_2020_SI/` |
| Other Birmingham figure archives (not used) | [Birmingham data record](https://edata.bham.ac.uk/456/) | `online downloaded data/Birmingham_Bray_2020/` |

`online downloaded data/SOURCES.md` repeats this table next to the data.

The [full Birmingham figure guide](references/en/birmingham_bray_2020_data_guide.md) lists each archive and its purpose. The Figure 5 audit exports are under `outputs/birmingham-handoff/` in the preparation workspace.

## Repository updates

Make changes in the local project checkout and verify them locally. Commit and push through Git. For another checkout of the same branch, use `git pull --ff-only origin main` to receive the tracked updates. Download the experimental data separately in each checkout that needs it.

## Local environment

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/check_environment.py
```

## Preparation and on-site notes

The original preparation material is available in [CHALLENGE.md](docs/CHALLENGE.md), [RESEARCH.md](docs/RESEARCH.md), and [QUESTIONS.md](docs/QUESTIONS.md). See [ON_SITE.md](docs/ON_SITE.md) for on-site planning and [DECISIONS.md](docs/DECISIONS.md) for the decision log.

Official brief: https://www.uni-ulm.de/en/io/degree-phd/students/fit4u/community/vernetzung/hackathon/
