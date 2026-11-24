Data: CAMELS-IND v2.2 (Mangukiya et al., 2025, Earth System Science Data 17, 461–491), Zenodo: https://zenodo.org/records/14999580.

## CE 766 final project

The [final answers](docs/final_submission.md) compare farm ponds, trench-cum-bunds, check dams and afforestation upstream of Chandil. The [Word document and two numbered upload figures](outputs/final/) accompany the answers. All 16 portfolios and both sets of assumptions appear in the [results table](outputs/tables/final_portfolios.csv). The [assumptions and sources](docs/assumptions.md) explain the operating rule and the limits of the downstream comparison.

From the repository root, with Python, NumPy, pandas, SciPy, PyArrow and Matplotlib installed, run:

```sh
python -m src.final_analysis
python -m pytest -q
```

The final analysis uses the checked-in catchment data, daily baseline simulations and fitted parameters. To repeat the earlier calibration, run `python -m src.calibrate` first. This overwrites the baseline calibration tables and simulation with a new run. The final analysis runs directly from the supplied files.
