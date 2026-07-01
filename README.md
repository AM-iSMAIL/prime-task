# Trading Performance and Market Sentiment Case Study

## Project Overview
This repository contains a professional data science case study that analyzes historical trading activity and merges it with the daily Fear & Greed Index to evaluate how market sentiment correlates with trading profitability, volumes, styles (long vs. short), trade sizes, and trader behaviors. 

## Objective
The primary objective of this project is to perform an Exploratory Data Analysis (EDA) and run rigorous statistical correlation tests on a matched dataset of historical trading logs and market sentiment scores, producing a refined, production-grade analysis suitable for investment and risk management review.

## Dataset Description
1. **`historical_data.csv`:** Contains 211,224 raw transaction records with parameters: Account, Coin, Execution Price, Size Tokens, Size USD, Side (BUY/SELL), Timestamp IST, Start Position, Direction (e.g., Open/Close Long/Short), Closed PnL, Transaction Hash, Order ID, Crossed, Fee, and Trade ID.
2. **`fear_greed_index.csv`:** Contains 2,644 daily records tracking market sentiment with fields: timestamp, value (0-100), classification (Extreme Fear, Fear, Neutral, Greed, Extreme Greed), and date (YYYY-MM-DD).

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

## Installation
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

## How to Run

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

## Generated Outputs
Upon running the pipeline, the following professional-grade artifacts are generated:
- **`analysis.log`:** Runtime logs detailing ingestion sizes, cleaning counts, and task progress using neutral terminology.
- **`report.md`:** A comprehensive executive summary report written in an objective, academic style outlining prep steps, strategy side definitions, bimodal metrics, and leaderboards.
- **`plots/sentiment_distribution.png`:** Combined chart representing the Fear & Greed value histogram and classification day counts (Figure 1).
- **`plots/cumulative_pnl_by_sentiment.png`:** Line chart tracking cumulative closed PnL with translucent color blocks overlaying daily market sentiment (Figure 2).
- **`plots/long_vs_short_performance.png`:** Strategy comparison showing net Closed PnL, win rates, and closed transaction counts side-by-side (Figure 3).
- **`plots/daily_volume_vs_sentiment.png`:** Dual-axis visualization showing volume volatility against the 7-day moving average of the sentiment index (Figure 4).
- **`plots/top_assets.png`:** Horizontal bar charts identifying top assets by trading volume and transaction counts (Figure 5).
- **`plots/top_traders.png`:** Horizontal bar charts plotting top 10 profitable and top 5 losing accounts (Figure 6).
- **`plots/correlation_heatmap.png`:** Double-panel correlation heatmaps representing Pearson Linear and Spearman Rank correlation matrices side-by-side (Figure 7).
- **`prime_task.zip`:** Compacted project archive bundling all files and plots, excluding the virtual environment `.venv`.

## Key Insights
- **Bimodal Sentiment Performance:** Profitability peaks in **Extreme Greed** (average realized PnL: **$130.21**, win rate: **89.17%**) and **Fear** (average realized PnL: **$112.63**, win rate: **87.29%**), dropping during Neutral and standard Greed regimes.
- **Long-Bias Dominance:** Long positions represent **64.3%** of all realized profits ($6.59M vs $3.67M) with an **85.95% win rate** and lower variance compared to Short positions (**78.00% win rate**, double the standard deviation).
- **Panic-Driven Volume Spikes:** Daily volume shows a moderate negative Pearson correlation with sentiment index values (**-0.26**), indicating trading activity accelerates during fear and capitulation.
- **Spearman Trade-Level Insights:** Individual trade sizes exhibit a negative Spearman rank correlation of **-0.12** with market greed, indicating that average trade sizes are larger during Fear. The rank correlation between individual trade sizes and Closed PnL is **+0.48**.

## Limitations
- **Data Constraints:** The study relies solely on the provided trading logs and Fear & Greed index. No external market factors are considered.
- **Daily Aggregation:** Daily index granularity ignores high-frequency, intraday trading dynamics.
- **Correlation Boundaries:** Statistical correlation does not establish causation.
- **Omission of Key Variables:** Factors like funding rates, market volatility, macroeconomic news, order book details, and execution slippage are missing from the dataset.

## Future Work
- **Predictive ML Modeling:** Train classifiers to forecast trade outcomes based on lagged sentiment.
- **Trader Behavior Clustering:** Group account addresses using K-Means to segment retail, market makers, and arbitrageurs.
- **Time-Series Revenue Forecasts:** Implement ARIMA/LSTM models to project daily volumes and fees.
- **Regime Risk Profiling:** Compute Value at Risk (VaR) and maximum drawdowns across sentiment regimes.
- **Macro Feature Integration:** Merge external data feeds (CPI, stock indexes, interest rates).
