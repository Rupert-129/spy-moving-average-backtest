import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np


def load_data(ticker):
    """Download historical price data for a ticker using yfinance."""
    
    raw_prices = yf.download(
        ticker,
        start = "2020-01-01",
        auto_adjust = True,
        multi_level_index = False,
        progress = False
    )
    
    if raw_prices.empty:
        raise RuntimeError("The file has not downloaded properly")
    
    return raw_prices


def inspect_and_clean(raw_prices):
    """
    Inspect the downloaded dataset, sort it by date, remove duplicate
    dates, and drop rows with missing closing prices.
    """
    
    print("First 5 rows:")
    print(raw_prices.head())

    print("\nColumn names:")
    print(raw_prices.columns)

    print("\nDataset info:")
    raw_prices.info()
    
    prices = raw_prices.copy()
    
    prices = prices.sort_index()
    # ^ ensures data is in order
    prices = prices[~prices.index.duplicated(keep = "first")]
    # ^ removes duplicate dates
    prices = prices.dropna(subset = ["Close"])
    # ^ removes rows where there is no closing price
    print("\nMissing values after cleaning")
    print(prices.isna().sum())
    
    if "Close" not in prices.columns:
        raise KeyError("Expected a 'Close' column but none was found")
    
    return prices

 
def daily_return(prices):
    """
    Calculate daily percentage returns and remove the initial row
    where no return can be calculated.
    """
   
    prices["Daily Return"] = prices["Close"].pct_change()
    
    prices = prices.dropna(subset = ["Daily Return"])
    
    print(prices[["Close", "Daily Return"]].head())
    
    return prices


def averages_and_signal(prices):
    """
    Calculate the 20-day and 100-day moving averages and generate
    a long-only trading signal.
    """
    
    prices["20 Day Average"] = (
        prices["Close"].rolling(window = 20).mean()
        )
    
    prices["100 Day Average"] = (
        prices["Close"].rolling(window = 100).mean()
        )
    
    prices["Signal"] = (
        prices["20 Day Average"] > prices["100 Day Average"]
        ).astype(int)
    
    #shift signal 1 day ahead to prevent look-ahead-bias
    prices["Position"] = prices["Signal"].shift(1)
    
    return prices


def strat_return_and_growth(prices, transaction_cost = 0.0005):
    """
    Calculate strategy returns after transaction costs and construct
    cumulative growth series for the strategy and buy-and-hold market.
    """
    
    prices["Trade"] = prices["Position"].diff().fillna(0)
         
    entries = (prices["Trade"] == 1).sum()
    exits = (prices["Trade"] == -1).sum()

    # counting entries and exits
    print("\nEntries:", entries)
    print("Exits:", exits)
    
    prices["Strategy Return"] = (
        prices["Position"] * prices["Daily Return"]
        - prices["Trade"].abs() *transaction_cost
    )
    
    prices["Market Growth"] = (
        1 + prices["Daily Return"].fillna(0)
    ).cumprod()
    
    prices["Strategy Growth"] = (
        1 + prices["Strategy Return"].fillna(0)
    ).cumprod()
    
    print(prices[["Daily Return", "Position", "Strategy Return"]].head())
    
    print("\n", prices[["Strategy Growth", "Market Growth"]].iloc[-1])
    
    return prices


