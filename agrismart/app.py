"""AgriSmart – AI crop recommendation website (Flask + SQLite + pandas + scikit-learn)."""
import numpy as np
from flask import Flask, render_template, request, jsonify, Response
import database as db
from data_gen import FEATURES, FEATURE_META, RANGES
from model import CropModel

app = Flask(__name__)
db.init_db()
samples = db.load_samples()
cm = CropModel(samples)


def read_values(data):
    """Validate the 7 inputs; clip to allowed ranges."""
    vals = {}
    for f in FEATURES:
        try:
            v = float(data[f])
        except (KeyError, TypeError, ValueError):
            return None
        lo, hi = RANGES[f]
        vals[f] = float(np.clip(v, lo, hi))
    return vals


@app.route("/")
def home():
    return render_template("index.html", meta=FEATURE_META, crops=db.get_crops())


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/history")
def history():
    df = db.history_df()
    return render_template("history.html", rows=df.to_dict("records"))


@app.route("/about")
def about():
    return render_template("about.html", accuracy=cm.accuracy, n=len(samples),
                           crops=samples["label"].nunique(), source=db.data_source())


@app.post("/api/predict")
def api_predict():
    data = request.get_json(silent=True) or {}
    vals = read_values(data)
    if vals is None:
        return jsonify(error="Please send all 7 numeric values."), 400
    top = cm.predict(vals)
    best = top[0]
    crops = db.get_crops()
    if data.get("save"):
        name = (data.get("field_name") or "My field").strip()[:40]
        db.save_prediction(name, vals, best["crop"], best["probability"])
    return jsonify(top=top, info=crops[best["crop"]], advice=cm.advice(best["crop"], vals),
                   colors={k: v["color"] for k, v in crops.items()}, saved=bool(data.get("save")))


@app.get("/api/stats")
def api_stats():
    hist = db.history_df()
    saved = hist["crop"].value_counts().to_dict() if len(hist) else {}
    pts = samples.groupby("label").sample(25, random_state=1)
    scatter = {c: g[["temperature", "rainfall"]].rename(columns={"temperature": "x", "rainfall": "y"})
               .to_dict("records") for c, g in pts.groupby("label")}
    return jsonify(
        kpis=dict(rows=len(samples), crops=int(samples["label"].nunique()),
                  accuracy=cm.accuracy, saved=int(len(hist))),
        importance=cm.importances(), scatter=scatter, saved_by_crop=saved,
        radar=cm.radar(RANGES), features=FEATURES,
        colors={k: v["color"] for k, v in db.get_crops().items()})


@app.delete("/api/history/<int:pid>")
def api_delete(pid):
    db.delete_prediction(pid)
    return jsonify(ok=True)


@app.get("/history.csv")
def history_csv():
    csv = db.history_df().to_csv(index=False)
    return Response(csv, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=agrismart_history.csv"})


if __name__ == "__main__":
    app.run(debug=True)
