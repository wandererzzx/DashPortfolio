import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go 
from datetime import datetime as dt
from util import DataManagement as dm

app = dash.Dash(__name__)
server = app.server

app.config['suppress_callback_exceptions']=True
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-finance-1.28.0.min.js'


vertical = False

if not vertical:
    app.layout = html.Div([
        dcc.Tabs(
            tabs=[
                {'label': 'Price Data', 'value': 1},
                {'label': 'Optimization', 'value': 2},
                {'label': 'Real-Time Reaction', 'value': 3},
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
                    {'label': 'Optimization', 'value': 2},
                    {'label': 'Real-Time Reaction', 'value': 3},
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

tabs_layout[2] = html.Div(
	html.Div('Portfolio Optimization')
)

tabs_layout[3] = html.Div(
	html.Div('Portfolio Optimization')
)


@app.callback(Output('data-load','children'),
			[Input('stock-ticker','value'),
			Input('date-pick-range','start_date'),
			Input('date-pick-range','end_date')])
def update_data(stock,start_date,end_date):
	global_df = dm.getData(stock, start_date, end_date)
	return global_df.to_json(date_format='iso', orient='split')
	

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