import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd 

url = "http://siata.gov.co:8089/estacionesAirePM25/cf7bb09b4d7d859a2840e22c3f3a9a8039917cc3/"
capturaWeb = pd.read_json(url, convert_dates=True)

lat = []
lon = []
nom = []
fechas = []
color = []
cont = []

for i in range(18):
    
    nom.append(capturaWeb['datos'][i]['nombre'])
    lat.append(capturaWeb['datos'][i]['coordenadas'][0]['latitud'])
    lon.append(capturaWeb['datos'][i]['coordenadas'][0]['longitud'])
    cont.append(capturaWeb['datos'][i]['valorICA'])
    color.append(capturaWeb['datos'][i]['colorIconoHex'])
    fechas.append(capturaWeb['datos'][i]['ultimaActualizacion'])

Estaciones = []
for estaciones in range(len(nom)):
    Estaciones.append(
        {
        'name':nom[estaciones],
        'lat': [lat[estaciones]],
        'lat': [lon[estaciones]],
        'marker': {
                'color':[color[estaciones]],
                'size': [100],
                'opacity': 0.6
            },
            'customdata': ['este es un valor'],
            'type': 'scattermapbox'
        }
    )



app = dash.Dash()

app.layout = html.Div([
    html.H1('Mapa de contaminacion de particulas p2.5m'),
    html.Div('a continuacion vamos a ver el mapa de medellin con la contaminaicon medida por los sensores de Siata'),
    dcc.Graph(id='map', figure={
        'data': Estaciones,
        'layout': {
            'mapbox': {
                'accesstoken': 'pk.eyJ1IjoibGVvbmFyZG9iZXRhbmN1ciIsImEiOiJjazlybGNiZWcwYjZ6M2dwNGY4MmY2eGpwIn0.EJjpR4klZpOHSfdm7Tsfkw',
                'center' : {
                    'lat': 6.240737,
                    'lon': -75.589900
                    },
                'zoom' : 10
            },
            'hovermode': 'closest',
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
        }
    })
])


if __name__ == '_main_':
    app.run_server(debug=True,host='0.0.0.0',port=80)