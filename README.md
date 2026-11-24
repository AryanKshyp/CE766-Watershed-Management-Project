# Subarnarekha watershed management

This CE 766 project compares farm ponds, trench-cum-bunds, check dams and afforestation upstream of Chandil. It evaluates rabi irrigation, Jamshedpur supply, dry-season river flow and capital cost for [16 portfolios](outputs/tables/final_portfolios.csv). See the [two figures](outputs/final/) and [model assumptions and sources](docs/assumptions.md).

The daily inputs cover the Jamshedpur and Adityapur catchments from 1980 to 2018. Missing discharge stays missing. The processed inputs are drawn from [CAMELS-IND v2.2, Mangukiya et al.](https://zenodo.org/records/14999580).

To reproduce the figures and tables from the repository root:

```sh
python -m src.final_analysis
python -m pytest -q
```

The final analysis uses the checked-in catchment data, daily baseline simulations and fitted parameters. To repeat the earlier calibration, run `python -m src.calibrate` first. This overwrites the baseline calibration tables and simulation with a new run. The final analysis runs directly from the supplied files.
