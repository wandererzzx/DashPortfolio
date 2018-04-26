import numpy as np
import pandas as pd 
import quandl

import cvxportfolio as cp

global key
key = 'MD5vrwzxyZbgJUcxdogL'

quandl.ApiConfig.api_key = key

def pri_pct_load(tickers=['AMZN', 'GOOGL'],start_date='2015-01-01',end_date='2016-12-31'):
	# get adjusted close price
	price_data = [(ticker, quandl.get('WIKI/'+ticker, 
                                    start_date=start_date, 
                                    end_date=end_date)['Adj. Close']) 
					for ticker in tickers]
	price_df = pd.DataFrame(data=dict(price_data))
	
	# get realized return computed by adjusted close price
	pct_data = [(ticker, quandl.get('WIKI/'+ticker, 
                                    start_date=start_date, 
                                    end_date=end_date)['Adj. Close'].pct_change()) 
					for ticker in tickers]

	pct_df = pd.DataFrame(data=dict(pct_data))
	pct_df[["USDOLLAR"]] = quandl.get('FRED/DTB3', start_date=start_date, end_date=end_date)/(250*100)

	pct_df = pct_df.fillna(method='ffill').iloc[1:]

	return price_df,pct_df

