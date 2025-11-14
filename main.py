from typing import Optional, Union, Any
from fastapi import FastAPI
from pydantic import BaseModel
from src.utils import TextPredictor

app = FastAPI()

class PredictionRequest(BaseModel):
    feature1: float
    feature2: float

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/predict/{modality}")
def predict_model(modality: str, inputs: dict[str, Any], options: Optional[dict[str, Any]] = None):
    try:
        if modality == "text":
            text_predictor = TextPredictor()
            if not text_predictor.validate_inputs(inputs, options):
                return {"error": "Invalid inputs for the specified modality."}
            return text_predictor.predict(inputs["input_text"])
        else:
            return {"error": "Unsupported modality."}
    except Exception as e:
        return {"error": str(e)}

@app.get("/predict_async/{modality}")
def predict_model_async(modality: str, inputs: dict[str, Any], options: Optional[dict[str, Any]] = None):
    try:
        if modality == "text":
            text_predictor = TextPredictor()
            if not text_predictor.validate_inputs(inputs, options):
                return {"error": "Invalid inputs for the specified modality."}
            return text_predictor.predict_async(inputs)
        else:
            return {"error": "Unsupported modality."}
    except Exception as e:
        return {"error": str(e)}

