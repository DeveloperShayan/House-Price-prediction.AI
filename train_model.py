# This file was missing from the article. It creates the trained model
# file (app/models/house_price_model.pkl) using the California Housing dataset.
# Run it once:  python train_model.py
from pathlib import Path

import joblib
from lightgbm import LGBMRegressor
from sklearn.datasets import fetch_california_housing
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

print("Downloading California Housing data (first time only)...")
X, y = fetch_california_housing(return_X_y=True, as_frame=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("model", LGBMRegressor(n_estimators=500, learning_rate=0.05, random_state=42, verbose=-1)),
])

print("Training the model...")
pipeline.fit(X_train, y_train)
print(f"Model accuracy (R² score): {r2_score(y_test, pipeline.predict(X_test)):.3f}")

out = Path(__file__).parent / "app" / "models" / "house_price_model.pkl"
joblib.dump(pipeline, out)
print(f"Model saved to: {out}")
