from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class HouseFeatures(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float


class HousePrediction(BaseModel):
    predicted_value: float
    estimated_price_usd: float


class BatchRequest(BaseModel):
    items: List[HouseFeatures] = Field(..., min_length=1, max_length=1000)


class FeatureContribution(BaseModel):
    feature: str
    value: float
    impact_usd: float


class Explanation(BaseModel):
    estimated_price_usd: float
    base_value_usd: float
    contributions: List[FeatureContribution]


class HistoryItem(HouseFeatures):
    id: int
    predicted_value: float
    estimated_price_usd: float
    created_at: Optional[datetime] = None


class Stats(BaseModel):
    total: int
    average_usd: Optional[float] = None
    min_usd: Optional[float] = None
    max_usd: Optional[float] = None
    last_at: Optional[datetime] = None


if __name__ == "__main__":
    house = HouseFeatures(
        MedInc=5.0, HouseAge=20.0, AveRooms=6.0, AveBedrms=1.0,
        Population=1000.0, AveOccup=3.0, Latitude=34.05, Longitude=-118.25,
    )
    print("Schema created successfully!")
    print(house)
    print(house.model_dump())
