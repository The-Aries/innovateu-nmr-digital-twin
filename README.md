# InnovateU 2026 — NMR Digital Twin

Private project workspace for the NMR Quantum Engineering challenge (20–21 November 2026, KICU Ulm).

## Scope

The challenge asks teams to demonstrate a traceable baseline-to-follow-up update, distinguish physical change from measurement effects, communicate uncertainty, and propose the next measurement. The organizer's [dossier v1.6](MRI_Local_Spectroscopy_Health_Digital_Twin_Hackathon_Dossier_v1.6.pdf) specifies the deliverables and permits public and synthetic data.

[Project plan and decisions](PROJECT_PLAN.md) maps the four tracks and submission tasks to the Birmingham Figure 5 case.

## Offline documents

Open [README.html](README.html) in a browser after cloning or downloading the repository. Each Markdown document has a companion HTML file in the same folder. Use [the project plan in HTML](PROJECT_PLAN.html) or the [Chinese materials index](translations/zh/index.html) for reading. The bundled [document viewer](assets/document-viewer/viewer.js) and [stylesheet](assets/document-viewer/viewer.css) supply the contents and document switcher offline.

## Project files

- [Birmingham Explorer](MRI_Data_Explorer_Birmingham.html) follows the measured ²³Na series and the corresponding electrochemical record for the main case. The cross-device time offset is provisional.
- [Bruker Explorer](MRI_Data_Explorer_Bruker.html) reads and compares TopSpin spectra. The Cambridge lithium-metal dataset provides the microwave on/off comparison.
- [Organizer's MRI Data Explorer](MRI_Data_Explorer_v1.0-rc5.html) opens the synthetic MRI/MRS teaching case.
- [Chinese materials index](translations/zh/index.html) links the translations to the organizer's original documents.
- [Organizer's StarterPack archive](MRI_Hackathon_DataScience_StarterPack_v0.3.zip) contains the full synthetic teaching package. Extract it to restore the MRI and MRS example files alongside those already in the StarterPack directory.
- [Bray et al. (2020)](references/papers/Bray_et_al_2020_Operando_Sodium_Ion_Battery_NMR.pdf) is the paper for the main case. See the [Birmingham case walkthrough](references/zh/birmingham_digital_twin_explained_zh.md) and [background references](references/zh/battery_mr_references_zh.md).

## Experimental data downloads

Keep downloaded archives and extracted third-party experiment data under `online downloaded data/`. Git ignores that directory. Open the Explorer HTML in a local browser and select the corresponding extracted directory.

| Dataset | Official download | Local location |
| --- | --- | --- |
| Birmingham ²³Na time series and electrochemistry (main case) | [Figure_5.zip](https://edata.bham.ac.uk/456/4/Figure_5.zip) | `online downloaded data/Figure_5/`, with `Na_fullSpectrum_60` through `Na_fullSpectrum_75` and the electrochemical text file directly inside |
| Cambridge lithium DNP NMR | [Li_DNP_NMR_data.zip](https://api.repository.cam.ac.uk/server/api/core/bitstreams/d7f35bc2-9740-4107-a4de-5cef29ead191/content) | `online downloaded data/open_data/`, containing `sample_A` through `sample_G` and `Misc` |
| Birmingham published comparison (optional reference) | [Figure_6.zip](https://edata.bham.ac.uk/456/5/Figure_6.zip) and [Supplementary Figure 8](https://edata.bham.ac.uk/456/10/SupplementaryFigure_8.zip) | `online downloaded data/Birmingham_Bray_2020/` |

Figure 5 alone is sufficient to replay the Birmingham Explorer. Download other files as needed using the [full Birmingham figure guide](references/en/birmingham_bray_2020_data_guide.md), the [Birmingham data record](https://edata.bham.ac.uk/456/) or the [Cambridge Apollo data record](https://www.repository.cam.ac.uk/items/a5ed5aab-5881-4e09-bcc1-89cb03df66e9).

## Repository updates

Make changes in the local project checkout, regenerate any affected companion HTML, and verify the changes locally. Commit and push through Git. For another checkout of the same branch, use `git pull --ff-only origin main` to receive the tracked updates. Download the experimental data separately in each checkout that needs it.

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
