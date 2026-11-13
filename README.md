# InnovateU 2026 — NMR Digital Twin

Private **preparation workspace** for the NMR Quantum Engineering challenge (20–21 November 2026, KICU Ulm).

## Scope

The official task is to build a digital-twin prototype from a baseline and follow-up synthetic MRI/MRS session, distinguish credible change from measurement effects, communicate uncertainty, and recommend the next measurement. Final deliverables are a working prototype, a machine-readable evidence packet, and a five-minute pitch.

**Status:** Preparation only. We have not received the official challenge dossier, synthetic data, measurement-error assumptions, or judging rubric. Do not invent them or treat unrelated public examples as competition data. Whether work started before the event can be submitted is unconfirmed.

## Before the event

- Read [challenge facts](docs/CHALLENGE.md), [scientific references](docs/RESEARCH.md), and [open questions](docs/QUESTIONS.md).
- Confirm event rules for pre-built code and participating in two teams.
- Check the Python scientific stack on the laptop; this is a generic environment check, not a competition solution.
- Attend the MRI/MRS lecture on 20 November, 10:00–13:00 (venue of lecture to confirm).

## Local environment

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/check_environment.py
```

No data, model or application is included yet. Once the organizers release the data, choose processing tools based on actual format instead of installing FSL-MRS or deep learning frameworks prematurely.

## On-site entry point

Read [ON_SITE.md](docs/ON_SITE.md) and record decisions in [DECISIONS.md](docs/DECISIONS.md).

Official brief: https://www.uni-ulm.de/en/io/degree-phd/students/fit4u/community/vernetzung/hackathon/
