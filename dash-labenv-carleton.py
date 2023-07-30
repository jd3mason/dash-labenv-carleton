from datetime import datetime
import base64
import io
from dash import Dash, dcc, html, Output, Input
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import pandas as pd

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN, dbc_css])
server = app.server
template = load_figure_template('cerulean')


header = html.H4("COLD Lab Environment", className="bg-primary text-white p-2 mb-2 text-center")

upload_datalogger = html.Div(
    dcc.Upload(
        id='upload-datalogger',
        children=html.Div(['Drag and Drop DataLogger File']),
        style={
            'width': '100%',
            'height': '10vh',
            'lineHeight': '10vh',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        },
        className='mt-1 mb-2' 
    ),
)

upload_particlecounter = html.Div(
    dcc.Upload(
        id='upload-particlecounter',
        children=html.Div(['Drag and Drop Particle Counter File']),
        style={
            'width': '100%',
            'height': '10vh',
            'lineHeight': '10vh',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center'
        },
        className='mt-1 mb-2' 
    ),
)

particle_size = html.Div(
    dcc.Checklist(
        id='particle-size-checklist',
        options=[
            {'label': '0.3 \u03BCm', 'value': '0.3 \u03BCm'},
            {'label': '0.5 \u03BCm', 'value': '0.5 \u03BCm'},
            {'label': '1.0 \u03BCm', 'value': '1.0 \u03BCm'},
            {'label': '2.0 \u03BCm', 'value': '2.0 \u03BCm'},
            {'label': '5.0 \u03BCm', 'value': '5.0 \u03BCm'},
            {'label': '10.0 \u03BCm', 'value': '10.0 \u03BCm'}
        ],
        value=['0.5 \u03BCm'],
        style={'font-size': '14px'},
        labelClassName='ms-3 mt-3'
    )
)

temperature_graph = html.Div(
    dcc.Graph(
        id='temperature-graph',
        config={'displayModeBar': True, 'toImageButtonOptions': {'height': 675, 'width': 1101}},
        style={'height': '70vh'}
    )
)

hummidity_graph = html.Div(
    dcc.Graph(
        id='humidity-graph',
        config={'displayModeBar': True, 'toImageButtonOptions': {'height': 675, 'width': 1101}},
        style={'height': '70vh'}
    )
)

particle_graph = html.Div(
    dcc.Graph(
        id='particle-graph',
        config={'displayModeBar': True, 'toImageButtonOptions': {'height': 675, 'width': 1101}},
        style={'height': '63.5vh'}
    )
)

tab1 = dbc.Tab([temperature_graph], label='Temperature')  
tab2 = dbc.Tab([hummidity_graph], label='Relative Humidity')
tab3 = dbc.Tab([particle_size, particle_graph], label='Particle Count')
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))


app.layout = dbc.Container([
    dcc.Store(id='datalogger-data'),
    dcc.Store(id='particlecounter-data'),
    header,
    dbc.Row([
        dbc.Col([upload_datalogger], width=6),
        dbc.Col([upload_particlecounter], width=6)]),
    tabs],
    className='dbc',
    fluid=True
)


