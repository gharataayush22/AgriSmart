"""Feature settings, crop facts, and a small fallback dataset.

The project normally uses the Kaggle 'Crop Recommendation' CSV (see database.py).
generate_dataset() is only a fallback so the site still runs if the CSV is missing.
"""
import colorsys
import numpy as np
import pandas as pd

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Slider limits cover the full range found in the Kaggle dataset
FEATURE_META = [
    dict(key="N", label="Nitrogen", unit="kg/ha", min=0, max=140, step=1, value=80, hint="Leafy growth"),
    dict(key="P", label="Phosphorus", unit="kg/ha", min=5, max=145, step=1, value=48, hint="Roots and flowering"),
    dict(key="K", label="Potassium", unit="kg/ha", min=5, max=205, step=1, value=40, hint="Crop strength"),
    dict(key="temperature", label="Temperature", unit="°C", min=8, max=44, step=0.5, value=24, hint="Average during season"),
    dict(key="humidity", label="Humidity", unit="%", min=14, max=100, step=1, value=80, hint="Relative humidity"),
    dict(key="ph", label="Soil pH", unit="", min=3.5, max=10, step=0.1, value=6.4, hint="Below 7 is acidic"),
    dict(key="rainfall", label="Rainfall", unit="mm", min=20, max=300, step=1, value=200, hint="Seasonal total"),
]
RANGES = {m["key"]: (m["min"], m["max"]) for m in FEATURE_META}

# Kaggle labels are lowercase and joined, e.g. 'kidneybeans'
LABEL_NAMES = {"kidneybeans": "Kidney Beans", "pigeonpeas": "Pigeon Peas", "mothbeans": "Moth Beans",
               "mungbean": "Mung Bean", "blackgram": "Black Gram"}

# season, water need, soil, duration, tip
CROP_INFO = {
    "Rice": ("Kharif (Jun–Nov)", "Very high", "Clay / clay loam", "110–150 days", "Keep fields flooded about 5 cm deep during tillering."),
    "Maize": ("Kharif / Rabi", "Moderate", "Sandy loam", "90–120 days", "Needs good drainage; two days of waterlogging can kill seedlings."),
    "Chickpea": ("Rabi (Oct–Mar)", "Low", "Sandy loam, well drained", "95–110 days", "A legume: it fixes its own nitrogen, so skip extra urea."),
    "Kidney Beans": ("Kharif / Rabi (hills)", "Moderate", "Well-drained loam", "90–120 days", "Avoid waterlogging; stake climbing varieties."),
    "Pigeon Peas": ("Kharif (Jun–Dec)", "Low", "Well-drained loam", "150–180 days", "Intercrop with sorghum or cotton for extra income."),
    "Moth Beans": ("Kharif (Jul–Oct)", "Very low", "Sandy, arid soil", "70–90 days", "Very drought hardy; good for dry regions like Rajasthan."),
    "Mung Bean": ("Kharif / Summer", "Low", "Loam / sandy loam", "60–75 days", "A short-duration legume that improves soil nitrogen."),
    "Black Gram": ("Kharif / Rabi", "Low", "Heavy loam", "70–90 days", "Seed treatment with rhizobium raises yield."),
    "Lentil": ("Rabi (Oct–Mar)", "Low", "Loam", "100–120 days", "Sow after monsoon; avoid excess irrigation."),
    "Pomegranate": ("Year-round (perennial)", "Low–moderate", "Light loam", "2–3 years to fruit", "Drip irrigation and regular pruning give better fruit."),
    "Banana": ("Year-round", "High", "Rich loam", "10–12 months", "Support plants with props; drip irrigation pays off."),
    "Mango": ("Flowers Dec–Feb", "Low–moderate", "Deep loam", "3–5 years to fruit", "Avoid irrigation during flowering."),
    "Grapes": ("Pruning Oct, harvest Feb–Mar", "Moderate", "Well-drained loam", "2–3 years to fruit", "Training on trellis and timely pruning decide quality."),
    "Watermelon": ("Summer (Jan–May)", "Moderate", "Sandy loam", "80–100 days", "Mulch with plastic to save water and control weeds."),
    "Muskmelon": ("Summer (Jan–May)", "Moderate", "Sandy loam", "80–90 days", "Cut irrigation as fruit ripens for sweeter melons."),
    "Apple": ("Temperate hills", "Moderate", "Well-drained loam", "4–6 years to fruit", "Needs winter chilling hours below 7 °C."),
    "Orange": ("Year-round (perennial)", "Moderate", "Light loam", "3–4 years to fruit", "Avoid waterlogging to prevent root rot."),
    "Papaya": ("Year-round", "Moderate", "Well-drained sandy loam", "9–12 months", "Very sensitive to waterlogging; plant on raised beds."),
    "Coconut": ("Year-round", "High", "Sandy coastal loam", "5–7 years to fruit", "Thrives near the coast; mulch with husk to hold moisture."),
    "Cotton": ("Kharif (Jun–Dec)", "Moderate", "Black cotton soil", "150–180 days", "Scout for bollworm every week."),
    "Jute": ("Kharif (Mar–Jul)", "High", "Alluvial loam", "100–120 days", "Needs warm humid weather and standing water for retting."),
    "Coffee": ("Hills, harvest Nov–Feb", "Moderate", "Rich acidic loam", "3–4 years to fruit", "Grow under shade trees; prefers slightly acidic soil."),
    # used only by the fallback dataset
    "Wheat": ("Rabi (Nov–Apr)", "Moderate", "Well-drained loam", "120–150 days", "One irrigation at crown-root stage matters most."),
    "Sugarcane": ("Year-round (12–18 mo)", "High", "Deep loam", "10–18 months", "Trash mulching saves water and keeps weeds down."),
    "Groundnut": ("Kharif / Summer", "Low–moderate", "Light sandy loam", "100–130 days", "Apply gypsum at flowering for better pod filling."),
}
DEFAULT_INFO = ("Varies", "Moderate", "Loam", "Varies", "Follow local agriculture office guidance for this crop.")


