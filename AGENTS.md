# Working rules

- This repository is the NMR team's preparation workspace, not a completed submission.
- Read README.md, docs/CHALLENGE.md, docs/QUESTIONS.md, and docs/DECISIONS.md first.
- Treat the organizer's dossier and actual dataset as authoritative once provided.
- Do not assume that the data are NIfTI, raw MRS, CSV, images, or previously processed values.
- Keep data, outputs and secrets out of Git. Record provenance and assumptions for all analysis.
- Do not reuse code or proprietary resources from the other challenge without explicit permission.
- Prefer simple, inspectable statistical methods with documented validity over unvalidated ML.
- Do not generate a competition solution before eligibility and pre-work rules are clarified.
- Before the on-site pitch, verify the evidence packet can be regenerated from the official input data.

## Execution hosts

- Coordinate and edit project files on the MacBook Air. Run project tests, data replays, and automation for Measure, Validate, Represent, and Integrate on the Mac mini.
- Connect with `ssh macmini` and use `/Users/aries/Projects/NMR-hackathon` on the Mac mini. Use Interceptor on that host for browser automation. Keep generated artifacts in the Mac mini's ignored `outputs/` directory and copy back the results needed for coordination.
- Before testing local changes, compare the two checkouts and sync the affected files without overwriting edits on the Mac mini. If the Mac mini is unavailable, report the blocker and ask before using the MacBook Air for execution.
