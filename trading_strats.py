import pandas as pd
import numpy as np
# from matplotlib import pyplot as plt

class portfolio:
	def __init__(self, initW, num_stocks, cost_per_unit, prices, num_points):
		self.W = []
		self.ttc = 0.
		self.peak = 0.
		self.md = 0.
		self.initW = initW
		self.num_s = num_stocks
		self.unit_c = cost_per_unit
		self.prices = prices
		self.N = num_points

	def run(self):
		num_assets = self.num_s+1
		pi = np.full(self.num_s, 1./num_assets)
		theta_n_prev = np.zeros(self.num_s)
		mm_balance = self.initW
		for i in range(self.N):
			p_n = self.prices[:,i]
			if i == 0:
				w_n_prev =  self.initW
			else:
				w_n_prev =  np.sum(theta_n_prev*p_n)+mm_balance
			theta_n = w_n_prev*pi/p_n
			transact_cost = np.sum(np.abs(theta_n_prev - theta_n))*self.unit_c
			w_shares = np.sum(theta_n*p_n)
			mm_balance = w_n_prev-w_shares- transact_cost
			self.ttc += transact_cost
			self.add_wealth(mm_balance+w_shares)
			theta_n_prev = theta_n

	def add_wealth(self, new_W):
		if new_W > self.peak:
			self.peak = new_W
		drawdown = 100.*(self.peak - new_W)/self.peak
		if drawdown > self.md:
			self.md = drawdown
		self.W.append(new_W)

	def get_sharpe_ratio(self):
		daily_return = np.diff(self.W)/self.W[-1]
		daily_mean = np.mean(daily_return)
		N = 252
		annual_mean = ((daily_mean+1.)**N)-1.
		annnual_variance = ((np.var(daily_return)+(daily_mean+1.)**2)**N)-((daily_mean+1.)**(2*N))
		return annual_mean/np.sqrt(annnual_variance)

	def get_annualized_return(self):
		daily_return = np.diff(self.W)/self.W[-1]
		daily_mean = np.mean(daily_return)
		N = 252
		return ((daily_mean+1.)**N)-1.

	def to_string(self):
		print(f"Annualized % gain:\t\t{self.get_annualized_return()*100.0}")
		wealth_change = self.W[-1]-self.W[0]
		print(f"Transactions as % of gain:\t{self.ttc/wealth_change*100.0}")
		print(f"Max drawdown:\t\t\t{self.md}")
		print(f"Sharpe ratio:\t\t\t{self.get_sharpe_ratio()}")

# Adjusted close downloaded from June 25, 2000 to June 26, 2020 inclusive of 3 stocks using data from Yahoo Finance
MSFT=pd.read_csv('MSFT.csv')["Adj Close"].to_numpy()
CSCO=pd.read_csv('CSCO.csv')["Adj Close"].to_numpy()
GE=pd.read_csv('GE.csv')["Adj Close"].to_numpy()
prices = np.vstack((MSFT, CSCO, GE))

N = len(prices[0])
initial_wealth = 10**6
cost_per_unit = 0.005
num_stocks = len(prices)

print("Full 20 years")
full_portfolio = portfolio(initial_wealth, num_stocks, cost_per_unit, prices, N)
full_portfolio.run()
full_portfolio.to_string()
print()

highest_start_index = 0
lowest_start_index = 0
volatile_start_index = 0
stable_start_index = 0

highest_percent_change = 0.
lowest__percent_change = 100000.
highest_variance = 0.
lowest_variance = 100000.

trading_days = 252
for i in range(0, N-trading_days):
	full_portfolio_start = np.mean(prices[:,i], axis=0)
	full_portfolio_end = np.mean(prices[:,i+trading_days-1], axis=0) 
	full_portfolio_percent_change = (full_portfolio_end - full_portfolio_start)/full_portfolio_start

	if full_portfolio_percent_change > highest_percent_change:
		highest_start_index = i
		highest_percent_change = full_portfolio_percent_change
	if full_portfolio_percent_change < lowest__percent_change:
		lowest_start_index = i
		lowest__percent_change = full_portfolio_percent_change

	returns_cov = np.cov(np.diff(prices[:,i:i+trading_days]))
	full_portfolio_variance = (np.trace(returns_cov)+2.*np.sum(np.triu(returns_cov))+2.*np.sum(np.tril(returns_cov)))/9.
	if full_portfolio_variance > highest_variance:
		highest_variance = full_portfolio_variance
		volatile_start_index = i
	if full_portfolio_variance < lowest_variance:
		lowest_variance = full_portfolio_variance
		stable_start_index = i

print("Most volatile year")
volatile_prices_range = prices[:,volatile_start_index:volatile_start_index+trading_days]
volatile_portfolio = portfolio(initial_wealth, num_stocks, cost_per_unit, volatile_prices_range, trading_days)
volatile_portfolio.run()
volatile_portfolio.to_string()
print()

print("Least volatile year")
stable_prices_range = prices[:,stable_start_index:stable_start_index+trading_days]
stable_portfolio = portfolio(initial_wealth, num_stocks, cost_per_unit, stable_prices_range, trading_days)
stable_portfolio.run()
stable_portfolio.to_string()
print()

print("Best year")
highest_prices_range = prices[:,highest_start_index:highest_start_index+trading_days]
highest_portfolio = portfolio(initial_wealth, num_stocks, cost_per_unit, highest_prices_range, trading_days)
highest_portfolio.run()
highest_portfolio.to_string()
print()

print("Worst year")
lowest_prices_range = prices[:,lowest_start_index:lowest_start_index+trading_days]
lowest_portfolio = portfolio(initial_wealth, num_stocks, cost_per_unit, lowest_prices_range, trading_days)
lowest_portfolio.run()
lowest_portfolio.to_string()
print()

# plt.plot(full_portfolio.W)
# plt.xlabel('Days since 6-26-00')
# plt.ylabel('Wealth, $')
# plt.show()