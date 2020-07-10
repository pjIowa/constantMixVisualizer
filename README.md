# Constant Mix Visualizer

This visualizer shows the performance of a constant mix portfolio for 3 stocks over the past 20 years and subset ranges. The strategy maintains equal wealth for stocks and the money market balance ($1:MSFT, $1:GE, $1:CISCO, $1:MM) and rebalances daily. The adjusted close price is used for each stock. The specific time range is 6/26/2000 - 6/25/2020 inclusive. Initial Wealth is $1M. The cost to trade is a flat $0.005 per share. And money market return is 0%

### Full 20 years
![Full 20](images/full_20.png) 

#### Statistics

Turnover: 85.674 %

Annualized mean return: 2.242 %

Expense ratio: 0.497 %

Max drawdown: 54.770 %

Sharpe ratio: 0.191

### Most volatile year
![Most Volatile](images/most_volatile.png) 

#### Statistics

Turnover: 187.199 %

Annualized rate of return: -0.821 %

Expense ratio: 0.085 %

Max drawdown: 29.340 %

Sharpe ratio: -0.028

### Least volatile year
![Least Volatile](images/least_volatile.png) 

#### Statistics

Turnover: 122.973 %

Annualized rate of return: 2.659 %

Expense ratio: 0.050 %

Max drawdown: 6.713 %

Sharpe ratio: 0.287

### Best year
![Best Year](images/best_year.png) 

#### Statistics

Turnover: 129.866 %

Annualized rate of return: 53.207 %

Expense ratio: 0.088 %

Max drawdown: 8.317 %

Sharpe ratio: 2.040

### Worst year
![Worst Year](images/worst_year.png) 

#### Statistics

Turnover: 284.685 %

Annualized rate of return: -50.142 %

Expense ratio: 0.145 %

Max drawdown: 41.217 %

Sharpe ratio: -1.899

#### Definitions
[Turnover](https://www.investopedia.com/terms/a/annual-turnover.asp)

TODO Annualized mean return formula in Latex

TODO Annualized variance formula in Latex

Expense ratio = Cumulative transaction costs / Final wealth

[Drawdown](https://en.wikipedia.org/wiki/Drawdown_(economics))

Sharpe Ratio  = Annualized Mean / sqrt(Annualized Variance)
