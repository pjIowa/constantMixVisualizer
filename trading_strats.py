import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

class Portfolio:
	def __init__(self, prices, mm_rates, dates):
		self.W = []
		self.cumulative_tc = []
		self.purchases = []
		self.sales = []
		self.ttc = 0.
		self.peak = 0.
		self.md = 0.
		self.initW = 10**6
		self.unit_c = .005
		self.prices = prices
		self.N = len(dates)
		self.dates = dates
		self.mm_rates = mm_rates

	def run(self):
		num_assets = Portfolio.num_s+1
		pi = np.full(Portfolio.num_s, 1./num_assets)
		theta_n_prev = np.zeros(Portfolio.num_s)
		mm_balance = self.initW
		for i in range(self.N):
			p_n = self.prices[:,i]
			if i == 0:
				w_n_prev =  self.initW
			else:
				day_gap = (self.dates[i]-self.dates[i-1])/np.timedelta64(1,'D')
				mm_rate_prev = self.mm_rates[i-int(day_gap)]
				mm_interest_rate = (1.+mm_rate_prev)**day_gap
				mm_balance = mm_balance*mm_interest_rate
				w_n_prev =  np.sum(theta_n_prev*p_n)+mm_balance
			theta_n = w_n_prev*pi/p_n
			delta_shares = theta_n - theta_n_prev
			shares_bought = np.where(delta_shares<0, 0, delta_shares) 
			shares_sold = np.where(delta_shares>0, 0, delta_shares) 
			self.purchases.append(np.sum(shares_bought*p_n))
			self.sales.append(np.sum(-1.*shares_sold*p_n))
			transact_cost = np.sum(np.abs(delta_shares))*self.unit_c
			w_n_shares = np.sum(theta_n*p_n)
			mm_balance = w_n_prev-w_n_shares-transact_cost
			self.ttc += transact_cost
			if len(self.cumulative_tc) == 0:
				self.cumulative_tc.append(transact_cost)
			else:
				self.cumulative_tc.append(self.cumulative_tc[-1]+transact_cost)
			self.add_wealth(mm_balance+w_n_shares)
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
		annual_mean = ((daily_mean+1.)**Portfolio.tN)-1.
		annnual_variance = ((np.var(daily_return)
			+(daily_mean+1.)**2)**Portfolio.tN)
		-((daily_mean+1.)**(2*Portfolio.tN))
		return annual_mean/np.sqrt(annnual_variance)

	def get_annualized_return(self):
		daily_return = np.diff(self.W)/self.W[-1]
		daily_mean = np.mean(daily_return)
		return ((daily_mean+1.)**Portfolio.tN)-1.

	def get_turnover(self):
		start_ind = range(0, self.N, Portfolio.tN)

		purchase_chunks = (self.purchases[i:i+Portfolio.tN] for i in start_ind)
		purchase_sums = []
		for chunk in purchase_chunks:
			purchase_sums.append(np.sum(chunk))
		sale_chunks = (self.sales[i:i+Portfolio.tN] for i in start_ind)
		sale_sums = []
		for chunk in sale_chunks:
			sale_sums.append(np.sum(chunk))

		wealth_chunks = (self.W[i:i+Portfolio.tN] for i in start_ind)
		wealth_avgs = []
		for chunk in wealth_chunks:
			wealth_avgs.append(np.mean(chunk))

		# larger of purchases or sales over year / average net assets over year
		# averaged over trading years
		turnovers = [np.maximum(p,s)/w for p,s,w in zip(purchase_sums,sale_sums,wealth_avgs)]
		return np.mean(turnovers)

	def print_stats(self):
		print(f"Turnover: {self.get_turnover()*100.0:.3f} %")
		print(f"Annualized rate of return: {self.get_annualized_return()*100.0:.3f} %")
		print(f"Expense ratio: {self.ttc/self.W[-1]*100.0:.3f} %")
		print(f"Max drawdown: {self.md:.3f} %")
		print(f"Sharpe ratio: {self.get_sharpe_ratio():.3f}")

	def plot(self):
		fig, axs = plt.subplots(2)
		axs[0].plot(self.dates, np.array(self.W)/self.initW*100.0)
		axs[1].plot(self.dates, np.array(self.cumulative_tc))
		axs[0].set_title('Wealth, % of Initial')
		axs[1].set_title('Transactions, $')
		plt.subplots_adjust(hspace = .4)
		plt.show()

