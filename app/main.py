from fastapi import FastAPI

from app.routers.prediction import router as prediction_router

app = FastAPI(
    title="EstateIQ – House Price Prediction API",
    description="Predict, explain, compare and batch-value house prices. Built by Shayan Niaz.",
    version="2.0.0",
)


@app.get("/")
def home():
    return {"message": "House Price Prediction API is running!"}


app.include_router(prediction_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
