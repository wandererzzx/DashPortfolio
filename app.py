import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from dateutil import parser
from util import DataManagement as dm

import sys
import os
sys.path.insert(0,os.path.abspath('.'))

from util import PreProcess
from util import StOP
from util import MarketSimulation



import cvxportfolio as cp

app = dash.Dash(__name__)
server = app.server

app.config['suppress_callback_exceptions']=True
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.css.append_css({"external_url": "https://codepen.io/peter-xxxxx/pen/xjEeyW.css"})

dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'


vertical = False

if not vertical:
    app.layout = html.Div([
        dcc.Tabs(
            tabs=[
                {'label': 'Price Data', 'value': 1},
                {'label': 'Simulation', 'value': 2},
            ],
            value=1,
            id='tabs',
            vertical=vertical
        ),
        html.Div(id='tab-content'),
        html.Div(id='data-load',style={'display':'none'})
    ], style={
        'width': '80%',
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto'
    })

else:
    app.layout = html.Div([
    	html.Div(
            'Portfolio Optimization',
            style = {'height':'5vh','text-align': 'center','line-height':'40px'}
        ),
        html.Div([
            dcc.Tabs(
                tabs=[
                    {'label': 'Price Data', 'value': 1},
                    {'label': 'Simulation', 'value': 2},
                ],
                value=1,
                id='tabs',
                vertical=vertical,
                style={
                    'height': '80vh',
                    'borderRight': 'thin lightgrey solid',
                    'textAlign': 'left',
                }
            )],
            style={'width': '20%', 'float': 'left'}
        ),
        html.Div(
            html.Div(id='tab-content'),
            style={'width': '80%', 'float': 'right'}
        )
    ], style={
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto',
    })


tabs_layout = dict()
tabs_layout[1] = [html.Div([
	html.Div(
		dcc.Input(
			id = 'stock-ticker',
			placeholder = "Enter a stock symbol...",
			type = 'text',
			value = 'AMZN',
		),
		style = {'margin-top':'20px','display':'inline-block','float':'left'}
	),
	html.Div(
		dcc.DatePickerRange(
			id = 'date-pick-range',
			start_date = dt(2018,1,1),
			end_date = dt.now(),
			with_portal = True
		),
		style = {'margin-top':'20px','display':'inline-block','float':'right'}
	)],style={'min-height':'50px','overflow':'hidden'}),
	html.Div(id='graphs',style={'margin-top':'20px','height':'50%'}),
	html.Div(
		[html.Div(id='stock-close',style={'float':'left','margin-top':'20px','width':'45%','display':'inline-block'}),
		html.Div([
			html.Div(id='stock-pct',style={'max-width':'100%','max-height':'50%','display':'block'}),
			html.Div(id='stock-pct-dis',style={'max-width':'100%','max-height':'50%','display':'block'})
		],style={'float':'right','margin-top':'20px','width':'50%','display':'inline-block'})],
		style = {'display':'flex'}
	)
]

