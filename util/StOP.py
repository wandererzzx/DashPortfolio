import numpy as np
import pandas as pd
import cvxportfolio as cp

class SPO_Problem(object):
	"""class for defining Single Period Optimization problem"""
	def __init__(self,tcost,hcost,risk,gamma_trade=1.0,gamma_hold=1.0,gamma_risk=5.0):
		self.tcost = tcost 
		self.gamma_trade = gamma_trade

		self.hcost = hcost 
		self.gamma_hold = gamma_hold

		self.risk = risk
		self.gamma_risk = gamma_risk

	# return constraints definition as a dict
	def constraints(self,**kwargs):
		self.constraints = dict()
		if kwargs is not None:
			for key,value in kwargs.items():
				self.constraints[key] = value

		return self.constraints


	def solve(self,return_forecast,solver = None):
		costs = [self.risk*self.gamma_risk,self.tcost*self.gamma_trade,self.hcost*self.gamma_hold]
		constraints = list(self.constraints.values())

		self.policy = cp.SinglePeriodOpt(return_forecast = return_forecast, 
                                		 costs = costs,
                                		 constraints = constraints,
                                		 solver = solver)
		return self.policy




class MPO_Problem(SPO_Problem):
	"""class for defining Multiple Period Optimization problem"""
	def __init__(self, trading_times,lookahead_periods=2,terminal_weights=None,*args, **kwargs):
		
		self.trading_times = trading_times
		self.lookahead_periods = lookahead_periods
		self.terminal_weights = terminal_weights

		super(MPO_Problem, self).__init__(*args, **kwargs)
		
	def solve(self,return_forecast,solver = None):
		costs = [self.risk*self.gamma_risk,self.tcost*self.gamma_trade,self.hcost*self.gamma_hold]
		constraints = list(self.constraints.values())

		self.policy = cp.MultiPeriodOpt(return_forecast = return_forecast,
										costs = costs,
										constraints = constraints,
										solver = solver,
										trading_times = self.trading_times,
										lookahead_periods = self.lookahead_periods,
										terminal_weights = self.terminal_weights)
		return self.policy