import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

class Portfolio:
	def __init__(self, initW):
		self.W = []
		self.ttc = 0.
		self.peak = 0.
		self.md = 0.
		self.initW = initW

	def add_wealth(self, new_W):
		if new_W > self.peak:
			self.peak = new_W
		drawdown = 100.*(self.peak - new_W)/self.peak
		if drawdown > self.md:
			self.md = drawdown
		# stored wealths are scaled to % of initial wealth to allow for easier interpretation
		self.W.append(new_W/self.initW*100.0)

	def get_sharpe_ratio(self):
		daily_return = np.diff(self.W)/self.W[:-1]
		daily_mean = np.mean(daily_return)
		N = 252
		annual_mean = ((daily_mean+1.)**N)-1.
		annnual_variance = ((np.var(daily_return)+(daily_mean+1.)**2)**N)-((daily_mean+1.)**(2*N))
		return annual_mean/np.sqrt(annnual_variance)

	def to_string(self):
		print(f"Total transaction cost:\t{self.ttc}")
		print(f"Max drawdown:\t\t{self.md}")
		print(f"Sharpe ratio:\t\t{self.get_sharpe_ratio()}")

# Adjusted close downloaded from June 25, 2000 to June 26, 2020 inclusive of 3 stocks using data from Yahoo Finance
MSFT=pd.read_csv('MSFT.csv')["Adj Close"].to_numpy()
CSCO=pd.read_csv('CSCO.csv')["Adj Close"].to_numpy()
GE=pd.read_csv('GE.csv')["Adj Close"].to_numpy()
prices = np.vstack((MSFT, CSCO, GE))

N = len(prices[0])
initial_wealth = 10**6
cost_per_unit = 0.005
num_stocks = len(prices)
num_assets = num_stocks+1.
pi = np.full(num_stocks, 1./num_assets)

theta_n_prev = np.zeros(num_stocks)
mm_balance = initial_wealth
portfolio = Portfolio(initial_wealth)
for i in range(N):
	p_n = prices[:,i]
	if i == 0:
		w_n_prev =  initial_wealth
	else:
		w_n_prev =  np.sum(theta_n_prev*p_n)+mm_balance
	theta_n = w_n_prev*pi/p_n
	transact_cost = np.sum(np.abs(theta_n_prev - theta_n))*cost_per_unit
	w_shares = np.sum(theta_n*p_n)
	mm_balance = w_n_prev-w_shares- transact_cost
	portfolio.ttc += transact_cost
	portfolio.add_wealth(mm_balance+w_shares)
	theta_n_prev = theta_n
portfolio.to_string()

plt.plot(portfolio.W)
plt.xlabel('Days since 6-26-00')
plt.ylabel('Wealth, $')
plt.show()