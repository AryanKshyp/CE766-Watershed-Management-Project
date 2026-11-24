# Progress log — CE 766 project (v2: Subarnarekha watershed management)

The v1 log (ML streamflow study, 2026-10-22) is in `archive/v1_ml_streamflow/docs/progress_log.md`.

## 2026-10-27 — Redesign, GR4J, baseline

**Done**
- Archived v1 (ML) in `archive/v1_ml_streamflow/`. Kept `load.py`, `metrics.py`, `test_metrics.py` and `data_notes.md`.
- Chose the study area: the Subarnarekha above Jamshedpur (06008, 12,785 km², with the Kharkai/Adityapur 06001 nested inside it).
- `src/gr4j.py` + tests (water balance closes, recession, non-negative).
- `src/calibrate.py`: 06008 KGE 0.88 calibration / 0.79 validation; 06001 0.85 / 0.52 (+23% bias in validation). Each catchment took ~2.5 min.
- `src/planning.py`: baseline planning table. GR4J over-predicts the 75% dependable yield by 20% (5,488 vs 4,572 MCM).
- `src/figures.py`: Fig 1 (map + validation hydrograph + dependable-yield curve).
- Drafted the preliminary submission (`docs/preliminary_submission.md`) and had it reviewed by a second agent.

**Problems**
- The 06008 gauge is regulated: Jan–May flow jumped in 2017–19 on the main stem only.
- GR4J's x2 ≈ −4.5 mm/day at both gauges, i.e. large exchange losses. Long-term ET is under-estimated against GLEAM, and the exchange term makes up the difference.
- numba and pymoo are not installed. Pure-Python GR4J runs in 0.03 s, which is fine for now.

**Changes from the proposal**
- ML dropped entirely. Conceptual model (GR4J) + XLRM portfolio study. One watershed instead of 31 gauges.

## 2026-11-24 — Final submission

- Checked the previously submitted text and repository. Kept the question, catchment, calibration and validation periods, four levers, and four objectives. Corrected the annual comparison to 35 whole post-warm-up water years and identified the 12 driest monsoons by local rainfall tercile.
- Recomputed the long-term balance on common days and the paired January–May outlet and Kharkai flows. The 2017 and 2018 main-stem increments were about 88 and 50 m³/s. Stored the supporting series in the final tables. Used JREDA design particulars to estimate Chandil inflow by area.
- Implemented ponds, bunds, check dams and a Zhang-based forest response, followed by a daily Chandil storage balance. Short tests cover each lever, combinations, zero works, spill, shortage and mass conservation. The final script also checks the balance over every historical run.
- Documented quantities, cost sources and scenario choices in `docs/assumptions.md`. Enumerated the 16 possible on/off combinations and repeated them with a combined stress case. Choosing fixed pilot sizes makes the set small enough to check exhaustively. This course submission does not claim an optimum over larger designs.
- Produced separate upload figures for the baseline and decision results. Compared modelled river-threshold attainment to observations before interpreting supply or river safety. A second agent drafted all six answer sections using the write-like-aryan skill.

### AI use

Codex helped inspect the existing project, locate sources, implement and test the scenario comparison, generate the figures, and draft the answers. Aryan supplied the assignment requirements and confirmed the preliminary text. His main instructions included “Go through our entire project and do all of the things required in this relevant to the final project submission instructions”, “It's better to do less work than do wrong work”, and “At the end, use another agent using the write like RN skill to write all of the these parts adhering to the word limit.” The writing agent received the verified results, section limits and the instruction to distinguish modelled supply from actual deliveries.
