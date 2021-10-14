import pandas as pd
url = "http://siata.gov.co:8089/estacionesAirePM25/cf7bb09b4d7d859a2840e22c3f3a9a8039917cc3/"
data = pd.read_json(url, convert_dates = True)

stationsInfo = {
    'code' : [],
    'date' : [],
    'name': [],
    'longitude': [],
    'latitude': [],
    'contaminationValue' : [],
    'colorIconHex': [],
    'category': [],
}
for i in range(18):
    stationsInfo['code'].append(data['datos'][i]['codigo'])
    stationsInfo['date'].append(data['datos'][i]['ultimaActualizacion'])
    stationsInfo['name'].append(data['datos'][i]['nombre'])
    stationsInfo['longitude'].append(data['datos'][i]['coordenadas'][0]['latitud'])
    stationsInfo['latitude'].append(data['datos'][i]['coordenadas'][0]['longitud'])
    stationsInfo['contaminationValue'].append(data['datos'][i]['valorICA'])
    stationsInfo['colorIconHex'].append(data['datos'][i]['colorIconoHex'])
    stationsInfo['category'].append(data['datos'][i]['categoria'])

data = pd.DataFrame(stationsInfo)
data['date'].astype('datetime64')