# Adjusted close downloaded from June 25, 2000 to June 26, 2020 inclusive of 3 stocks using data from Yahoo Finance
MSFT=pd.read_csv('MSFT.csv')["Adj Close"].to_numpy()
CSCO=pd.read_csv('CSCO.csv')["Adj Close"].to_numpy()
GE=pd.read_csv('GE.csv')["Adj Close"].to_numpy()
prices = np.vstack((MSFT, CSCO, GE))
t_dates = pd.to_datetime(pd.read_csv('GE.csv')["Date"]).to_numpy()

# get indices of each trade date from treasury 3mo dates array
treasury_3mo = pd.read_csv('DGS3MO.csv')
treasury_3mo_dates = pd.to_datetime(treasury_3mo["DATE"]).to_numpy()
indices = []
last_elem = 0.
for t_date in t_dates:
	if t_date in treasury_3mo_dates:
		last_elem = np.where(treasury_3mo_dates==t_date)[0][0]
	indices.append(last_elem)

# get the 3mo rates for the subset indices
raw_3mo_rates=pd.to_numeric(treasury_3mo["Rate"]).to_numpy()
treasury_rates = raw_3mo_rates[np.array(indices)]

# use same-day 3mo treasury rate to approximate daily MM rate
mm_rates = (1.+treasury_rates/100.0)**(1./360.)-1.

N = len(prices[0])
Portfolio.num_s = len(prices)
trading_days_in_year = 252
Portfolio.tN = trading_days_in_year

print("All 20 years")
full_portfolio = Portfolio(prices, mm_rates, t_dates)
full_portfolio.run()
full_portfolio.print_stats()
print()

highest_start_index = 0
lowest_start_index = 0
volatile_start_index = 0
stable_start_index = 0

highest_percent_change = 0.
lowest__percent_change = 100000.
highest_variance = 0.
lowest_variance = 100000.

for i in range(0, N-trading_days_in_year):
	full_portfolio_start = np.mean(prices[:,i], axis=0)
	full_portfolio_end = np.mean(prices[:,i+trading_days_in_year-1], axis=0) 
	full_portfolio_percent_change = (full_portfolio_end - full_portfolio_start)/full_portfolio_start

	if full_portfolio_percent_change > highest_percent_change:
		highest_start_index = i
		highest_percent_change = full_portfolio_percent_change
	if full_portfolio_percent_change < lowest__percent_change:
		lowest_start_index = i
		lowest__percent_change = full_portfolio_percent_change

	returns_cov = np.cov(np.diff(prices[:,i:i+trading_days_in_year]))
	full_portfolio_variance = (np.trace(returns_cov)+2.*np.sum(np.triu(returns_cov))+2.*np.sum(np.tril(returns_cov)))/9.
	if full_portfolio_variance > highest_variance:
		highest_variance = full_portfolio_variance
		volatile_start_index = i
	if full_portfolio_variance < lowest_variance:
		lowest_variance = full_portfolio_variance
		stable_start_index = i

print("Most volatile year")
v_range = range(volatile_start_index,volatile_start_index+trading_days_in_year)
volatile_prices = prices[:,v_range]
volatile_dates = t_dates[v_range]
volatile_mm = mm_rates[v_range]
volatile_portfolio = Portfolio(volatile_prices, volatile_mm, volatile_dates)
volatile_portfolio.run()
volatile_portfolio.print_stats()
print()

print("Least volatile year")
s_range = range(stable_start_index,stable_start_index+trading_days_in_year)
stable_prices = prices[:,s_range]
stable_dates = t_dates[s_range]
stable_mm = mm_rates[s_range]
stable_portfolio = Portfolio(stable_prices, stable_mm, stable_dates)
stable_portfolio.run()
stable_portfolio.print_stats()
print()

print("Best year")
h_range = range(highest_start_index,highest_start_index+trading_days_in_year)
highest_prices = prices[:,h_range]
highest_dates = t_dates[h_range]
highest_mm = mm_rates[h_range]
highest_portfolio = Portfolio(highest_prices, highest_mm, highest_dates)
highest_portfolio.run()
highest_portfolio.print_stats()
print()

print("Worst year")
l_range = range(lowest_start_index,lowest_start_index+trading_days_in_year)
lowest_prices = prices[:,l_range]
lowest_dates = t_dates[l_range]
lowest_mm = mm_rates[l_range]
lowest_portfolio = Portfolio(lowest_prices, lowest_mm, lowest_dates)
lowest_portfolio.run()
lowest_portfolio.print_stats()

full_portfolio.plot()
volatile_portfolio.plot()
stable_portfolio.plot()
highest_portfolio.plot()
lowest_portfolio.plot()