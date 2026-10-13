"""All SQLite code lives here."""
import os
import sqlite3
import pandas as pd
from data_gen import (CROP_INFO, DEFAULT_INFO, FEATURES, LABEL_NAMES,
                      color_for, generate_dataset)

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "agrismart.db")
CSV_PATH = os.path.join(BASE, "data", "Crop_recommendation.csv")


def load_kaggle_csv():
    """Read the Kaggle 'Crop Recommendation' CSV with pandas. Returns None if the file is missing."""
    if not os.path.exists(CSV_PATH):
        return None
    df = pd.read_csv(CSV_PATH)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={c: (c.upper() if c.lower() in ("n", "p", "k") else c.lower()) for c in df.columns})
    df["label"] = (df["label"].astype(str).str.strip().str.lower()
                   .map(lambda s: LABEL_NAMES.get(s, s.title())))
    return df[FEATURES + ["label"]].dropna()


def data_source():
    return "Kaggle Crop Recommendation dataset" if os.path.exists(CSV_PATH) else "simulated sample data"


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS crops(
            name TEXT PRIMARY KEY, season TEXT, water TEXT, soil TEXT,
            days TEXT, tip TEXT, color TEXT);
        CREATE TABLE IF NOT EXISTS samples(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            N REAL, P REAL, K REAL, temperature REAL, humidity REAL,
            ph REAL, rainfall REAL, label TEXT);
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            field_name TEXT,
            N REAL, P REAL, K REAL, temperature REAL, humidity REAL,
            ph REAL, rainfall REAL, crop TEXT, confidence REAL);
        """)
        kaggle = load_kaggle_csv()
        have = c.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
        if kaggle is not None and have != len(kaggle):      # import Kaggle data into SQLite
            c.execute("DELETE FROM samples")
            kaggle.to_sql("samples", c, if_exists="append", index=False)
        elif kaggle is None and have == 0:                   # fallback so the site still runs
            generate_dataset().to_sql("samples", c, if_exists="append", index=False)
        # (re)build crop facts for every crop found in the data
        labels = sorted(r[0] for r in c.execute("SELECT DISTINCT label FROM samples"))
        c.execute("DELETE FROM crops")
        c.executemany("INSERT INTO crops VALUES (?,?,?,?,?,?,?)",
                      [(n, *CROP_INFO.get(n, DEFAULT_INFO), color_for(i, len(labels)))
                       for i, n in enumerate(labels)])


def load_samples():
    with conn() as c:
        return pd.read_sql_query("SELECT N,P,K,temperature,humidity,ph,rainfall,label FROM samples", c)


def get_crops():
    with conn() as c:
        return {r["name"]: dict(r) for r in c.execute("SELECT * FROM crops")}


def save_prediction(field_name, v, crop, confidence):
    with conn() as c:
        c.execute("""INSERT INTO predictions(field_name,N,P,K,temperature,humidity,ph,rainfall,crop,confidence)
                     VALUES (?,?,?,?,?,?,?,?,?,?)""",
                  (field_name, v["N"], v["P"], v["K"], v["temperature"], v["humidity"],
                   v["ph"], v["rainfall"], crop, confidence))


def history_df():
    with conn() as c:
        return pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", c)


def delete_prediction(pid):
    with conn() as c:
        c.execute("DELETE FROM predictions WHERE id=?", (pid,))