def metrics(prices):
    """
    Calculate and display performance metrics including total return,
    CAGR, volatility, Sharpe ratio, maximum drawdown, exposure,
    trade counts, and daily win rate.
    """
    
    best_day = prices["Daily Return"].idxmax()
    worst_day = prices["Daily Return"].idxmin()

    print("\nBest Day:", best_day)
    print("Return:", prices.loc[best_day, "Daily Return"])

    print("\nWorst Day", worst_day)
    print("Return", prices.loc[worst_day, "Daily Return"])
    
    market_return = (prices["Market Growth"].iloc[-1] - 1) * 100
    strategy_return = (prices["Strategy Growth"].iloc[-1] - 1) * 100
    
    print("\nMarket Return:", market_return, "%")
    print("Strategy Return:", strategy_return, "%")
    
    market_vol = prices["Daily Return"].std() * np.sqrt(252)
    strategy_vol = prices["Strategy Return"].std() * np.sqrt(252)
    
    print("\nMarket Volitility:", market_vol)
    print("Strategy Volitility:", strategy_vol)
    
    market_sharpe = (
        np.sqrt(252) 
        * prices["Daily Return"].mean()
        / prices["Daily Return"].std()
        )
    
    strategy_sharpe = (
        np.sqrt(252)
        * prices["Strategy Return"].mean()
        / prices["Strategy Return"].std()
        )
    
    print("\nMarket Sharpe Ratio", market_sharpe)
    print("Strategy Sharpe Ratio", strategy_sharpe)
    
    years = (prices.index[-1] - prices.index[0]).days / 365.25

    market_cagr = (
         (prices["Market Growth"].iloc[-1]
         / prices["Market Growth"].iloc[0]
         ) ** (1 / years)) - 1 
         
    strategy_cagr = (
        (prices["Strategy Growth"].iloc[-1]
         / prices["Strategy Growth"].iloc[0]
         ) ** (1 / years)) - 1
    
    print("\nMarket CAGR:", (market_cagr * 100), "%")  
    print("Strategy CAGR:", (strategy_cagr * 100), "%")   

    
    prices["Market Drawdown"] = (
        prices["Market Growth"] / prices["Market Growth"].cummax() - 1
        )

    prices["Strategy Drawdown"] =  (
        prices["Strategy Growth"] / prices["Strategy Growth"].cummax() - 1
        )
    
    print("\n", prices[["Strategy Drawdown", "Market Drawdown"]].min())
    
    strategy_exposure = prices["Position"].mean()
    
    print("\nStrategy Exposure:", strategy_exposure * 100, "%")
    
    prices["Trade"] = prices["Position"].diff().fillna(0)
         
    entries = (prices["Trade"] == 1).sum()
    exits = (prices["Trade"] == -1).sum()

    # counting entries and exits
    print("\nEntries:", entries)
    print("Exits:", exits)
    
    trade_returns = []
    entry_price = None
    
    for i in range(len(prices)):
        trade = prices["Trade"].iloc[i]
        
        if trade == 1:
            entry_price = prices["Close"].iloc[i]
            
        elif trade == -1 and entry_price is not None:
            exit_price =prices["Close"].iloc[i]
            
            trade_return = (
                exit_price 
                / entry_price) - 1
            
            trade_returns.append(trade_return)
            
            entry_price = None
    
    trade_returns = pd.Series(trade_returns)
   
    if not trade_returns.empty:
        completed_trades = len(trade_returns)
        average_trade_return = trade_returns.mean()
        highest_trade_return = trade_returns.max()
        lowest_trade_return = trade_returns.min()
        winning_trade_rate = (trade_returns > 0).mean()
    
        print("\nNumber of Trades:", completed_trades)
        print("Average Return From Trades:", average_trade_return * 100, "%")
        print("Highest Trade Return:", highest_trade_return * 100, "%")
        print("Lowest Trade Return:", lowest_trade_return * 100, "%")
        print("Winning Trade Rate:", winning_trade_rate * 100, "%")
    else:
        print("No Trades Were Completed")
    
   
    
    invested_returns = prices.loc[
        prices["Position"] == 1, "Strategy Return"
    ]
    
    all_days_win_rate = (prices["Strategy Return"] > 0).mean()
    invested_win_rate = (invested_returns > 0).mean()
    
    print("\nAll Days Win Rate:", all_days_win_rate * 100, "%")
    print("Invested Win Rate", invested_win_rate * 100, "%")
    
    
    return prices


def graphs(prices):
    """Plot prices, moving averages, daily returns, and equity curves."""
    
    #closing prices
    prices["Close"].plot(figsize = (10, 5))
    plt.title("SPY Closing price")
    plt.xlabel("Date (Yr)")
    plt.ylabel("Price ($)")
    plt.tight_layout()
    plt.show()
    
    #closing prices with moving averages
    prices[["Close", "20 Day Average", "100 Day Average"]
           ].plot(figsize = (10, 5))
    plt.title("SPY with Moving Averages")
    plt.xlabel("Date (Yr)")
    plt.ylabel("Price ($)")
    plt.tight_layout()
    plt.show()
    
    # This is the plot for the daily returns
    prices["Daily Return"].plot(figsize = (10, 5))
    plt.title("Daily Returns")
    plt.xlabel("Date (Yr)")
    plt.ylabel("Daily Return")
    plt.axhline(0)
    plt.tight_layout()
    plt.show()
    
    #strategy growth against market growth
    prices[["Strategy Growth", "Market Growth"]].plot(figsize = (10,5))
    plt.xlabel("Date (Yr)")
    plt.ylabel("Cumulative Growth (Initial Value = 1)")
    plt.tight_layout()
    plt.show()


def main():
    """Run the full backtesting workflow in the correct order."""
    
    raw_prices = load_data("SPY")
    prices = inspect_and_clean(raw_prices)
    prices = daily_return(prices)
    prices = averages_and_signal(prices)
    prices = strat_return_and_growth(prices)
    prices = metrics(prices)
    graphs(prices)
    
#prevents the backtest running if one of its functions is called elsewhere
if __name__ == "__main__":
    main()
    
    


