from utils import TextPredictor
from setup_celery import app

@app.task
def predict_text_input(input_text: str) -> dict:
    """
    Celery task to perform text classification using a pre-trained model.

    Args:
        input_text (str): The text to classify.

    Returns:
        dict: The classification result.
    """
    try:
        text_predictor = TextPredictor()
        return text_predictor.predict(input_text)
    except Exception as e:
        return {"error": str(e)}