tabs_layout[2] = [html.Div([
		html.H4('Single Period Optimization'),
		html.Div(
			[html.H6('portfolio selection:',style={'color':'#007eff'}),
			 dcc.Dropdown(
			 	id = 'portfolio',
			 	options = [
			 		{'label':'AMZN','value':'AMZN'},
			 		{'label':'GOOGL','value':'GOOGL'},
			 		{'label':'FB','value':'FB'},
			 		{'label':'NKE','value':'NKE'},
			 		{'label':'TSLA','value':'TSLA'}
			 	],
			 	value = ['AMZN','GOOGL','FB'],
			 	multi = True
			 ),
			 html.H6('return estimation:',style={'color':'#007eff','margin-top':'20px'}),
			 dcc.Dropdown(
			 	id = 'r_hat',
			 	options = [
			 		{'label':'Rolling Average','value': 1},
			 	],
			 	value = 1,
			 	clearable = False
			 ),
			 html.H6('risk model:',style={'color':'#007eff','margin-top':'20px'}),
			 dcc.Dropdown(
			 	id = 'sigma_hat',
			 	options = [
			 		{'label':'Full Volatility','value': 1},
			 	],
			 	value = 1,
			 	clearable = False
			 ),
			 html.H6('transaction cost model:',style={'color':'#007eff','margin-top':'20px'}),
			 html.Div([
			 	html.Div('a',style={'display':'inline-block','float':'left','font-style':'italic','font-size':'23px'}),
		 		dcc.Input(
		 			id = 'half_spread',
		 			placeholder = 'Enter half spread parameter...',
		 			type = 'number',
		 			value = 0.00025,
		 			style = {'display':'inline-block','margin-left':'5','width':'80%'}
		 		),
			 ],style={'display':'inline-block','width':'50%'}),
			 html.Div([
			 	html.Div('b',style={'display':'inline-block','float':'left','font-style':'italic','font-size':'23px'}),
		 		dcc.Input(
		 			id = 'nonlin_coef',
		 			placeholder = 'Enter nonlinear coefficient...',
		 			type = 'number',
		 			value = 1.0,
		 			style = {'display':'inline-block','margin-left':'5','width':'80%'}
		 		),
			 ],style={'display':'inline-block','width':'50%'}),
			 html.H6('holding cost model:',style={'color':'#007eff','margin-top':'20px'}),
			 html.Div([
			 	html.Div('borrow cost',style={'font-style':'italic','font-size':'15px','display':'inline-block','width':'50%'}),
		 		dcc.Input(
		 			id = 'borrow_cost',
		 			placeholder = 'Enter borrow cost...',
		 			type = 'number',
		 			value = 0.0001,
		 			style = {'display':'inline-block','margin-left':'5','width':'40%'}
		 		),
			 ]),
			 html.H6('constraints:',style={'color':'#007eff','margin-top':'20px'}),
			 html.Div([
			 	html.Div('leverage constraint',style={'font-style':'italic','font-size':'15px','display':'inline-block','width':'50%'}),
		 		dcc.Input(
		 			id = 'levecons',
		 			placeholder = 'Enter leverage constraint...',
		 			type = 'number',
		 			value = 3,
		 			style = {'display':'inline-block','margin-left':'5','width':'40%'}
		 		),
			 ]),
			 html.H6('initial portfolio:',style={'color':'#007eff','margin-top':'20px'}),
			 html.Div([
		 		dcc.Input(
		 			id = 'initial_asset',
		 			placeholder = 'Enter initial asset...',
		 			type = 'number',
		 			value = 0,
		 			style = {'display':'inline-block','width':'45%'}
		 		),
		 		dcc.Input(
		 			id = 'initial_cash',
		 			placeholder = 'Enter initial cash...',
		 			type = 'number',
		 			value = 10000,
		 			style = {'display':'inline-block','margin-left':'5','width':'45%'}
		 		),
			 ]),
			 html.H6('simulation period:',style={'color':'#007eff','margin-top':'20px'}),
			 dcc.DatePickerRange(
				id = 'period-pick',
				start_date = dt(2017,1,1),
				end_date = dt.now(),
				with_portal = True
			 ),
			 html.Button('Start Simulation',id = 'button',n_clicks=0,style={'margin-top':'20px','margin-left':'60px'})
			],
		style={'height':'90%','width': '33%','float': 'left','margin-bottom':'20px'}),
		html.Div(id = 'results',style={'height':'100%','width': '66%', 'float': 'right'}),
	],style={'margin-top':'20px'})
]




@app.callback(Output('results','children'),
			[Input('button','n_clicks')],
			[State('portfolio','value'),
			 State('r_hat','value'),
			 State('sigma_hat','value'),
			 State('half_spread','value'),
			 State('nonlin_coef','value'),
			 State('borrow_cost','value'),
			 State('levecons','value'),
			 State('initial_asset','value'),
			 State('initial_cash','value'),
			 State('period-pick','start_date'),
			 State('period-pick','end_date')])
