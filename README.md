# Trading Performance and Market Sentiment Case Study

## Project Overview
This repository contains a professional data science case study that analyzes historical trading activity and merges it with the daily Fear & Greed Index to evaluate how market sentiment correlates with trading profitability, volumes, styles (long vs. short), trade sizes, and trader behaviors. 

## Objective
The primary objective of this project is to perform an Exploratory Data Analysis (EDA) and run rigorous statistical correlation tests on a matched dataset of historical trading logs and market sentiment scores, producing a refined, production-grade analysis suitable for investment and risk management review.

## Dataset Description
1. **`historical_data.csv`:** Contains 211,224 raw transaction records with parameters: Account, Coin, Execution Price, Size Tokens, Size USD, Side (BUY/SELL), Timestamp IST, Start Position, Direction (e.g., Open/Close Long/Short), Closed PnL, Transaction Hash, Order ID, Crossed, Fee, and Trade ID.
2. **`fear_greed_index.csv`:** Contains 2,644 daily records tracking market sentiment with fields: timestamp, value (0-100), classification (Extreme Fear, Fear, Neutral, Greed, Extreme Greed), and date (YYYY-MM-DD).

## Technologies Used
- **Language:** Python 3.12+
- **Data Manipulation:** pandas, numpy
- **Visualizations:** matplotlib, seaborn
- **Execution & Reporting:** Jupyter Notebook, nbconvert, tabulate

## Installation & Setup
To reproduce the analysis locally:

1. **Initialize the Virtual Environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate the Environment:**
   - **Windows (PowerShell):**
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running Instructions

### 1. Execute Standalone Pipeline
To run the automated cleaning, analysis, and plotting script:
```bash
python analysis.py
```
This logs process updates to `analysis.log`, outputs statistical markdown tables to standard output, and saves 7 high-resolution charts in the `plots/` folder.

### 2. Run Jupyter Notebook
To run the notebook server:
```bash
python -m notebook
```
Open [analysis.ipynb](analysis.ipynb) to inspect the inline executed cells, visualizations, and comprehensive observations.

### 3. Re-run Notebook Validation
To programmatically re-verify the notebook:
```bash
jupyter nbconvert --to notebook --execute --inplace analysis.ipynb
```

## Project Structure
```
product/
├── .gitignore               # Version control exclusion file
├── MEMORY.md                # IDE project tracking memory
├── README.md                # Project documentation (this file)
├── analysis.ipynb           # Executed Jupyter Notebook
├── analysis.py              # Modular Python pipeline script
├── fear_greed_index.csv     # Raw sentiment dataset
├── historical_data.csv      # Raw trading transaction dataset
├── requirements.txt         # Locked dependencies file
├── plots/                   # Saved high-resolution figures
│   ├── correlation_heatmap.png
│   ├── cumulative_pnl_by_sentiment.png
│   ├── daily_volume_vs_sentiment.png
│   ├── long_vs_short_performance.png
│   ├── sentiment_distribution.png
│   ├── top_assets.png
│   └── top_traders.png
└── prime_task.zip           # Complete project bundle
```

## Key Findings
- **Bimodal Sentiment Peaks:** Profitability shows non-linear characteristics, peaking during Extreme Greed (average realized PnL: **$130.21**, win rate: **89.17%**) and Fear (average realized PnL: **$112.63**, win rate: **87.29%**). Profitability drops during Neutral and standard Greed regimes.
- **Long-Bias Performance:** Long positions represent **64.3%** of all realized profits ($6.59M vs $3.67M) with an **85.95% win rate** and lower variance compared to Short positions, which exhibit a **78.00% win rate** and over double the standard deviation.
- **Volume surges in Fear:** Daily trading volume has a moderate negative correlation with daily Fear & Greed index values (Pearson: **-0.26**), statistically validating that market activity accelerates during fear and capitulation.
- **Spearman Trade-Level Insights:** The rank correlation between individual trade sizes and Closed PnL is **+0.48**, and trade sizes show a negative rank correlation of **-0.12** with market greed, indicating that average trade sizes are larger during Fear.

## Future Work
- **Predictive ML Classifiers:** Build models to predict trade profitability using lagged sentiment, sizes, and past volatility.
- **Trader Behavior Clustering:** Implement K-Means clustering to partition account profiles (retail vs. market makers/bots).
- **Time-Series Forecasting:** Implement ARIMA or LSTM models to forecast daily platform volume and fee revenues.
- **Risk Analysis:** Calculate Value at Risk (VaR) and maximum drawdowns across sentiment regimes.
