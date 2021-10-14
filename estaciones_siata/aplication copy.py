import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

url = "http://siata.gov.co:8089/estacionesAirePM25/cf7bb09b4d7d859a2840e22c3f3a9a8039917cc3/"
data = pd.read_json(url, convert_dates = True)
stationsInfo = {
    'id' : [],
    'code' : [],
    'date' : [],
    'name': [],
    'longitude': [],
    'latitude': [],
    'contaminationValue' : [],
    'colorIconHex': [],
    'category': [],
}
for i in range(len(data['datos'])):
    stationsInfo['id'].append(i)
    stationsInfo['code'].append(data['datos'][i]['codigo'])
    stationsInfo['date'].append(data['datos'][i]['ultimaActualizacion'])
    stationsInfo['name'].append(data['datos'][i]['nombre'][data['datos'][i]['nombre'].find('-')+2:])
    stationsInfo['longitude'].append(data['datos'][i]['coordenadas'][0]['longitud'])
    stationsInfo['latitude'].append(data['datos'][i]['coordenadas'][0]['latitud'])
    stationsInfo['contaminationValue'].append(data['datos'][i]['valorICA'])
    stationsInfo['colorIconHex'].append(data['datos'][i]['colorIconoHex'])
    stationsInfo['category'].append(data['datos'][i]['categoria'])

stationsInfo = pd.DataFrame(stationsInfo)
stationsInfo['date'].astype('datetime64')

#web server
app = dash.Dash()

px.set_mapbox_access_token('pk.eyJ1IjoibGVvbmFyZG9iZXRhbmN1ciIsImEiOiJjazlybGNiZWcwYjZ6M2dwNGY4MmY2eGpwIn0.EJjpR4klZpOHSfdm7Tsfkw')
mapfig = px.scatter_mapbox(stationsInfo, lat='latitude', lon='longitude', color='category',
                            text= 'name', mapbox_style='outdoors',
                            labels='name')
mapfig.update_layout(
    legend={
        'font_size':12,
        'itemclick': "toggleothers",
        'title': {
            'font_size': 18,
            'text': 'estaciones de monitoreo'
        }
    })
mapfig.update_mapboxes(
    zoom=10.5
    )
mapfig.update_traces(
    {
        'marker': {
            'size': 25,
            'opacity': 0.5,
        }
    }
)

stationlist = []
for station in range(len(stationsInfo['id'])):
    stationlist.append({
        'label': stationsInfo['name'][station], 'value':stationsInfo['name'][station]
    })
app.layout = html.Div(style={},children=[
    html.H1('Contaminación el el valle de Aburrá', style={'textAlign':'center'}),
    dcc.Graph(id='map2',style = {'width': '70%'} ,figure=mapfig),
    dcc.Dropdown(
        id = 'station-list',
        options= stationlist,
        placeholder="Selecciona una estación de monitoreo",
        value = ''
    ),
    html.Div(
        id='information-box', children=[
            html.H3('Información de la estación'),
            html.P('nombre completo'),
            html.P(id='station-name'),
            html.P('latitud'),
            html.P(id='station-latitude'),
            html.P('Longitud'),
            html.P(id='station-longitude'),
            html.P('Valor de la contaminación'),
            html.P(id='station-contaminationValue'),
            html.P('ultima actualización'),
            html.P(id='station-date'),
        ]
    )
])
@app.callback(
    Output('station-name', 'children'),
    Output('station-latitude', 'children'),
    Output('station-longitude', 'children'),
    Output('station-contaminationValue', 'children'),
    Output('station-date', 'children'),
    Input('station-list', 'value')
)
def update_output(value):
    name = value
    latitude = stationsInfo.loc[stationsInfo.loc[:, 'name'] == value,'latitude']
    longitude = stationsInfo.loc[stationsInfo.loc[:, 'name'] == value,'longitude']
    contaminationValue = stationsInfo.loc[stationsInfo.loc[:, 'name'] == value,'contaminationValue']
    date = stationsInfo.loc[stationsInfo.loc[:, 'name'] == value,'date']
    return(value, latitude, longitude, contaminationValue, date)

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0',port=80)