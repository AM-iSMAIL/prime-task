import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging

# Configure logging using neutral terminology
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('analysis.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Set plotting style for professional look
sns.set_theme(style="whitegrid", context="talk")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'figure.titlesize': 20,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'figure.figsize': (12, 7),
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
})

# Customized color palette
SENTIMENT_PALETTE = {
    'Extreme Fear': '#D50000',  # Red
    'Fear': '#FF6D00',          # Orange
    'Neutral': '#90A4AE',       # Slate Gray
    'Greed': '#00BFA5',         # Teal
    'Extreme Greed': '#00C853'  # Green
}

def load_data(historical_path, fear_greed_path):
    """Load the historical trading data and fear/greed index."""
    logger.info("Loading datasets.")
    try:
        df_hist = pd.read_csv(historical_path)
        df_fg = pd.read_csv(fear_greed_path)
        logger.info(f"Historical trading data shape: {df_hist.shape}")
        logger.info(f"Fear & Greed Index shape: {df_fg.shape}")
        return df_hist, df_fg
    except Exception as e:
        logger.error(f"Error loading datasets: {e}")
        raise

def clean_data(df_hist, df_fg):
    """Clean missing values and convert timestamps to datetime."""
    logger.info("Cleaning and preprocessing data.")
    
    # 1. Clean Fear & Greed Index
    df_fg_clean = df_fg.copy()
    df_fg_clean = df_fg_clean.dropna(subset=['date', 'value', 'classification'])
    df_fg_clean['date_parsed'] = pd.to_datetime(df_fg_clean['date'], format='%Y-%m-%d', errors='coerce')
    df_fg_clean['value'] = pd.to_numeric(df_fg_clean['value'], errors='coerce')
    df_fg_clean = df_fg_clean.dropna(subset=['date_parsed', 'value'])
    df_fg_clean['trading_date'] = df_fg_clean['date_parsed'].dt.strftime('%Y-%m-%d')
    
    # 2. Clean Historical Data
    df_hist_clean = df_hist.copy()
    df_hist_clean['timestamp_ist'] = pd.to_datetime(df_hist_clean['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    df_hist_clean = df_hist_clean.dropna(subset=['timestamp_ist'])
    df_hist_clean['trading_date'] = df_hist_clean['timestamp_ist'].dt.strftime('%Y-%m-%d')
    
    # Convert numeric fields
    numeric_cols = ['Execution Price', 'Size Tokens', 'Size USD', 'Closed PnL', 'Fee', 'Start Position']
    for col in numeric_cols:
        if col in df_hist_clean.columns:
            df_hist_clean[col] = pd.to_numeric(df_hist_clean[col], errors='coerce').fillna(0.0)
            
    # Drop rows with negative Size USD (if any)
    df_hist_clean = df_hist_clean[df_hist_clean['Size USD'] >= 0]
    
    logger.info("Data cleaning completed.")
    return df_hist_clean, df_fg_clean

def merge_datasets(df_hist, df_fg):
    """Merge trading data with Fear & Greed Index on trading date."""
    logger.info("Merging datasets.")
    # Select key columns from Fear & Greed
    df_fg_subset = df_fg[['trading_date', 'value', 'classification']].rename(
        columns={'value': 'fg_value', 'classification': 'fg_classification'}
    )
    df_fg_subset = df_fg_subset.drop_duplicates(subset=['trading_date'])
    
    # Perform inner merge
    df_merged = pd.merge(df_hist, df_fg_subset, on='trading_date', how='inner')
    logger.info(f"Merged dataset contains {df_merged.shape[0]} rows")
    
    # Classify Long vs Short trades based on closing transaction side
    # If Side == SELL and Closed PnL != 0 -> Long position closed
    # If Side == BUY and Closed PnL != 0 -> Short position closed
    df_merged['Position_Side'] = np.where(
        df_merged['Closed PnL'] != 0.0,
        np.where(df_merged['Side'] == 'SELL', 'Long', 'Short'),
        'No_Realized_PnL'
    )
    
    return df_merged

def run_pnl_analysis(df):
    """Analyze Closed PnL and trade metrics."""
    logger.info("Analyzing Closed PnL and sentiment performance.")
    
    # Filter for realized trades
    df_realized = df[df['Closed PnL'] != 0.0]
    total_realized_trades = len(df_realized)
    
    total_pnl = df_realized['Closed PnL'].sum()
    winning_trades = df_realized[df_realized['Closed PnL'] > 0]
    losing_trades = df_realized[df_realized['Closed PnL'] < 0]
    
    win_rate = (len(winning_trades) / total_realized_trades) * 100 if total_realized_trades > 0 else 0
    avg_win = winning_trades['Closed PnL'].mean() if len(winning_trades) > 0 else 0
    avg_loss = losing_trades['Closed PnL'].mean() if len(losing_trades) > 0 else 0
    profit_factor = abs(winning_trades['Closed PnL'].sum() / losing_trades['Closed PnL'].sum()) if losing_trades['Closed PnL'].sum() != 0 else np.inf
    
    # Standard deviation calculations
    std_pnl_all = df['Closed PnL'].std()
    std_pnl_realized = df_realized['Closed PnL'].std()
    std_size_usd = df['Size USD'].std()
    
    print("\n" + "="*50)
    print("GLOBAL TRADING METRICS SUMMARY")
    print("="*50)
    print(f"Total Transactions:         {len(df):,}")
    print(f"Realized (PnL) Trades:      {total_realized_trades:,}")
    print(f"Total Closed PnL (USD):    ${total_pnl:,.2f}")
    print(f"Overall Win Rate:           {win_rate:.2f}%")
    print(f"Winning Trades Count:       {len(winning_trades):,}")
    print(f"Losing Trades Count:        {len(losing_trades):,}")
    print(f"Average Win (USD):         ${avg_win:,.2f}")
    print(f"Average Loss (USD):        ${avg_loss:,.2f}")
    print(f"Profit Factor:              {profit_factor:.2f}")
    print(f"Average Trade Size (USD):  ${df['Size USD'].mean():,.2f}")
    print(f"Median Trade Size (USD):   ${df['Size USD'].median():,.2f}")
    print(f"Std Dev Trade Size (USD):  ${std_size_usd:,.2f}")
    print(f"Std Dev Closed PnL (All):  ${std_pnl_all:,.2f}")
    print(f"Std Dev PnL (Realized):    ${std_pnl_realized:,.2f}")
    print(f"Total Trading Volume (USD):${df['Size USD'].sum():,.2f}")
    print(f"Total Trading Fees (USD):  ${df['Fee'].sum():,.2f}")
    print("="*50 + "\n")
    
    # Sentiment level performance
    sentiment_perf = df_realized.groupby('fg_classification').agg(
        total_pnl=('Closed PnL', 'sum'),
        trade_count=('Closed PnL', 'count'),
        avg_pnl=('Closed PnL', 'mean'),
        std_pnl=('Closed PnL', 'std'),
        win_rate=('Closed PnL', lambda x: (x > 0).mean() * 100)
    ).reindex(['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
    
    print("PERFORMANCE BY MARKET SENTIMENT")
    print(sentiment_perf.to_markdown())
    print("\n" + "="*50 + "\n")
    
    return sentiment_perf

def run_long_vs_short_analysis(df):
    """Analyze performance of Long vs Short trades."""
    logger.info("Analyzing Long vs Short performance.")
    df_realized = df[df['Closed PnL'] != 0.0]
    
    ls_perf = df_realized.groupby('Position_Side').agg(
        total_pnl=('Closed PnL', 'sum'),
        trade_count=('Closed PnL', 'count'),
        avg_pnl=('Closed PnL', 'mean'),
        std_pnl=('Closed PnL', 'std'),
        median_pnl=('Closed PnL', 'median'),
        win_rate=('Closed PnL', lambda x: (x > 0).mean() * 100),
        total_volume=('Size USD', 'sum'),
        avg_volume=('Size USD', 'mean')
    )
    
    print("LONG VS SHORT PERFORMANCE")
    print(ls_perf.to_markdown())
    print("\n" + "="*50 + "\n")
    
    return ls_perf

def run_asset_analysis(df):
    """Analyze most traded assets."""
    logger.info("Analyzing asset trading activity.")
    
    asset_perf = df.groupby('Coin').agg(
        trade_count=('Size USD', 'count'),
        total_volume=('Size USD', 'sum'),
        realized_pnl=('Closed PnL', 'sum'),
        avg_trade_size=('Size USD', 'mean'),
        std_trade_size=('Size USD', 'std')
    ).sort_values(by='total_volume', ascending=False)
    
    print("TOP 10 MOST TRADED ASSETS BY VOLUME")
    print(asset_perf.head(10).to_markdown())
    print("\n" + "="*50 + "\n")
    
    return asset_perf

def run_trader_analysis(df):
    """Analyze trader profitability."""
    logger.info("Analyzing trader profitability.")
    
    trader_perf = df.groupby('Account').agg(
        total_pnl=('Closed PnL', 'sum'),
        trade_count=('Size USD', 'count'),
        total_volume=('Size USD', 'sum'),
        avg_trade_size=('Size USD', 'mean'),
        win_rate=('Closed PnL', lambda x: (x[x != 0.0] > 0).mean() * 100 if (x != 0.0).any() else 0)
    ).sort_values(by='total_pnl', ascending=False)
    
    print("TOP 10 MOST PROFITABLE TRADERS")
    print(trader_perf.head(10).to_markdown())
    print("\nTOP 5 LEAST PROFITABLE TRADERS (LARGEST LOSSES)")
    print(trader_perf.tail(5).to_markdown())
    print("\n" + "="*50 + "\n")
    
    return trader_perf

def run_correlation_analysis(df):
    """Analyze correlation between sentiment and trading variables."""
    logger.info("Analyzing correlation metrics.")
    
    # 1. Aggregate on a daily basis
    daily_stats = df.groupby('trading_date').agg(
        avg_fg_value=('fg_value', 'mean'),
        total_pnl=('Closed PnL', 'sum'),
        total_volume=('Size USD', 'sum'),
        trade_count=('Size USD', 'count'),
        avg_trade_size=('Size USD', 'mean'),
        total_fees=('Fee', 'sum')
    ).reset_index()
    
    # Calculate daily correlation matrices (Pearson and Spearman)
    target_cols = ['avg_fg_value', 'total_pnl', 'total_volume', 'trade_count', 'avg_trade_size', 'total_fees']
    daily_corr_pearson = daily_stats[target_cols].corr(method='pearson')
    daily_corr_spearman = daily_stats[target_cols].corr(method='spearman')
    
    print("DAILY AGGREGATE CORRELATION MATRIX (PEARSON)")
    print(daily_corr_pearson.to_markdown())
    print("\nDAILY AGGREGATE CORRELATION MATRIX (SPEARMAN)")
    print(daily_corr_spearman.to_markdown())
    print("\n" + "="*50 + "\n")
    
    # 2. Individual transaction correlation (Pearson and Spearman)
    df_realized = df[df['Closed PnL'] != 0.0]
    ind_cols = ['fg_value', 'Closed PnL', 'Size USD', 'Fee']
    individual_corr_pearson = df_realized[ind_cols].corr(method='pearson')
    individual_corr_spearman = df_realized[ind_cols].corr(method='spearman')
    
    print("INDIVIDUAL TRADE LEVEL CORRELATION MATRIX (PEARSON)")
    print(individual_corr_pearson.to_markdown())
    print("\nINDIVIDUAL TRADE LEVEL CORRELATION MATRIX (SPEARMAN)")
    print(individual_corr_spearman.to_markdown())
    print("\n" + "="*50 + "\n")
    
    # 3. Descriptive stats of the Fear & Greed index itself
    daily_fg = df.drop_duplicates(subset=['trading_date'])
    fg_stats = daily_fg['fg_value'].describe()
    print("FEAR & GREED INDEX VALUE DESCRIPTIVE STATISTICS")
    print(fg_stats.to_markdown())
    print("\n" + "="*50 + "\n")
    
    # Daily PnL and Volume standard deviations
    std_daily_pnl = daily_stats['total_pnl'].std()
    std_daily_volume = daily_stats['total_volume'].std()
    print(f"Daily PnL Standard Deviation:       ${std_daily_pnl:,.2f}")
    print(f"Daily Volume Standard Deviation:    ${std_daily_volume:,.2f}")
    print("="*50 + "\n")
    
    return daily_stats, daily_corr_pearson, daily_corr_spearman, individual_corr_pearson, individual_corr_spearman

def generate_visualizations(df, daily_stats, daily_corr_pearson, daily_corr_spearman, output_dir='plots'):
    """Generate and save professional visualizations."""
    logger.info(f"Generating and saving plots to {output_dir}/.")
    os.makedirs(output_dir, exist_ok=True)
    
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    
    # -------------------------------------------------------------
    # Plot 1: Sentiment Distribution & Classification Breakdown
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    daily_fg = df.drop_duplicates(subset=['trading_date'])
    sns.histplot(daily_fg['fg_value'], kde=True, bins=25, color='#4D4DFF', ax=ax1)
    ax1.set_title("Fear & Greed Index Value Distribution", pad=15)
    ax1.set_xlabel("Fear & Greed Index Value (0-100)")
    ax1.set_ylabel("Count of Days")
    
    class_counts = daily_fg['fg_classification'].value_counts().reindex(sentiment_order)
    sns.barplot(
        x=class_counts.index, 
        y=class_counts.values, 
        palette=[SENTIMENT_PALETTE[c] for c in class_counts.index], 
        ax=ax2, 
        hue=class_counts.index,
        legend=False
    )
    ax2.set_title("Market Sentiment Classification Counts (Days)", pad=15)
    ax2.set_xlabel("Market Sentiment")
    ax2.set_ylabel("Number of Days")
    plt.xticks(rotation=15)
    
    plt.suptitle("Market Sentiment Analysis (Fear & Greed Index)", fontsize=22, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sentiment_distribution.png'))
    plt.close()
    
    # -------------------------------------------------------------
    # Plot 2: Cumulative Closed PnL over Time by Sentiment
    # -------------------------------------------------------------
    plt.figure(figsize=(14, 8))
    daily_stats_sorted = daily_stats.sort_values(by='trading_date').copy()
    daily_stats_sorted['trading_date_dt'] = pd.to_datetime(daily_stats_sorted['trading_date'])
    daily_stats_sorted['cumulative_pnl'] = daily_stats_sorted['total_pnl'].cumsum()
    
    daily_fg_classification = df.drop_duplicates(subset=['trading_date'])[['trading_date', 'fg_classification']]
    daily_stats_sorted = pd.merge(daily_stats_sorted, daily_fg_classification, on='trading_date', how='left')
    
    plt.plot(daily_stats_sorted['trading_date_dt'], daily_stats_sorted['cumulative_pnl'], color='#37474F', linewidth=2.5, label='Cumulative PnL')
    
    # Shading regions by sentiment
    current_sentiment = None
    start_date = None
    
    for idx, row in daily_stats_sorted.iterrows():
        date = row['trading_date_dt']
        sentiment = row['fg_classification']
        
        if current_sentiment is None:
            current_sentiment = sentiment
            start_date = date
        elif current_sentiment != sentiment or idx == daily_stats_sorted.index[-1]:
            color = SENTIMENT_PALETTE.get(current_sentiment, '#CFD8DC')
            plt.axvspan(start_date, date, color=color, alpha=0.15)
            current_sentiment = sentiment
            start_date = date
            
    for name, color in SENTIMENT_PALETTE.items():
        plt.scatter([], [], color=color, alpha=0.5, label=name, s=100)
        
    plt.title("Cumulative Closed PnL over Time with Sentiment Overlay", pad=20)
    plt.xlabel("Trading Date")
    plt.ylabel("Cumulative PnL (USD)")
    plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x*1e-6:.1f}M"))
    plt.legend(title='Market Sentiment', bbox_to_anchor=(1.02, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cumulative_pnl_by_sentiment.png'))
    plt.close()
    
    # -------------------------------------------------------------
    # Plot 3: Long vs Short Performance Comparison
    # -------------------------------------------------------------
    df_realized = df[df['Closed PnL'] != 0.0]
    ls_perf = df_realized.groupby('Position_Side').agg(
        total_pnl=('Closed PnL', 'sum'),
        trade_count=('Closed PnL', 'count'),
        win_rate=('Closed PnL', lambda x: (x > 0).mean() * 100)
    ).reset_index()
    
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 7))
    
    # Total PnL
    sns.barplot(x='Position_Side', y='total_pnl', data=ls_perf, palette=['#00E676', '#FF1744'], ax=ax1, hue='Position_Side', legend=False)
    ax1.set_title("Total Realized PnL (USD)", pad=15)
    ax1.set_xlabel("Position Side")
    ax1.set_ylabel("Total PnL ($)")
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x*1e-6:.1f}M"))
    
    # Win Rate
    sns.barplot(x='Position_Side', y='win_rate', data=ls_perf, palette=['#00E676', '#FF1744'], ax=ax2, hue='Position_Side', legend=False)
    ax2.set_title("Win Rate (%)", pad=15)
    ax2.set_xlabel("Position Side")
    ax2.set_ylabel("Win Rate (%)")
    ax2.set_ylim(0, 100)
    for p in ax2.patches:
        ax2.annotate(f"{p.get_height():.2f}%", (p.get_x() + p.get_width() / 2., p.get_height() - 8),
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points', color='white', weight='bold')
                    
    # Trade Count
    sns.barplot(x='Position_Side', y='trade_count', data=ls_perf, palette=['#00E676', '#FF1744'], ax=ax3, hue='Position_Side', legend=False)
    ax3.set_title("Number of Closed Trades", pad=15)
    ax3.set_xlabel("Position Side")
    ax3.set_ylabel("Trades Count")
    ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x*1e-3:.0f}K"))
    
    plt.suptitle("Long vs. Short Performance Comparison", fontsize=22, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'long_vs_short_performance.png'))
    plt.close()
    
    # -------------------------------------------------------------
    # Plot 4: Daily Trading Volume vs. Fear & Greed Index Value
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(15, 8))
    
    daily_stats_sorted['trading_date_dt'] = pd.to_datetime(daily_stats_sorted['trading_date'])
    ax1.plot(daily_stats_sorted['trading_date_dt'], daily_stats_sorted['total_volume'], color='#1A237E', linewidth=1.5, label='Daily Volume (USD)')
    ax1.set_xlabel('Trading Date', labelpad=10)
    ax1.set_ylabel('Daily Trading Volume (USD)', color='#1A237E', labelpad=10)
    ax1.tick_params(axis='y', labelcolor='#1A237E')
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x*1e-6:.1f}M"))
    
    ax2 = ax1.twinx()
    daily_stats_sorted['fg_ma7'] = daily_stats_sorted['avg_fg_value'].rolling(window=7, min_periods=1).mean()
    ax2.plot(daily_stats_sorted['trading_date_dt'], daily_stats_sorted['fg_ma7'], color='#FF6D00', linewidth=2.5, linestyle='--', label='Fear & Greed Index (7D MA)')
    ax2.set_ylabel('Fear & Greed Index Value (7D MA)', color='#FF6D00', labelpad=10)
    ax2.tick_params(axis='y', labelcolor='#FF6D00')
    ax2.set_ylim(0, 100)
    
    plt.title('Daily Trading Volume vs. Fear & Greed Index Trend', pad=20)
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, 'daily_volume_vs_sentiment.png'))
    plt.close()
    
    # -------------------------------------------------------------
    # Plot 5: Top 10 Most Traded Assets
    # -------------------------------------------------------------
    asset_perf = df.groupby('Coin').agg(
        trade_count=('Size USD', 'count'),
        total_volume=('Size USD', 'sum')
    ).sort_values(by='total_volume', ascending=False).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Top 10 by Volume
    top10_vol = asset_perf.head(10)
    sns.barplot(x='total_volume', y='Coin', data=top10_vol, palette='viridis', ax=ax1, hue='Coin', legend=False)
    ax1.set_title("Top 10 Assets by Total Volume (USD)", pad=15)
    ax1.set_xlabel("Total Trading Volume ($)")
    ax1.set_ylabel("Asset Name (Coin)")
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x*1e-6:.1f}M"))
    
    # Top 10 by Trade Count
    asset_perf_count = asset_perf.sort_values(by='trade_count', ascending=False)
    top10_count = asset_perf_count.head(10)
    sns.barplot(x='trade_count', y='Coin', data=top10_count, palette='magma', ax=ax2, hue='Coin', legend=False)
    ax2.set_title("Top 10 Assets by Transaction Count", pad=15)
    ax2.set_xlabel("Number of Transactions")
    ax2.set_ylabel("")
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x*1e-3:.0f}K"))
    
    plt.suptitle("Asset-Level Trading Activity Analysis", fontsize=22, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_assets.png'))
    plt.close()
    
    # -------------------------------------------------------------
    # Plot 6: Trader Profitability Leaderboard
    # -------------------------------------------------------------
    trader_perf = df.groupby('Account').agg(
        total_pnl=('Closed PnL', 'sum')
    ).sort_values(by='total_pnl', ascending=False).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Top 10 profitable
    top10_prof = trader_perf.head(10).copy()
    top10_prof['Trader_ID'] = top10_prof['Account'].apply(lambda x: x[:6] + "..." + x[-4:])
    sns.barplot(x='total_pnl', y='Trader_ID', data=top10_prof, palette='crest', ax=ax1, hue='Trader_ID', legend=False)
    ax1.set_title("Top 10 Most Profitable Traders", pad=15)
    ax1.set_xlabel("Total Closed PnL ($)")
    ax1.set_ylabel("Trader Address (Masked)")
    ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x*1e-3:.0f}K"))
    
    # Top 5 losing
    top5_loss = trader_perf.tail(5).copy().iloc[::-1]
    top5_loss['Trader_ID'] = top5_loss['Account'].apply(lambda x: x[:6] + "..." + x[-4:])
    sns.barplot(x='total_pnl', y='Trader_ID', data=top5_loss, palette='flare', ax=ax2, hue='Trader_ID', legend=False)
    ax2.set_title("Top 5 Least Profitable Traders (Largest Losses)", pad=15)
    ax2.set_xlabel("Total Closed PnL ($)")
    ax2.set_ylabel("")
    ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x*1e-3:.0f}K"))
    
    plt.suptitle("Trader Profitability Leaderboards", fontsize=22, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_traders.png'))
    plt.close()
    
    # -------------------------------------------------------------
    # Plot 7: Daily Pearson vs Spearman Correlation Matrix Heatmaps
    # -------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
    mask = np.triu(np.ones_like(daily_corr_pearson, dtype=bool))
    
    rename_dict = {
        'avg_fg_value': 'Fear & Greed Index',
        'total_pnl': 'Closed PnL',
        'total_volume': 'Trading Volume',
        'trade_count': 'Transaction Count',
        'avg_trade_size': 'Avg Trade Size',
        'total_fees': 'Trading Fees'
    }
    
    pearson_renamed = daily_corr_pearson.rename(index=rename_dict, columns=rename_dict)
    spearman_renamed = daily_corr_spearman.rename(index=rename_dict, columns=rename_dict)
    
    sns.heatmap(
        pearson_renamed, 
        mask=mask, 
        cmap='coolwarm', 
        vmax=1.0, 
        vmin=-1.0, 
        center=0,
        square=True, 
        linewidths=.5, 
        cbar_kws={"shrink": .8},
        annot=True,
        fmt=".2f",
        ax=ax1
    )
    ax1.set_title("Pearson Correlation (Linear)", pad=15)
    
    sns.heatmap(
        spearman_renamed, 
        mask=mask, 
        cmap='coolwarm', 
        vmax=1.0, 
        vmin=-1.0, 
        center=0,
        square=True, 
        linewidths=.5, 
        cbar_kws={"shrink": .8},
        annot=True,
        fmt=".2f",
        ax=ax2
    )
    ax2.set_title("Spearman Rank Correlation (Non-linear)", pad=15)
    
    plt.suptitle("Daily Aggregated Trading Variables Correlation Heatmaps", fontsize=22, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()
    
    logger.info("All visualizations generated.")

def main():
    logger.info("Starting market sentiment and trading analysis pipeline.")
    
    hist_path = "historical_data.csv"
    fg_path = "fear_greed_index.csv"
    
    if not os.path.exists(hist_path) or not os.path.exists(fg_path):
        logger.error("Required CSV files are missing. Please place them in the working directory.")
        return
        
    df_hist, df_fg = load_data(hist_path, fg_path)
    df_hist_clean, df_fg_clean = clean_data(df_hist, df_fg)
    df = merge_datasets(df_hist_clean, df_fg_clean)
    
    # Run analysis steps
    sentiment_perf = run_pnl_analysis(df)
    ls_perf = run_long_vs_short_analysis(df)
    asset_perf = run_asset_analysis(df)
    trader_perf = run_trader_analysis(df)
    daily_stats, daily_corr_p, daily_corr_s, ind_corr_p, ind_corr_s = run_correlation_analysis(df)
    
    # Generate figures
    generate_visualizations(df, daily_stats, daily_corr_p, daily_corr_s)
    
    logger.info("Pipeline completed.")

if __name__ == '__main__':
    main()
