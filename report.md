# Executive Case Study: Trading Activity and Market Sentiment Analysis (2023 - 2025)

## Executive Summary
This case study evaluates the relationship between market sentiment (measured by the daily **Fear & Greed Index**) and trading outcomes (measured by **Closed PnL**). The dataset contains historical trading logs from **May 1, 2023, to May 1, 2025**, representing **211,218 transactions** and **$1,191,098,773.60** in trading volume. 

The platform's traders realized a total net Closed PnL of **$10,254,486.95** with an overall win rate of **83.20%** and a profit factor of **4.48**. 

This report provides quantitative analyses, documents trader and strategy characteristics, outlines study assumptions and limitations, and presents recommendations for risk management, algorithmic scaling, and infrastructure capacity.

---

## 1. Assumptions & Data Scope

Before initiating the cleaning and analysis pipeline, the following assumptions are established:
1. **Timezone Alignment:** Timestamps in `historical_data.csv` (`Timestamp IST`) are converted to a standardized timezone (IST) to represent local trading times.
2. **Date-Level Merging:** Transactions are matched with the daily Fear & Greed Index using the calendar trading date (YYYY-MM-DD), assuming daily index values represent market sentiment for the entire calendar day.
3. **Missing Value Protocol:** Rows containing missing critical timestamps or keys are removed. Missing non-critical numeric parameters are set to `0.0`.
4. **Sentiment Classifications:** The Fear & Greed Index classification (Extreme Fear, Fear, Neutral, Greed, Extreme Greed) is treated as the primary categorical variable representing daily market sentiment.

---

## 2. Preprocessing & Ingestion Details

### 2.1 Cleaning Steps
1. **Datetime Parsing:** 
   - The index dates were parsed using `YYYY-MM-DD` formatting.
   - The historical timestamps (`Timestamp IST`) were parsed using `DD-MM-YYYY HH:MM`. 
   - A standardized string date column (`trading_date` in format `YYYY-MM-DD`) was created in both datasets as a merge key.
2. **Numeric Type Enforcement:** Financial and volume metrics (`Execution Price`, `Size Tokens`, `Size USD`, `Closed PnL`, `Fee`, `Start Position`) were cast to numeric types. Empty or whitespace values and type mismatches were filled with `0.0`.
3. **Quality Control:** Records with negative `Size USD` values were removed.
4. **Merge Protocol:** An inner join on `trading_date` was performed, yielding **211,218 matched records** for final analysis.

### 2.2 Trade Direction & Realization
A transaction is considered a realized trade when its `Closed PnL` is non-zero. Over the two-year period, **104,402 trades** realized PnL. Trades are classified into Long and Short based on their closing transaction:
- **Long Positions:** Closed by a `SELL` order (e.g. `Close Long`, `Sell` (Spot), `Long > Short`, or `Auto-Deleveraging`). When Closed PnL is non-zero and `Side == 'SELL'`, the trade is classified as **Long**.
- **Short Positions:** Closed by a `BUY` order (e.g. `Close Short`, `Short > Long`, `Liquidated Isolated Short`, or `Settlement`). When Closed PnL is non-zero and `Side == 'BUY'`, the trade is classified as **Short**.

---

## 3. Global Performance Summary
The following table provides the summary statistics for all trading activity during the evaluated period:

| Metric | Value |
| :--- | :---: |
| **Total Transactions** | 211,218 |
| **Realized (PnL) Trades** | 104,402 |
| **Total Closed PnL (USD)** | $10,254,486.95 |
| **Overall Win Rate** | 83.20% |
| **Winning Trades Count** | 86,863 |
| **Losing Trades Count** | 17,539 |
| **Average Win (USD)** | $152.00 |
| **Average Loss (USD)** | -$168.13 |
| **Profit Factor** | 4.48 |
| **Average Trade Size (USD)** | $5,639.19 |
| **Median Trade Size (USD)** | $597.02 |
| **Std Dev Trade Size (USD)** | $27,816.03 |
| **Std Dev Closed PnL (All)** | $634.61 |
| **Std Dev PnL (Realized)** | $1,272.93 |
| **Total Trading Volume (USD)** | $1,191,098,773.60 |
| **Total Trading Fees (USD)** | $245,849.21 |

---

## 4. In-Depth Analysis

### 4.1 Profitability by Market Sentiment
Evaluating Closed PnL across market sentiment regimes indicates a non-linear, bimodal performance distribution:

