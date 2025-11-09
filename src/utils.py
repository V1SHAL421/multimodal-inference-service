from transformers import pipeline
from abc import ABC, abstractmethod

from tasks import predict_text_input

class BasePredictor(ABC):
    @abstractmethod
    def validate_inputs(self, modality: str, inputs: dict, options: dict | None) -> bool:
        pass
    @abstractmethod
    def predict(self, inputs: dict) -> dict:
        pass


class TextPredictor(BasePredictor):
    def __init__(self):
        self.pipeline = pipeline(task="text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
        self.valid_inputs = {"input_text"}

    def validate_inputs(self, inputs: dict, options: dict | None) -> bool:
        """
        Validate inputs based on modality.
        
        Args:
            modality (str): The modality of the prediction (e.g., "text").
            inputs (dict): The input data for prediction.
            options (dict | None): Additional options for prediction.

        Returns:
            bool: True if inputs are valid for the modality, False otherwise.
        """
        try:
            for input in inputs:
                if input not in self.valid_inputs:
                    return False
            return True
        except Exception:
            return False

    def predict(self, input_text: str) -> dict:
        """
        Perform text classification using a pre-trained model.

        Args:
            input_text (str): The text to classify.

        Returns:
            dict: The classification result.
        """
        try:
            result = self.pipeline(input_text)[0]
            return {"label": result['label'], "score": result['score']}
        except Exception as e:
            return {"error": str(e)}


    def predict_async(self, inputs: dict) -> dict:
        """
        Placeholder for asynchronous prediction method.

        Args:
            inputs (dict): The input data for prediction.
        Returns:
            dict: The prediction result.
        """
        try:
            result = predict_text_input.delay(inputs["input_text"])
            return {"task_id": result.id}
        except Exception as e:
            return {"error": str(e)}