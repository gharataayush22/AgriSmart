# AgriSmart

**Contributors:** Aayush Gharat, Krishna Gajara, Jay Agarwal, Vinay Chavan, Atharva Bandekar

---

AgriSmart is a Python dashboard that uses a Kaggle crop dataset to show a scatter (dot) plot and charts, and recommends the best crop to grow based on Nitrogen, Phosphorus, Potassium, humidity and other soil and weather values.

## Project Structure

```
agrismart/
├── data/
│   └── Crop_recommendation.csv
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── about.html
│   ├── base.html
│   ├── dashboard.html
│   ├── history.html
│   └── index.html
├── agrismart.db
├── app.py
├── data_gen.py
├── database.py
├── model.py
├── README.md
└── requirements.txt
```