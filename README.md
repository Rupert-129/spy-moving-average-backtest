# spy-moving-average-backtest
A Python backtest of a 20/100-day moving-average crossover strategy on SPY, including transaction costs and benchmark performance analysis.

## OVERVIEW
I have built a backtester to see if I could in some way beat simply just buying holding an asset for years. The Ticker I used as my test subject 
is the SPY (a tracker of the S&P500), and to produce my signals I compared 20 and 100 day moving averages. The metrics I primarily compared were,
total return, Sharpe ratio, CAGR, volatility and drawdown. 

## STRATEGY
The strategy uses 20 day and 100 day simple moving averages. These periods represent roughly 1 month of trading time and 5 months of trading activity 
respectively. I selected these timeframes to balance noise reduction and responsiveness. Shorter time frames yielded noisier and variable moving
averages whereas longer time frames gave a moving average that was slower to respond to moves in the market. The values I have chosen are intended to 
give smooth and responsive moving averages that give valid results when used. however, these values are not assumed to be optimal. 

The strategy I have chosen is a long-only trend-following strategy. If the 20-day average moves above the 100-day average, a signal is produced and the 
backtester entersa  long position. It then stays in the position until the 20-day moving average goes below the 100-day average in which case, it 
leaves the position and holds its cash until another signal. 

It is worth mentioning that if a signal is produced on day t, then the backtester will only enter the position on day t + 1. This is intentional
and avoids look-ahead bias. 

## DATA AND ASSUMPTIONS
### DATA
The dataset I decided to use was SPY, This is an ETF tracking the S&P 500 that is present on Yahoo finance. To import the data I used yfinance.
I tested over a period of 6 years worth of daily trading data, specifically the closing price, making sure to adjust for dividends and stock splits.
I was under the impression that the data was already clean but just to make sure I created a function that sorts entries into chronological order, 
removes duplicate values and removes missing entries. The benchmark for the backtester was a continuously invested buy-and-hold position in SPY.
To generate the first part of the 100 day moving average I have added a warmup period at the beginning of the backtest to ensure the results are
fair. 
### ASSUMPTIONS
The strategy is long only and when invested the backtester allocates 100% of its cash into SPY. This is also true for the inverse case where it will
hold 100% of its cash when not invested. The cash does not accrue interest and returns are always reinvested and compounded. A 5 basis point transaction
cost is taken at every entry and exit. Slippage and bid-ask spread is not modelled. Orders are assumed to be filled at the required price. A signal that 
is generated on day t dictates exposure over the next close-to-close return interval. We are not using leverage for this strategy. When calculating 
Sharpe ratios we assume a risk-free rate of 0 and that there are 252 trading days in a year. Taxes are not considered. 

 










