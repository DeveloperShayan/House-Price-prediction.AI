from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.schemas.house import (BatchRequest, Explanation, HistoryItem,
                               HouseFeatures, HousePrediction, Stats)
from app.services import prediction_service as service

router = APIRouter(prefix="/predict", tags=["House Price Prediction"])


@router.post("/", response_model=HousePrediction, summary="Predict one house and save it")
def predict(data: HouseFeatures):
    return service.predict_house_price(data)


@router.post("/preview", response_model=List[HousePrediction],
             summary="Predict one or more houses WITHOUT saving (used for what-if & compare)")
def preview(request: BatchRequest):
    return service.predict_many(request.items, save=False)


@router.post("/batch", response_model=List[HousePrediction],
             summary="Predict many houses and save them all")
def batch(request: BatchRequest):
    return service.predict_many(request.items, save=True)


@router.post("/explain", response_model=Explanation,
             summary="Explain which features raised or lowered the price")
def explain(data: HouseFeatures):
    try:
        return service.explain(data)
    except Exception as error:
        raise HTTPException(status_code=501, detail=f"Explanation not available: {error}")


@router.get("/history", response_model=List[HistoryItem], summary="Saved predictions from SQL Server")
def history(limit: int = Query(200, ge=1, le=5000)):
    return service.get_history(limit)


@router.get("/stats", response_model=Stats, summary="Summary statistics from SQL Server")
def stats():
    return service.get_stats()