@app.callback(
    Output(component_id='datalogger-data', component_property='data'),
    Input(component_id='upload-datalogger', component_property='contents'),
)
def store_date(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        datalogger_data = df.to_dict('records') 
    else:
        datalogger_data = None
    return datalogger_data


@app.callback(
    Output(component_id='particlecounter-data', component_property='data'),
    Input(component_id='upload-particlecounter', component_property='contents'),
)
def store_date(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        particlecounter_data = df.to_dict('records') 
    else:
        particlecounter_data = None
    return particlecounter_data


@app.callback(
    Output(component_id='temperature-graph', component_property='figure'),  
    Output(component_id='humidity-graph', component_property='figure'),
    Input(component_id='datalogger-data', component_property='data')
)
def update_datalogger_plots(datalogger_data):
    if datalogger_data is not None:
        df = pd.DataFrame(datalogger_data)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)
        date_buttons = [{'count': 1, 'step': 'day', 'stepmode': 'backward', 'label': '1D'},
                        {'count': 5, 'step': 'day', 'stepmode': 'backward', 'label': '5D'},
                        {'count': 1, 'step': 'month', 'stepmode': 'backward', 'label': '1M'},
                        {'count': 3, 'step': 'month', 'stepmode': 'backward', 'label': '3M'},
                        {'count': 6, 'step': 'month', 'stepmode': 'backward', 'label': '6M'},
                        {'count': 1, 'step': 'year', 'stepmode': 'backward', 'label': '1Y'},
                        {'count': 3, 'step': 'year', 'stepmode': 'backward', 'label': '3Y'},
                        {'count': 5, 'step': 'year', 'stepmode': 'backward', 'label': '5Y'}]
        fig_temperature = px.line(df, x=df.index, y='Chan 1 - Deg C')
        fig_humidity = px.line(df, x=df.index, y='Chan 2 - %RH')
        fig_temperature.update_layout({'xaxis': {'rangeselector': {'buttons': date_buttons}}})
        fig_humidity.update_layout({'xaxis': {'rangeselector': {'buttons': date_buttons}}})
    else:
        fig_temperature = px.scatter(x=[datetime.now()], y=[-1], range_y=[0, 20])
        fig_humidity = px.scatter(x=[datetime.now()], y=[-1], range_y=[0, 40])

    fig_temperature.update_layout(xaxis_title='Time', yaxis_title='Temperature (\u00B0C)')
    fig_temperature.update_traces(marker=dict(size=3))
    fig_humidity.update_layout(xaxis_title='Time', yaxis_title='Relative Humidity (%)')
    fig_humidity.update_traces(marker=dict(size=3))
    return fig_temperature, fig_humidity


@app.callback(
    Output(component_id='particle-graph', component_property='figure'),  
    Input(component_id='particlecounter-data', component_property='data'),
    Input(component_id='particle-size-checklist', component_property='value')
)
def update_particlecounter_plot(particlecounter_data, particle_size_list):
    if particlecounter_data is not None:
        df = pd.DataFrame(particlecounter_data)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df.set_index('Datetime', inplace=True)
        df.columns = ['0.3 \u03BCm', '0.5 \u03BCm', '1.0 \u03BCm', '2.0 \u03BCm', '5.0 \u03BCm', '10.0 \u03BCm']
        particle_size_list_sorted = sorted(particle_size_list.copy())
        if '10.0 \u03BCm' in particle_size_list_sorted: particle_size_list_sorted.remove('10.0 \u03BCm'); particle_size_list_sorted.append('10.0 \u03BCm')
        dff = df.loc[:, particle_size_list_sorted]
        particle_color_map = {'0.3 \u03BCm': 'red', '0.5 \u03BCm': 'cornflowerblue', '1.0 \u03BCm': 'gold', '2.0 \u03BCm': 'mediumseagreen', '5.0 \u03BCm': 'purple','10.0 \u03BCm': 'darkorange'}
        date_buttons = [{'count': 1, 'step': 'day', 'stepmode': 'backward', 'label': '1D'},
                        {'count': 5, 'step': 'day', 'stepmode': 'backward', 'label': '5D'},
                        {'count': 1, 'step': 'month', 'stepmode': 'backward', 'label': '1M'},
                        {'count': 3, 'step': 'month', 'stepmode': 'backward', 'label': '3M'},
                        {'count': 6, 'step': 'month', 'stepmode': 'backward', 'label': '6M'},
                        {'count': 1, 'step': 'year', 'stepmode': 'backward', 'label': '1Y'},
                        {'count': 3, 'step': 'year', 'stepmode': 'backward', 'label': '3Y'},
                        {'count': 5, 'step': 'year', 'stepmode': 'backward', 'label': '5Y'}]
        fig_particle = px.line(dff, x=dff.index, y=dff.columns, log_y=True, range_y=[1,10000000], color_discrete_map=particle_color_map)
        fig_particle.update_layout({'xaxis': {'rangeselector': {'buttons': date_buttons}}})
    else:
        fig_particle = px.scatter(x=[datetime.now()], y=[0], log_y=True, range_y=[1,10000000])
    fig_particle.update_layout(xaxis_title='Time', yaxis_title='Particles/ft\u00B3', legend=dict(title=None))
    fig_particle.update_traces(marker=dict(size=3))
    return fig_particle



if __name__=='__main__':
    app.run_server(debug=False)