def simulation(n_clicks,portfolio,r_hat,sigma_hat,half_spread,
				nonlin_coef,borrow_cost,levecons,initial_asset,
				initial_cash,start_date,end_date):
	
	if n_clicks < 1:
		pass
	else:
		try:
			start_time = start_date

			start_date = parser.parse(start_date)
			start_date = start_date - relativedelta(years=1)
			start_date = start_date.strftime("%Y-%m-%d")

			print('loading data...')
			_,pct_df = PreProcess.pri_pct_load(portfolio,start_date=start_date,end_date=end_date)

			print('data loaded.')
			if r_hat == 1:
				if sigma_hat == 1:
					r_h,sigma_h = PreProcess.re_ri_estimate(pct_df)

			tcost = cp.TcostModel(half_spread=half_spread)
			hcost = cp.HcostModel(borrow_costs=borrow_cost)
			risk = cp.FullSigma(sigma_h)
			return_forecast = cp.ReturnsForecast(returns = r_h)
			gamma_trade, gamma_hold = 1., 1.
			gamma_risk = 5.
			leverage_limit = cp.LeverageLimit(levecons)
			spo = StOP.SPO_Problem(tcost,hcost,risk,gamma_trade,gamma_hold,gamma_risk)
			spo.constraints(leverage_limit = leverage_limit)
			spo.solve(return_forecast = return_forecast)
			

			end_time = end_date

			init_portfolio = pd.Series(index=pct_df.columns, data=initial_asset)
			init_portfolio.USDOLLAR = initial_cash

			result = MarketSimulation.backTest(spo,init_portfolio,pct_df,
		                                   start_time=start_time,end_time=end_time)
			print('Simulation Finished.')

			value_scatters = [go.Scatter(
							x = result.v.index, y = result.v.values,
							mode = 'lines+markers',
							name = 'values',
							marker = go.Marker(color = '#e21220'))]

			values_graph = dcc.Graph(
				id = 'values',
				figure = go.Figure(
					data = value_scatters,
					layout = go.Layout(
						height = 300,
						showlegend = True,
						margin=go.Margin(l=40, r=0, t=40, b=30),
						legend = go.Legend(x=0,y=1.0)
					)
				)
			)


			weight_scatters = [go.Scatter(
							x = result.w[i].index, y = result.w[i].values,
							mode = 'lines+markers',
							name = i,
							text = i,
							marker = go.Marker()) for i in r_h.columns]


			weight_graph = dcc.Graph(
							id = 'weights',
							figure = go.Figure(
								data = weight_scatters,
								layout = go.Layout(
									height = 300,
									showlegend = True,
									margin=go.Margin(l=40, r=0, t=40, b=30),
									legend = go.Legend(x=0,y=1.0)
								)
							)
						)
			reports = dm.reports(result)
			return [
			html.Div(values_graph,style={'height':'33%'}),
			html.Div(weight_graph,style={'margin-top':'10px','height':'33%'}),
			html.Div(reports,style={'height':'200px','margin-top':'10px','margin-left':'40px','overflow':'scroll'})]


		except Exception as e:
			raise e


@app.callback(Output('data-load','children'),
			[Input('stock-ticker','value'),
			Input('date-pick-range','start_date'),
			Input('date-pick-range','end_date')])
def update_data(stock,start_date,end_date):
	try:
		global_df = dm.getData(stock, start_date, end_date)
		return global_df.to_json(date_format='iso', orient='split')
	except Exception as e:
		print(e)
	
	

@app.callback(Output('tab-content', 'children'), [Input('tabs', 'value')])
def display_content(value):
	return tabs_layout[value]


@app.callback(Output('graphs','children'),
			[Input('data-load','children'),
			Input('stock-ticker','value')])
