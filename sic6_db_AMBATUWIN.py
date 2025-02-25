from datetime import datetime
from flask import Flask,jsonify,request
app = Flask(__name__)
from statistics import mean
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://Zephyros:ambatulearn123@sensorcluster.b6izp.mongodb.net/?appName=SensorCluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Database
db = client['MyDatabase']
my_collections = db['SensorData']

def store_data(data):
    results = my_collections.insert_one(data)
    return results.inserted_id

def get_temperature():
    get_temperature_result = my_collections.find({},{'_id': 0,'temperature':1,'timestamp':1})
    return get_temperature_result

def get_humudity():
    get_humidity_result = my_collections.find({},{'_id': 0,'humidity':1})
    return get_humidity_result

@app.route('/',methods=['GET'])
def entry_point():
    return jsonify(message="Hello World")


@app.route('/sensor1',methods=['POST','GET'])
def data_sensor():
    if request.method == 'POST':
        body = request.get_json()
        temperature = body ['temperature']
        humidity = body ['humidity']
        gerakan = body ['gerakan']
        timestamp = body ['timestamp']
        data_final = {
            "temperature":temperature,
            "humidity":humidity,
            "gerakan":gerakan,
            "timestamp": timestamp
        }
        
        id = store_data(data_final)
        return {
            "message":f"Hello i have processed your request with id {id}",
        }

@app.route('/sensor1/temperature/all',methods=['GET'])
def get_data_temperature():
    result = [x for x in get_temperature()]
    start_date = request.args.get('start_date','')
    end_date = request.args.get('end_date','')
    try:
        start_date_timestamp = datetime.strptime(start_date,"%d-%m-%Y  %H:%M:%S")
        end_date_timestamp = datetime.strptime(end_date,"%d-%m-%Y  %H:%M:%S")
        temp_list = []
        for items in result:
            element = datetime.strptime(items['timestamp'],"%d-%m-%Y  %H:%M:%S")
            if start_date_timestamp < element < end_date_timestamp:
                temp_list.append(items)
        print(result)
        return jsonify(message="Success", data = temp_list)    
    except:
        pass 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)