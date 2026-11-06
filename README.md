# Football Diplomacy (SE333 AI for Sports)
Do geopolitics predict football talent flows and international friendlies? Country-pair x year panel, 1994-2021.

Data (not in repo; see dataset/README_data_sources.md locally): Transfermarkt (dcaribou), martj42 international_results, CEPII Gravity V202211, GML MID 2.2.1.

Run order (from CODE FILES/):
1. python fd_features.py   -> dataset/processed/model_T*.parquet
2. python fd_models.py     -> results/master_results.csv
3. python fd_explain.py    -> reports/figures/final/