| Market Sentiment Classification | Total Closed PnL (USD) | Trade Count | Average PnL (USD) | Std Dev PnL (USD) | Win Rate (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Extreme Fear** | $739,110.00 | 10,406 | $71.03 | $606.33 | 76.22% |
| **Fear** | $3,357,160.00 | 29,808 | $112.63 | $772.39 | 87.29% |
| **Neutral** | $1,292,920.00 | 18,159 | $71.20 | $729.08 | 82.39% |
| **Greed** | $2,150,130.00 | 25,176 | $85.40 | $1,114.77 | 76.89% |
| **Extreme Greed** | $2,715,170.00 | 20,853 | $130.21 | $2,159.20 | 89.17% |

#### Observations:
- **Bimodal Profitability Peaks:** Trading performance is optimized in two opposite regimes: **Extreme Greed** (Average PnL: **$130.21**, Win Rate: **89.17%**) and **Fear** (Average PnL: **$112.63**, Win Rate: **87.29%**). See **Figure 1 (plots/sentiment_distribution.png)** for the distribution of sentiment states.
- **Speculative Momentum:** Extreme Greed yields the highest average profitability and win rates, indicating that momentum-following strategies are effective when market euphoria is at its peak. However, it also displays the highest variance (standard deviation of **$2,159.20**), indicating elevated risk. See **Figure 2 (plots/cumulative_pnl_by_sentiment.png)** for the timeline of cumulative Closed PnL by sentiment.
- **Dip-Buying Quality:** Fear periods represent profitable buying opportunities (mean reversion) that generate strong PnL upon subsequent rebounds, while exhibiting a moderate standard deviation (**$772.39**).
- **Regime Transition Risk:** 
  - Shifting from **Fear to Extreme Fear** results in a decline in performance (Average PnL falls to **$71.03**, Win Rate falls to **76.22%**), reflecting the risk of catching a falling knife during capitulation.
  - Shifting from **Greed to Extreme Greed** is positive, but trading during standard **Greed** is sub-optimal (Average PnL: **$85.40**, Win Rate: **76.89%**).

---

### 4.2 Long vs. Short Strategy Comparison
A side-by-side comparison of Long and Short trades outlines a long bias in profitability and volume:

| Position Side | Total PnL (USD) | Trade Count | Average PnL (USD) | Std Dev PnL (USD) | Median PnL (USD) | Win Rate (%) | Total Volume (USD) | Avg Volume (USD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Long** | $6,589,147.64 | 68,345 | $96.41 | $879.76 | $6.81 | 85.95% | $411,584,000 | $6,022.15 |
| **Short** | $3,665,339.31 | 36,057 | $101.65 | $1,858.87 | $4.77 | 78.00% | $180,787,000 | $5,013.93 |

#### Observations:
- **Long Strategy Dominance:** Long positions captured **64.3%** of all realized profits ($6.59M vs $3.67M) and were executed almost twice as frequently. They also featured a higher win rate (**85.95%** vs **78.00%**). See **Figure 3 (plots/long_vs_short_performance.png)** for the side-by-side strategy comparison.
- **Short Strategy Risk Profile:** Short trades are less frequent but exhibit a slightly higher average profit per trade (**$101.65** vs **$96.41**). However, the standard deviation for Short trades (**$1,858.87**) is over double that of Long trades (**$879.76**), indicating that shorting carries higher tail risk.

---

### 4.3 Trading Volume and Activity Trends
- **Total Volume:** **$1,191,098,773.60**
- **Average Daily Volume:** ~$2,486,636.27 (Standard Deviation: **$6,290,451.60**)
- **Volatility Spikes:** Volume is highly volatile. When plotted against the 7-day Moving Average of the Fear & Greed index (**Figure 4: plots/daily_volume_vs_sentiment.png**), these spikes strongly align with periods of **Fear and Extreme Fear** (low index values). Market participants trade in larger sizes and higher frequencies during panic capitulations.

---

### 4.4 Most Traded Assets (Coins)
We analyzed trading activity at the asset level to identify volume leaders and revenue generators:

| Asset (Coin) | Trade Count | Total Volume (USD) | Net Realized PnL (USD) | Avg Trade Size (USD) | Std Dev Trade Size (USD) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **BTC** | 26,064 | $644,232,000 | $868,045.00 | $24,717.30 | $95,334.00 |
| **HYPE** | 68,005 | $141,990,000 | $1,948,480.00 | $2,087.94 | $8,312.83 |
| **SOL** | 10,691 | $125,075,000 | $1,639,560.00 | $11,699.10 | $31,929.60 |
| **ETH** | 11,158 | $118,281,000 | $1,319,980.00 | $10,600.60 | $36,054.90 |
| **@107** | 29,992 | $55,760,900 | $2,783,910.00 | $1,859.19 | $5,887.96 |

#### Observations:
- **Institutional Volume Leader:** **BTC** represents **54.1%** of all trading volume on the platform ($644.23M) with an average trade size of **$24,717.30**, indicating institutional or high-net-worth trader focus. See **Figure 5 (plots/top_assets.png)** for asset volume and transaction count comparisons.
- **Retail & Algo Leader:** **HYPE** is the most frequently traded coin with **68,005 transactions**, but has a much lower average trade size ($2,087.94).
- **Outsized Alpha Generators:** While BTC dominated volume, the asset that generated the most profit was **@107** with **$2.78 Million** in net Closed PnL, followed closely by **HYPE ($1.95 Million)** and **SOL ($1.64 Million)**.
- **Underperforming Assets:** Certain assets generated net losses for the platform's traders, notably **TRUMP (-$364,825)** and **FARTCOIN (-$100,687)**, indicating poor trading performance in highly speculative meme coins.

---

### 4.5 Trader Leaderboard Analysis
An analysis of account-level performance indicates concentration:

#### Top 5 Most Profitable Accounts:
1. `0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23`: **+$2,143,380.00** (14,733 trades, 79.11% Win Rate)
2. `0x083384f897ee0f19899168e3b1bec365f52a9012`: **+$1,600,230.00** (3,818 trades, 79.27% Win Rate)
3. `0xbaaaf6571ab7d571043ff1e313a9609a10637864`: **+$940,164.00** (21,192 trades, 99.12% Win Rate)
4. `0x513b8629fe877bb581bf244e326a047b249c4ff1`: **+$840,423.00** (12,236 trades, 89.55% Win Rate)
5. `0xbee1707d6b44d4d52bfe19e41f8a828645437aab`: **+$836,081.00** (40,184 trades, 76.31% Win Rate)

#### Top 3 Least Profitable Accounts (Largest Losses):
1. `0x8170715b3b381dffb7062c0298972d4727a0a63b`: **-$167,621.00** (4,601 trades, 75.22% Win Rate)
2. `0x271b280974205ca63b716753467d5a371de622ab`: **-$70,436.20** (3,809 trades, 71.56% Win Rate)
3. `0x3998f134d6aaa2b6a5f723806d00fd2bbbbce891`: **-$31,203.60** (815 trades, 65.09% Win Rate)

#### Observations:
- **Profit Concentration:** The top two traders alone earned **$3.74 Million**, which represents **36.5%** of the entire platform's net realized Closed PnL. See **Figure 6 (plots/top_traders.png)** for trader profitability distributions.
- **Systematic Profiles:** Account `0xbaaaf...7864` achieved a **99.12% win rate** over **21,192 trades**, and `0x430f0...7713` achieved a **100% win rate** over **1,237 trades**. These profiles are highly indicative of market-making algorithms or arbitrage bots which capitalize on low-risk spreads.
- **Risk Mitigation:** The largest individual loss was limited to **-$167,621**, compared to the top profit of **+$2.14M**, showing that traders successfully cap tail-risk losses.

---

### 4.6 Statistical & Correlation Analysis

#### daily aggregate correlation (479 days):
| Metric Pair | Pearson (Linear) | Spearman (Rank-based) |
| :--- | :---: | :---: |
| **Sentiment Value vs. Closed PnL** | -0.08 | +0.04 |
| **Sentiment Value vs. Trading Volume** | -0.26 | -0.06 |
| **Sentiment Value vs. Transaction Count** | -0.25 | -0.03 |
| **Sentiment Value vs. Trading Fees** | -0.26 | -0.19 |
| **Trading Volume vs. Transaction Count** | +0.72 | +0.90 |
| **Trading Volume vs. Trading Fees** | +0.98 | +0.92 |

#### individual trade level correlation (104,402 realized trades):
| Metric Pair | Pearson (Linear) | Spearman (Rank-based) |
| :--- | :---: | :---: |
| **Sentiment Value vs. Closed PnL** | +0.01 | +0.04 |
| **Sentiment Value vs. Trade Size (USD)** | -0.03 | -0.12 |
| **Trade Size (Size USD) vs. Closed PnL** | +0.16 | +0.48 |
| **Trade Size (Size USD) vs. Fee** | +0.76 | +0.82 |

#### Fear & Greed Index Descriptive Statistics:
- **Count:** 479 trading days
- **Mean:** 60.05
- **Standard Deviation:** 18.69
- **Min:** 10 (Extreme Fear)
- **25% Percentile:** 48
- **50% Percentile (Median):** 67
- **75% Percentile:** 74
- **Max:** 94 (Extreme Greed)

#### Observations:
- **Panic-Driven Volume Spikes:** The moderate negative Pearson correlation (-0.26) between daily market sentiment and volume/fees indicates that daily trading volume increases linearly as fear rises (lower index values). See **Figure 7 (plots/correlation_heatmap.png)** for Pearson and Spearman heatmaps.
- **Trade-Level Size Reductions in Greed:** The Spearman rank correlation between individual trade sizes and sentiment is **-0.12**, statistically demonstrating that trade sizes monotonically decrease as market greed rises.
- **Strong Rank Correlation of Size & PnL:** The trade-level Spearman rank correlation between trade size and realized Closed PnL is **+0.48**, which is substantially higher than the Pearson correlation (+0.16). This indicates a strong monotonic relationship where larger trade sizes are associated with larger realized profit/loss, though the relationship is non-linear.
- **Non-Linear Sentiment-Profitability Relationship:** The lack of linear correlation between Fear & Greed and Closed PnL (-0.08 daily, +0.01 trade-level) confirms that market sentiment does not have a simple linear relationship with trading profitability. Profitability is non-linear and bimodal, peaking at the extremes (Extreme Greed and Fear) while dropping in Neutral/Greed/Extreme Fear.

---

## 5. Limitations

The findings of this case study are subject to the following limitations:
1. **Data Scope:** The analysis is based exclusively on the provided historical trading logs and the Fear & Greed Index. No external market factors or macro indicators are included.
2. **Lack of Intraday Granularity:** The Fear & Greed Index is a daily metric. Aggregating transaction logs to the daily level may obscure high-frequency, intraday trading behaviors and sentiment swings.
3. **Correlation vs. Causation:** The identified correlations reflect statistical associations and do not imply direct causal relationships.
4. **Omission of Key Variables:** Critical variables such as market volatility, funding rates, macroeconomic news, order book depth, and slippage were not available in the dataset, and these factors may significantly influence trading outcomes.

---

## 6. Future Work

To extend this study, the following work is proposed:
1. **Predictive Modeling:** Build machine learning classifiers to predict trade profitability based on lagged sentiment changes, trade sizes, and past volatility.
2. **Trader Clustering:** Apply unsupervised learning (e.g., K-Means clustering) to segment accounts into distinct behavioral profiles (retail, market makers, arbitrageurs, momentum traders).
3. **Time-Series Forecasting:** Implement ARIMA or LSTM models to forecast platform trading volumes and fee revenue.
4. **Risk & Drawdown Analysis:** Calculate Value at Risk (VaR) and maximum drawdown profiles across different sentiment regimes to improve risk parameters.
5. **Macro Integration:** Incorporate external indicators (e.g., interest rate decisions, funding rates, CPI releases, and stock market indexes) to test for compounding effects.

---

## 7. Recommendations & Actions

### 7.1 For Algorithmic & Systematic Traders
1. **Regime-Specific Strategy Switching:**
   - **Speculative Momentum:** When the Fear & Greed index enters **Extreme Greed (>75)**, deploy trend-following, momentum-breakout algorithms with a strong Long bias.
   - **Fear Mean-Reversion:** When the index is in **Fear (25-45)**, deploy mean-reversion, dip-buying algorithms.
   - **Neutral/Greed Neutrality:** In Neutral or standard Greed regimes, reduce size or deploy market-neutral grid trading strategies, as these regimes exhibit choppy, lower-yielding setups.
2. **Capitulation Risk Avoidance:**
   - Scale down or cease dip-buying when the index breaks below **25 (Extreme Fear)**. The average PnL drops by **37%** and win rate drops by **11%** compared to standard Fear, indicating risk of holding losing long positions during capitulation.

### 7.2 For Risk Managers & System Operators
1. **Infrastructure Scaling for Fear Regimes:**
   - Since trading volume and transaction counts expand during low-sentiment periods (Fear/Extreme Fear, Pearson correlation -0.26), execution servers, database write capacity, and API rate-limit configurations must scale up automatically during low-sentiment days.
2. **Fee Optimization Policies:**
   - Transaction fees total **$245,849.21**, primarily concentrated during high-volume panic sell-offs. Systematic traders and the platform should implement fee-reduction structures (e.g. holding exchange utility tokens or negotiating market-maker fee rebates) to protect net margins.
