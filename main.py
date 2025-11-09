from typing import Optional, Union, Any
from fastapi import FastAPI
from pydantic import BaseModel
from src.utils import validate_predict_inputs, predict_text_classification

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
        if not validate_predict_inputs(modality, inputs, options):
            return {"error": "Invalid inputs for the specified modality."}
        return predict_text_classification(inputs["input_text"])
    except Exception as e:
        return {"error": str(e)}

@app.get("/predict_async")
def predict_model_async(feature1: float, feature2: float):
    pass

