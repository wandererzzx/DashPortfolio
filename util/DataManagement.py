import pandas as pd
from datetime import datetime as dt
import colorlover as cl
import quandl
import plotly.graph_objs as go
import plotly.figure_factory as ff

global key
key = 'MD5vrwzxyZbgJUcxdogL'
quandl.ApiConfig.api_key = key

colorscale = cl.scales['9']['qual']['Paired']

def getData(stock,start_date,end_date):
	price_df = quandl.get('WIKI/'+stock,start_date=start_date,end_date=end_date)
	return price_df

def getCandle(stock,price_df):
	price_df = price_df.reset_index()
	candlestick = {
		'x':price_df['index'],
		'open':price_df['Open'],
		'high':price_df['High'],
		'low':price_df['Low'],
		'close':price_df['Close'],
		'type':'candlestick',
		'name':stock,
		'legendgroup':stock,
		'increasing': {'line': {'color': colorscale[0]}},
		'decreasing': {'line': {'color': colorscale[1]}}

	}
	return candlestick



def getBollinger(stock,price_df,window_size=10, num_of_std=5):
	price_df = price_df.reset_index()
	price = price_df.Close
	rolling_mean = price.rolling(window=window_size).mean()
	rolling_std  = price.rolling(window=window_size).std()
	upper_band = rolling_mean + (rolling_std*num_of_std)
	lower_band = rolling_mean - (rolling_std*num_of_std)

	bbands = (rolling_mean, upper_band, lower_band)

	bollinger_traces = [{
		'x': price_df['index'], 'y': y,
		'type': 'scatter', 'mode': 'lines',
		'line': {'width': 1, 'color': colorscale[(i*2) % len(colorscale)]},
		'hoverinfo': 'none',
		'legendgroup': stock,
		'showlegend': True if i == 0 else False,
		'name': '{} - bollinger bands'.format(stock)
	} for i, y in enumerate(bbands)]

	return bollinger_traces

def getScatter(stock,price_df):
	price_df = price_df.reset_index()
	scatter = go.Scatter(
		x = price_df['index'], y = price_df['Adj. Close'],
		mode = 'lines+markers',
		name = '{} - adjusted close price'.format(stock),
		marker = go.Marker(color = '#e89f7d')
	)

	return scatter

def getPct(stock,price_df):
	pct_df = price_df.pct_change().fillna(method='ffill').iloc[1:]
	pct_df = pct_df.reset_index()
	pct = go.Scatter(
		x = pct_df['index'], y = pct_df['Adj. Close'],
		mode = 'lines+markers',
		name = '{} - price percentage change'.format(stock),
		marker = go.Marker(color = 'rgb(26, 118, 255)')

	)
	return pct


def getPctDis(stock,price_df):
	pct_df = price_df.pct_change().fillna(method='ffill').iloc[1:]
	pct_df = pct_df.reset_index()

	hist_data = go.Histogram(
			y = pct_df['Adj. Close'],
			name = '{} - pct-hist'.format(stock),
			marker = dict(color='#efa7d8'),
			opacity=0.75
		)
	# group_labels = ['price percentage change distribution']
	# fig = ff.create_distplot(hist_data,group_labels)
	return hist_data