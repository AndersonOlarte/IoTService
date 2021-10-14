from flask import Flask, request
from flask.scaffold import _matching_loader_thinks_module_is_package
import mysql.connector as mys
import pandas as pd
import sqlite3
import json
from scipy.interpolate import griddata
data = {}
parameters_db = {'host':'localhost', 'user':'root', 'password':'@Anderson12345678', 'database':'IoT' }
#parameters_db = 'incomingData.db'
isLocal = False

def ConnectionDB(parameters, isLocal):
    if (isLocal):
        return sqlite3.connect(parameters)
    else:
        return mys.connect(host=parameters['host'], user=parameters['user'], password=parameters['password'], database=parameters['database'], auth_plugin='mysql_native_password')


def CalculateAQI(ica):
    aqiData = pd.DataFrame({
        'aqiLow':[0, 51, 101, 151, 201, 301],
        'aqiHigh':[50, 100, 150, 200, 300, 500],
        'concLow':[0.0, 12.1, 35.5, 55.5, 150.5, 250.5],
        'concHigh':[12.0, 35.4, 55.4, 150.4, 250.4, 500.4],
        'aqiState': ['Buena', 'Moderada', 'Insalubre para grupos sensitivos', 'Insalubre','Muy insalubre','Peligroso' ]
    })
    rowData = 0
    for number in range(aqiData.shape[0]):
        if (ica >= aqiData['concLow'][number] and ica <= aqiData['concHigh'][number]):
            rowData = number
            break
        else:
            continue
    aqiValue = (((aqiData['aqiHigh'][rowData]-aqiData['aqiLow'][rowData])/
    (aqiData['concHigh'][rowData]-aqiData['concLow'][rowData]))*(ica -aqiData['concLow'][rowData])
    +aqiData['aqiLow'][rowData])
    return(int(aqiValue), aqiData['aqiState'][rowData])

app = Flask(__name__)

@app.route('/')
def index():
    return({"Hola_desde":"Index"})

@app.route('/createTable')
def createDB():
    #conexión a archivo local
    connector = ConnectionDB(parameters_db, isLocal)
    #connector = sqlite3.connect(dbPath)
    cursor = connector.cursor()
    cursor.execute('DROP TABLE IF EXISTS data')
    cursor.execute('CREATE TABLE data (date DATETIME ,sensorid NUMERIC, packeid NUMERIC, temperature NUMERIC, humidity NUMERIC, light NUMERIC, longitude NUMERIC, latitude NUMERIC )')
    connector.commit()
    connector.close()
    return("Se ha creado la base de datos")

@app.route('/data', methods=['POST'])
def readData():

    values = request.data.decode('utf-8').split(";")
    for item in values:
        sensor = item.split()
        data[sensor[0]] = sensor[1]
    query = 'INSERT INTO data VALUES("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}");'.format(
        data['date'],data['sensorID'],data['packetID'],data['Temperature'],data['Humidity'],
        data['Light'],data['Latitude'],data['Longitude'])
    connector = ConnectionDB(parameters_db, isLocal)
    cursor = connector.cursor()
    cursor.execute(query)
    connector.commit()
    connector.close()
    return("200 ok")

@app.route('/printData')
def printData():
    connector = ConnectionDB(parameters_db, isLocal)
    dataFrame = pd.read_sql_query('SELECT * FROM data',connector)
    connector.close()
    return(dataFrame.to_json())

@app.route('/requestICA', methods=['POST'])
def queryICA():
    position = json.loads(request.data.decode('utf-8'))
    print('la posición enviada por la aplicación local es: ', position)
    print(position["longitude"])
    url = "http://siata.gov.co:8089/estacionesAirePM25/cf7bb09b4d7d859a2840e22c3f3a9a8039917cc3/"
    capturaWeb = pd.read_json(url, convert_dates=True)
    lat = []
    lon = []
    nom = []
    fechas = []
    cont = []
    for i in range(18):
        nom.append(capturaWeb['datos'][i]['nombre'])
        lat.append(capturaWeb['datos'][i]['coordenadas'][0]['longitud'])
        lon.append(capturaWeb['datos'][i]['coordenadas'][0]['latitud'])
        cont.append(capturaWeb['datos'][i]['valorICA'])
        fechas.append(capturaWeb['datos'][i]['ultimaActualizacion'])
    latitud = position["latitude"]
    longitud = position["longitude"]

    ICA = griddata((lat, lon), cont, (latitud, longitud), method='nearest')
    print('la contaminación en la ubicación es: ', ICA)
    AQI, state = CalculateAQI(ICA)
    response = {"ica": ICA, "aqi":AQI,"state": state}
    # return({"Hola_desde":"Index"})
    return(json.dumps(response))

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*" # <- You can change "*" for a domain for example "http://localhost"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response

if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
