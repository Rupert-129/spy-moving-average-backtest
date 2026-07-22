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
 










