from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import json

app = FastAPI(title="Phone & Tablet Resale Estimator API")

# Load model and exact feature column list
model = joblib.load("best_xgb.joblib")
with open("feature_columns.json", "r") as f:
    feature_columns = json.load(f)

class PhoneInput(BaseModel):
    original_price: float
    days_used: int
    screen_size: float
    rear_camera_mp: float
    front_camera_mp: float
    internal_memory: float
    ram: float
    battery: float
    weight: float
    release_year: int
    is_4g: int
    is_5g: int
    brand: str
    os: str
    condition_score: int
    is_working: int
    is_tablet: int = 0

@app.get("/")
def home():
    return {"status": "online", "message": "Resale Value Estimator API"}

@app.post("/predict")
def predict(data: PhoneInput):
    try:
        # 1. Compute normalized_new_price = ln(original_price)
        normalized_new_price = float(np.log(data.original_price))
        
        # 2. Build dictionary matching EXACT features from your training X matrix
        input_dict = {
            'screen_size': data.screen_size,
            '4g': data.is_4g,
            '5g': data.is_5g,
            'rear_camera_mp': data.rear_camera_mp,
            'front_camera_mp': data.front_camera_mp,
            'internal_memory': data.internal_memory,
            'ram': data.ram,
            'battery': data.battery,
            'weight': data.weight,
            'release_year': data.release_year,
            'days_used': data.days_used,
            'normalized_new_price': normalized_new_price,
            'is_tablet': data.is_tablet,
            'condition_score': data.condition_score,
            'working': data.is_working,
            f"device_brand_{data.brand}": 1,
            f"os_{data.os}": 1
        }
        
        df_input = pd.DataFrame([input_dict])
        
        # 3. Align columns with training feature set (fills unselected brands/os dummies with 0)
        X_processed = df_input.reindex(columns=feature_columns, fill_value=0)
        
        # 4. Predict Retention Ratio
        predicted_ratio = float(model.predict(X_processed)[0])
        
        # Clip retention ratio between 2% and 100%
        predicted_ratio = max(0.02, min(1.0, predicted_ratio))
        estimated_resale_price = data.original_price * predicted_ratio
        
        return {
            "original_price": data.original_price,
            "predicted_retention_ratio": round(predicted_ratio, 4),
            "predicted_retention_percentage": f"{round(predicted_ratio * 100, 1)}%",
            "estimated_resale_price": round(estimated_resale_price, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))