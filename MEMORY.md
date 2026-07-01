# Project Memory: Trading & Market Sentiment Case Study

## Project Overview & Mission
This project involves analyzing historical trading data and merging it with the Fear & Greed Index to understand market sentiment and its correlation with trading profitability, trade sizes, directions (long vs short), and trader behaviors. The ultimate goal is to produce a professional data science case study with:
1. An interactive Jupyter Notebook (`analysis.ipynb`)
2. A standalone production-quality Python script (`analysis.py`)
3. A comprehensive executive summary report (`report.md`)

## Tech Stack & Versions
- **Language:** Python 3.12+
- **Environment:** virtualenv (`.venv`)
- **Libraries:** pandas, numpy, matplotlib, seaborn, ipykernel, notebook

## Architecture & Core Decisions
- **Merging Strategy:** Convert `Timestamp IST` in historical trading data to `YYYY-MM-DD` date and merge with the `date` column from the Fear & Greed index.
- **Long vs Short Classification:** For trades with realized PnL (`Closed PnL != 0`), classify as `Long` if `Side == 'SELL'` (buying first, then selling to close) and `Short` if `Side == 'BUY'` (selling first, then buying to close).
- **Visualizations:** Professional matplotlib/seaborn plots with consistent color palettes, descriptive titles, and clear styling.

## Progress & Roadmap
- [x] Locate and copy raw datasets (`historical_data.csv` and `fear_greed_index.csv`)
- [x] Initialize Python virtual environment and install packages
- [x] Create implementation plan and obtain user approval
- [x] Draft Python script (`analysis.py`) for data cleaning, merging, analysis, and plotting
- [x] Create Jupyter Notebook (`analysis.ipynb`) with visualizations and markdown observations
- [x] Write executive report (`report.md`) containing insights and recommendations
- [x] Verify execution of notebook and script
- [x] Refine case study tone, add Assumptions, Limitations, and Future Work
- [x] Compute advanced stats (Spearman correlation & standard deviations)
- [x] Create project README.md and re-generate ZIP archive
