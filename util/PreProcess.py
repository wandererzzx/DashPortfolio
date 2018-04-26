import numpy as np
import pandas as pd 
import quandl

global key
key = 'MD5vrwzxyZbgJUcxdogL'

quandl.ApiConfig.api_key = key

def pri_pct_load(tickers=['AMZN', 'GOOGL'],start_date='2012-01-01',end_date='2016-12-31'):
	# get adjusted close price
	price_data = [(ticker, quandl.get('WIKI/'+ticker, 
                                    start_date=start_date, 
                                    end_date=end_date)['Adj. Close']) 
					for ticker in tickers]
	price_df = pd.DataFrame(data=dict(price_data))
	
	# get realized return computed by adjusted close price
	pct_df = price_df.pct_change()
	pct_df[["USDOLLAR"]] = quandl.get('FRED/DTB3', start_date=start_date, end_date=end_date)/(250*100)

	pct_df = pct_df.fillna(method='ffill').iloc[1:]

	return price_df,pct_df


def re_ri_estimate(pct_df):
	# using rolling average as the estimate of return as risk 
	# (past one year mean return as the return estimate of present day)
	r_hat = pct_df.rolling(window=250,min_periods=250).mean().shift(1).dropna()
	#Sigma_hat = pct_df.rolling(window=250, min_periods=250, closed='neither').cov().dropna()
	Sigma_hat = pct_df.rolling(window=250,min_periods=250,closed='neither').cov().unstack().shift(1).stack().dropna()
	
	return r_hat,Sigma_hat
