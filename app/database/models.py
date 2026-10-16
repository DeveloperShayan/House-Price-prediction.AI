from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class HousePredictionRecord(Base):
    __tablename__ = "HousePredictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    MedInc: Mapped[float] = mapped_column(Float, nullable=False)
    HouseAge: Mapped[float] = mapped_column(Float, nullable=False)
    AveRooms: Mapped[float] = mapped_column(Float, nullable=False)
    AveBedrms: Mapped[float] = mapped_column(Float, nullable=False)
    Population: Mapped[float] = mapped_column(Float, nullable=False)
    AveOccup: Mapped[float] = mapped_column(Float, nullable=False)
    Latitude: Mapped[float] = mapped_column(Float, nullable=False)
    Longitude: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