def color_for(i, n):
    """Evenly spaced, readable colour for crop number i of n."""
    h = (i / max(n, 1)) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, 0.42 + 0.08 * (i % 2), 0.55)
    return "#%02X%02X%02X" % (int(r * 255), int(g * 255), int(b * 255))


# ---------- fallback dataset (only used if the Kaggle CSV is missing) ----------
_PROFILES = {
    "Rice": [(80, 12), (48, 8), (40, 6), (24, 2.5), (82, 5), (6.4, 0.5), (230, 30)],
    "Wheat": [(100, 14), (50, 8), (38, 7), (18, 2.5), (58, 8), (6.8, 0.4), (80, 18)],
    "Maize": [(78, 12), (48, 8), (20, 5), (22, 3), (65, 8), (6.2, 0.5), (90, 20)],
    "Cotton": [(120, 10), (40, 7), (20, 5), (25, 2.5), (80, 6), (7.0, 0.5), (80, 18)],
    "Sugarcane": [(100, 12), (38, 7), (60, 8), (27, 2.5), (75, 6), (6.8, 0.5), (150, 25)],
    "Chickpea": [(40, 10), (68, 8), (80, 8), (19, 2.5), (22, 6), (7.3, 0.5), (80, 15)],
    "Banana": [(100, 10), (80, 8), (50, 7), (27, 2), (80, 5), (6.0, 0.4), (105, 15)],
    "Groundnut": [(30, 8), (45, 8), (30, 6), (28, 2.5), (65, 7), (6.5, 0.4), (100, 18)],
}


def generate_dataset(n_per_crop=200, seed=42):
    rng = np.random.default_rng(seed)
    frames = []
    for crop, prof in _PROFILES.items():
        cols = {f: np.clip(rng.normal(m, s, n_per_crop), *RANGES[f]).round(2)
                for f, (m, s) in zip(FEATURES, prof)}
        df = pd.DataFrame(cols)
        df["label"] = crop
        frames.append(df)
    return pd.concat(frames, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)
