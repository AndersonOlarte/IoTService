from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return ("200 OK")

@app.route('/data', methods=['POST'])
def readData():
    values = request.data.decode('utf-8').split(sep=';')
    print(values)
    return("200 OK")
if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0', port=80)