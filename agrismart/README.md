# AgriSmart – AI Crop Recommendation Website

Python mini project (SY B.Tech). Flask website + SQLite + pandas + NumPy + scikit-learn.

## Dataset (Kaggle)
Download **Crop Recommendation Dataset** from Kaggle and save it as `data/Crop_recommendation.csv`.
On startup the app reads it with pandas and loads it into the SQLite `samples` table.
If you add or change the CSV later, just restart the app.

## Run it
```
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000  (the database `agrismart.db` is created automatically on first run).

## Files
| File | Purpose |
|---|---|
| app.py | Flask routes and JSON APIs |
| database.py | All SQLite code (tables, insert, read, delete) |
| data_gen.py | NumPy + pandas dataset generator, crop facts |
| model.py | RandomForest model, advice engine, chart data |
| templates/ | HTML pages (Jinja2) |
| static/js/predict.js | Live sliders and result panel |
| static/js/dashboard.js | Chart.js charts |
| static/css/style.css | Styling |

## Pages
- Crop advisor: sliders update the prediction live; save a field to SQLite
- Dashboard: scatter, radar, feature-importance and saved-crops charts
- Saved fields: table from SQLite, delete rows, download CSV
- How it works: explains the pipeline for your viva

## Ideas to extend
- Load the real Kaggle "Crop Recommendation" dataset into the `samples` table
- Add a yield-prediction page (LinearRegression)
- Add login with Flask sessions
- Add a weather API for automatic temperature/rainfall
