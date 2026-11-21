# Data Science Partner Lecture and Assignment

## What the lecture should cover — 60–75 minutes

This is **not a general database lecture**. The quantum-engineering students need enough data literacy to make a physical measurement portable, queryable and safe for a downstream digital-twin update.

1. **Why format is part of evidence — 5 min**  
   A number without units, acquisition context, coordinate frame and provenance is not a trustworthy measurement.
2. **DICOM -> NIfTI -> BIDS / MRS-BIDS — 15 min**  
   What each representation is for; what metadata is retained, externalised or can be lost during conversion.
3. **JSON and CSV as interface formats — 15 min**  
   Inspect `data_contract.json`, `features.csv` and `evidence packet (packets/*.json)`.
4. **Data quality — 10 min**  
   Required fields, missing/invalid values, unit checks, identifiers, range checks, de-identification. Preserve `null`/reason rather than inventing values.
5. **Provenance and lineage — 10 min**  
   Link every derived feature to source file(s), processing step, version and quality status.
6. **Hands-on — 15–20 min**  
   Modify the example evidence packet and decide whether the twin should `update`, `update_with_warning` or `reject`.

## Student assignment

Using the baseline and follow-up examples:

1. inventory the available files and metadata;
2. create or revise `features.csv`;
3. perform a small set of missingness/type/unit/range checks and create `qc_report.json`;
4. create one `evidence packet (packets/*.json)` satisfying `data_contract.json`;
5. label the owner of each quality decision: Quantum Engineering, Precision Mechanics / Metrology, Data Science, Digital Twin, or Shared;
6. decide `update`, `update_with_warning`, or `reject` and give a machine-readable reason;
7. demonstrate one provenance trace from twin variable back to source file.

### What is *not* required

- a full relational-database theory course;
- advanced SQL optimisation;
- a production data warehouse;
- a complex ML model;
- silent imputation of missing scientific values.

A simple, explicit and testable contract is preferred over a sophisticated but opaque stack.
