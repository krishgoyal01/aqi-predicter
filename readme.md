# AQI Forecasting Dashboard

An end-to-end machine learning pipeline that forecasts Air Quality Index (AQI) 
across 20 Indian cities using historical CPCB sensor data (2015-2020), 
deployed as an interactive Flask dashboard.

**Live Demo:** [https://aqi-predictor.onrender.com](https://aqi-predictor.onrender.com)
*(Hosted on Render's free tier — first load may take 30-50s if the app has been idle)*

## Features
- Interactive dropdown-driven chart (city + pollutant) using Plotly.js
- AQI prediction using a trained XGBoost model
- Historical Explorer mode — compare predicted vs actual AQI for any past date
- Pollution regime classification (Good/Moderate/Poor/Severe) via K-Means clustering
- Fully containerized with Docker and deployed on Render

## Data
- Source: [Air Quality Data in India (2015-2020)](https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india), CPCB via Kaggle
- ~29,500 daily records across 22 cities, narrowed to 20,000 after data quality filtering

## Approach

### Data Cleaning
- Linear interpolation (capped at 5-day gaps) + city-month average fallback for missing pollutant values
- Dropped Xylene (60% missing) and rows with unresolvable gaps
- Removed AQI outliers outside CPCB's valid 0-500 range
- Excluded Aizawl and Kochi due to insufficient seasonal coverage (<1 year of data)

### Feature Engineering
- Lag features (AQI_lag1/2/3/7) and rolling averages (3-day, 7-day)
- Calendar features: month, day of week, year, season
- One-hot encoded city and season

### Modeling
*Linear Regression:*
Mean Absolut Error: 12.45 
Root Mean Squared Error:19.31 
R²:  0.937 
*Random Forest:*
Mean Absolut Error: 10.60 
Root Mean Squared Error:16.66 
R²:  0.953 
*XGBoost (deployed)*
Mean Absolut Error: 10.31
Root Mean Squared Error:16.24 
R²:  0.955 

Train/test split is **time-based** (not random shuffling) to avoid leaking future information into training

Feature importance confirms the model relies primarily on PM2.5 (55%) and 
recent AQI history (AQI_lag1, 21%), consistent with real-world air quality science.

### Unsupervised Clustering
K-Means (k=4) clusters days into pollution severity regimes based on raw 
pollutant concentrations alone (no AQI used). Validated:
- Cluster median AQI increases monotonically (Good → Severe), confirming 
  the clusters align with real severity
- Cross-checked against DBSCAN, which found no strong density-based 
  separation — confirming pollution levels form more of a continuum than 
  sharply distinct clusters in raw pollutant space

## Tech Stack
Python · Pandas · Scikit-learn · XGBoost · Flask · Plotly.js · Docker · Gunicorn · Render

## Running Locally
```bash
git clone https://github.com/krishgoyal01/aqi-predicter.git
cd aqi-predicter
docker build -t aqi-predictor .
docker run -p 5000:5000 -e PORT=5000 aqi-predictor
```
Visit `http://localhost:5000`

## Known Limitations
- Dataset ends July 2020; "latest date" predictions reflect monsoon-season 
  conditions (naturally lower pollution) — use Historical Explorer to see 
  the model across different seasons
- Only production model (XGBoost) and clustering artifacts are committed to 
  the repo; Linear Regression and Random Forest were used for comparison 
  during development but aren't part of the deployed application
- Planned: live data integration via OpenAQ API for real-time forecasting

## Project Structure
```
aqi-predictor/
├── app/              # Flask application (routes, templates, static JS/CSS)
├── data/processed/   # Cleaned, feature-engineered dataset
├── models/           # Trained XGBoost + K-Means models
├── notebook/         # EDA, cleaning, and model training notebooks
├── Dockerfile
└── reqs.txt
```