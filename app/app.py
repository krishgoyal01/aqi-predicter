from flask import Flask, render_template,request, jsonify
import pandas as pd
import pickle
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
columns_path = os.path.join(BASE_DIR, 'models', 'original_city.pkl')# name of cities 
data_path = os.path.join(BASE_DIR, 'data', 'processed', 'city_day_features.pkl')# processed data

with open(columns_path, 'rb') as f:
    city = pickle.load(f)

cities=sorted(city.tolist())

pollutants = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'AQI']

with open(data_path, 'rb') as f:
    city_data = pickle.load(f)


app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html',cities=cities,pollutants=pollutants)
@app.route('/get_data')
def get_data():
    city = request.args.get('city')
    pollutant = request.args.get('pollutant')
    x='City_'+city
    filtered_data=city_data[(city_data[x] == 1) ].sort_values('Date')
    response = {
        'dates': filtered_data['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'values': filtered_data[pollutant].tolist()
    }
    return jsonify(response)


    
if __name__ == '__main__':
    app.run(debug=True)