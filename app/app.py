from flask import Flask, render_template,request, jsonify
import pandas as pd
import pickle
import os
import joblib
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
columns_path = os.path.join(BASE_DIR, 'models', 'original_city.pkl')# name of cities 
data_path = os.path.join(BASE_DIR, 'data', 'processed', 'city_day_features.pkl')# processed data

with open(columns_path, 'rb') as f:
    city = pickle.load(f)

cities=sorted(city.tolist())

pollutants = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3', 'CO', 'SO2', 'O3', 'AQI']

with open(data_path, 'rb') as f:
    city_data = pickle.load(f)
#xg boost model
model_path=os.path.join(BASE_DIR, 'models', 'model_xgb.pkl')
model_columns_path=os.path.join(BASE_DIR, 'models', 'model_columns.pkl')
with open(model_path, 'rb') as f:
    model_xgb = pickle.load(f)

with open(model_columns_path, 'rb') as f:
    model_columns = pickle.load(f)

# kmeans clustering model
kmeans_path=os.path.join(BASE_DIR, 'models', 'kmeans_model.pkl')
kmeans = joblib.load(kmeans_path)
cluster_scaler_path=os.path.join(BASE_DIR, 'models', 'cluster_scaler.pkl')
cluster_scaler = joblib.load(cluster_scaler_path)
cluster_columns_path=os.path.join(BASE_DIR, 'models', 'cluster_columns.pkl')
cluster_columns = joblib.load(cluster_columns_path)

cluster_labels = {1: 'Good', 2: 'Moderate', 3: 'Poor', 0: 'Severe'}


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


@app.route('/get_dates')
def get_dates():
    city = request.args.get('city')
    x='City_'+city
    city_rows=city_data[(city_data[x] == 1) ].sort_values('Date')
    dates = city_rows['Date'].dt.strftime('%Y-%m-%d').tolist()
    return jsonify({'dates': dates})


@app.route('/predict_historical')
def predict_historical():
    city = request.args.get('city')
    x='City_'+city
    city_rows= city_data[(city_data[x] == 1)].sort_values('Date')
    date = request.args.get('date')
    selected_row=city_rows[city_rows['Date']==date]
    #last_row = city_rows.iloc[-1]
    if(selected_row.empty):
        return jsonify({'error': 'No data available for the selected date.'}), 404
    selected_row = selected_row.iloc[0]
    actual_aqi = selected_row['AQI']
    # aqi prediction using xgboost model
    input_row = selected_row[model_columns]
    input_df=pd.DataFrame([input_row])
    prediction = model_xgb.predict(input_df)[0]
    # kmeans clustering prediction
    cluster_input = selected_row[cluster_columns]
    cluster_input_df = pd.DataFrame([cluster_input])
    cluster_input_scaled = cluster_scaler.transform(cluster_input_df)
    cluster_number = kmeans.predict(cluster_input_scaled)[0]
    cluster_name= cluster_labels[cluster_number]

    return jsonify({'city':city,
                    'selected_date': selected_row['Date'].strftime('%Y-%m-%d'),
                    'actual_aqi':float(actual_aqi),
                    'predicted_aqi': round(float(prediction), 2),
                    'pollution_level': cluster_name
                    })

@app.route('/predict_latest')
def predict_latest():
    city = request.args.get('city')
    x='City_'+city
    city_rows= city_data[(city_data[x] == 1)].sort_values('Date')
    last_row = city_rows.iloc[-1]
    # aqi prediction using xgboost model
    input_row = last_row[model_columns]
    input_df=pd.DataFrame([input_row])
    prediction = model_xgb.predict(input_df)[0]
    # kmeans clustering prediction
    cluster_input = last_row[cluster_columns]
    cluster_input_df = pd.DataFrame([cluster_input])
    cluster_input_scaled = cluster_scaler.transform(cluster_input_df)
    cluster_number = kmeans.predict(cluster_input_scaled)[0]
    cluster_name= cluster_labels[cluster_number]

    return jsonify({'city':city,
                    'selected_date': last_row['Date'].strftime('%Y-%m-%d'),
                    'predicted_aqi': round(float(prediction), 2),
                    'pollution_level': cluster_name
                    })

        
