"""Machine-learning part: RandomForest + simple rule-based advice."""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from data_gen import FEATURES

ADVICE = {
    "N": ("Nitrogen is low. Add urea or well-rotted compost before sowing.",
          "Nitrogen is high. Skip urea this cycle to avoid lush, weak growth."),
    "P": ("Phosphorus is low. Apply single super phosphate (SSP) at sowing.",
          "Phosphorus is high. No phosphate fertiliser needed this season."),
    "K": ("Potassium is low. Apply muriate of potash (MOP).",
          "Potassium is high. Hold back on potash."),
    "temperature": ("Season is cooler than ideal. Consider a later sowing date.",
                    "Season is hotter than ideal. Mulch and irrigate in the evening."),
    "humidity": ("Air is drier than ideal. Plan extra irrigation.",
                 "Air is very humid. Watch for fungal disease and space plants well."),
    "ph": ("Soil is too acidic. Add agricultural lime.",
           "Soil is too alkaline. Add gypsum or organic matter."),
    "rainfall": ("Rainfall is below what this crop needs. Arrange irrigation.",
                 "Rainfall is above ideal. Make sure fields have good drainage."),
}


class CropModel:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        X, y = df[FEATURES], df["label"]
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        self.clf = RandomForestClassifier(n_estimators=150, random_state=42).fit(X_tr, y_tr)
        self.accuracy = round(float(self.clf.score(X_te, y_te)) * 100, 1)
        self.profile = df.groupby("label")[FEATURES].agg(["mean", "std"])

    def predict(self, values: dict, top=3):
        x = pd.DataFrame([values], columns=FEATURES)
        proba = self.clf.predict_proba(x)[0]
        order = np.argsort(proba)[::-1][:top]
        return [{"crop": str(self.clf.classes_[i]), "probability": round(float(proba[i]) * 100, 1)}
                for i in order]

    def importances(self):
        imp = sorted(zip(FEATURES, self.clf.feature_importances_), key=lambda t: -t[1])
        return [{"feature": f, "value": round(float(v) * 100, 1)} for f, v in imp]

    def advice(self, crop: str, values: dict):
        """Compare each input with the crop's typical value (z-score)."""
        out = []
        for f in FEATURES:
            mean = self.profile.loc[crop, (f, "mean")]
            std = max(self.profile.loc[crop, (f, "std")], 1e-6)
            z = (values[f] - mean) / std
            if z < -1:
                out.append({"feature": f, "status": "low", "message": ADVICE[f][0]})
            elif z > 1:
                out.append({"feature": f, "status": "high", "message": ADVICE[f][1]})
        return out

    def radar(self, ranges: dict):
        """Typical profile of each crop scaled 0-100 (for the radar chart)."""
        res = {}
        for crop in self.profile.index:
            res[crop] = [round(float((self.profile.loc[crop, (f, "mean")] - ranges[f][0]) /
                                     (ranges[f][1] - ranges[f][0]) * 100), 1) for f in FEATURES]
        return res
