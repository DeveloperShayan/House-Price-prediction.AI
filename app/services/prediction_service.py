from pathlib import Path
from typing import List

import joblib
import pandas as pd
from sqlalchemy import func

from app.schemas.house import HouseFeatures
from app.database.session import SessionLocal
from app.database.models import HousePredictionRecord

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "house_price_model.pkl"

FEATURES = ["MedInc", "HouseAge", "AveRooms", "AveBedrms",
            "Population", "AveOccup", "Latitude", "Longitude"]

model = joblib.load(MODEL_PATH)


# ---------------------------------------------------------------- helpers
def _frame(items: List[HouseFeatures]) -> pd.DataFrame:
    return pd.DataFrame([i.model_dump() for i in items], columns=FEATURES)


def _to_result(value: float) -> dict:
    value = float(value)
    return {
        "predicted_value": round(value, 3),
        "estimated_price_usd": round(value * 100000, 2),
    }


def _save(items: List[HouseFeatures], results: List[dict]) -> None:
    db = SessionLocal()
    try:
        for item, result in zip(items, results):
            db.add(HousePredictionRecord(**item.model_dump(), **result))
        db.commit()
        print(f"Saved {len(items)} record(s) to the database.")
    except Exception as error:
        db.rollback()
        print("DATABASE SAVE FAILED:", repr(error))
        raise
    finally:
        db.close()


# ---------------------------------------------------------------- predictions
def predict_many(items: List[HouseFeatures], save: bool = False) -> List[dict]:
    """Predict several houses at once. Saves them to SQL Server when save=True."""
    results = [_to_result(v) for v in model.predict(_frame(items))]
    if save:
        _save(items, results)
    return results


def predict_house_price(data: HouseFeatures) -> dict:
    """Predict one house and save it to SQL Server."""
    return predict_many([data], save=True)[0]


def explain(data: HouseFeatures) -> dict:
    """Show how much each feature pushed the price up or down (LightGBM SHAP values)."""
    X = _frame([data])
    preprocess, estimator = model[:-1], model[-1]
    contrib = estimator.predict(preprocess.transform(X), pred_contrib=True)[0]
    base = float(contrib[-1])
    total = float(sum(contrib))
    return {
        "estimated_price_usd": round(total * 100000, 2),
        "base_value_usd": round(base * 100000, 2),
        "contributions": [
            {"feature": f, "value": float(X.iloc[0][f]), "impact_usd": round(float(c) * 100000, 2)}
            for f, c in zip(FEATURES, contrib[:-1])
        ],
    }


# ---------------------------------------------------------------- reporting
def get_history(limit: int = 200) -> List[dict]:
    db = SessionLocal()
    try:
        rows = (db.query(HousePredictionRecord)
                .order_by(HousePredictionRecord.id.desc())
                .limit(limit).all())
        return [
            {c: getattr(r, c) for c in
             ["id", *FEATURES, "predicted_value", "estimated_price_usd", "created_at"]}
            for r in rows
        ]
    finally:
        db.close()


def get_stats() -> dict:
    db = SessionLocal()
    try:
        price = HousePredictionRecord.estimated_price_usd
        total, avg, low, high, last = db.query(
            func.count(HousePredictionRecord.id), func.avg(price),
            func.min(price), func.max(price), func.max(HousePredictionRecord.created_at),
        ).one()
        return {"total": total or 0, "average_usd": avg, "min_usd": low,
                "max_usd": high, "last_at": last}
    finally:
        db.close()


if __name__ == "__main__":
    house = HouseFeatures(
        MedInc=5.0, HouseAge=20.0, AveRooms=6.0, AveBedrms=1.0,
        Population=1000.0, AveOccup=3.0, Latitude=34.05, Longitude=-118.25,
    )
    print("Prediction successful!")
    print(predict_house_price(house))
    print("Explanation:", explain(house))
