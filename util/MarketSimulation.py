import numpy as np
import pandas as pd

import cvxportfolio as cp


def backTest(Problem,init_portfolio,market_returns,start_time='2013-01-03',end_time='2016-12-31'):
	# backtest for the different problem policy
	market_sim = cp.MarketSimulator(yc_market_returns = market_returns, 
									costs = [Problem.tcost,Problem.hcost], cash_key='USDOLLAR') 
	
	# result get from spo policy 
	result = market_sim.run_backtest(init_portfolio,
                               start_time=start_time, end_time=end_time,  
                               policy=Problem.policy)

	return result