def update_graphs(global_df,stock):
	graphs = []
	try:
		df = pd.read_json(global_df, orient='split')
		candlestick = dm.getCandle(stock,df)
		bollinger_traces = dm.getBollinger(stock,df)

		graphs.append(dcc.Graph(
			id = stock,
			figure = {
				'data':[candlestick] + bollinger_traces,
				'layout':{
					'margin':{'b': 0, 'r': 10, 'l': 60, 't': 0},
					'legend':{'x': 0}
				}
			}
		))
	except: 
		graphs.append(html.H3(
                'Data is not available.',
                style={'marginTop': 20, 'marginBottom': 20}
           ))

	return graphs

@app.callback(Output('stock-close','children'),
			[Input('data-load','children'),
			Input('stock-ticker','value')])
def update_close(global_df,stock):
	try:
		df = pd.read_json(global_df, orient='split')
		scplot = dm.getScatter(stock,df)
		graph = dcc.Graph(
			id = 'scatter',
			figure = go.Figure(
				data = [scplot],
				layout = go.Layout(
					height = 400,
					showlegend = True,
					margin=go.Margin(l=40, r=0, t=40, b=30),
					legend = go.Legend(x=0,y=1.0)
				)
			)
		)
	except:
		graph = html.H3(
                'Data is not available.',
                style={'marginTop': 20, 'marginBottom': 20}
		)

	return graph

@app.callback(Output('stock-pct','children'),
			[Input('data-load','children'),
			Input('stock-ticker','value')])
def update_pct(global_df,stock):
	try:
		df = pd.read_json(global_df, orient='split')
		scplot = dm.getPct(stock,df)
		graph = dcc.Graph(
			id = 'pct',
			figure = go.Figure(
				data = [scplot],
				layout = go.Layout(
					height = 200,
					showlegend = True,
					margin=go.Margin(l=40, r=0, t=40, b=30),
					legend = go.Legend(x=0,y=1.0)
				)
			)
		)
	except:
		graph = html.H3(
		        'Data is not available.',
		        style={'marginTop': 20, 'marginBottom': 20}
		)
	return graph



@app.callback(Output('stock-pct-dis','children'),
			[Input('data-load','children'),
			Input('stock-ticker','value')])
def update_pct_dis(global_df,stock):
	try:
		df = pd.read_json(global_df, orient='split')
		distplot = dm.getPctDis(stock,df)
		graph = dcc.Graph(
			id = 'pct-dis',
			figure = go.Figure(
				data = [distplot],
				layout = go.Layout(
					height = 200,
					showlegend = True,
					margin=go.Margin(l=40, r=0, t=40, b=30),
					legend = go.Legend(x=0,y=1.0)
				)
			)
		)
	except:
		graph = html.H3(
		        'Data is not available.',
		        style={'marginTop': 20, 'marginBottom': 20}
		)
	return graph



    # data = [
    #     {
    #         'x': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
    #               2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
    #         'y': [219, 146, 112, 127, 124, 180, 236, 207, 236, 263,
    #               350, 430, 474, 526, 488, 537, 500, 439],
    #         'name': 'Rest of world',
    #         'marker': {
    #             'color': 'rgb(55, 83, 109)'
    #         },
    #         'type': ['bar', 'scatter', 'box'][int(value) % 3]
    #     },
    #     {
    #         'x': [1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
    #               2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
    #         'y': [16, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
    #               299, 340, 403, 549, 499],
    #         'name': 'China',
    #         'marker': {
    #             'color': 'rgb(26, 118, 255)'
    #         },
    #         'type': ['bar', 'scatter', 'box'][int(value) % 3]
    #     }
    # ]

    # return html.Div([
    #     dcc.Graph(
    #         id='graph',
    #         figure={
    #             'data': data,
    #             'layout': {
    #                 'margin': {
    #                     'l': 30,
    #                     'r': 0,
    #                     'b': 30,
    #                     't': 0
    #                 },
    #                 'legend': {'x': 0, 'y': 1}
    #             }
    #         }
    #     ),
    #     html.Div(' '.join(get_sentences(10)))
    # ])


if __name__ == '__main__':
    app.run_server()