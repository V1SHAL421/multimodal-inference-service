from transformers import pipeline 

def validate_predict_inputs(modality: str, inputs: dict, options: dict | None) -> bool:
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
        modalities_to_inputs = {
            "text": ["input_text"]
        }
        
        if modality not in modalities_to_inputs:
            return False
        valid_inputs = modalities_to_inputs[modality]
        for input in inputs:
            if input not in valid_inputs:
                return False
        return True
    except Exception:
        return False

def predict_text_classification(input_text: str) -> dict:
    """
    Perform text classification using a pre-trained model.

    Args:
        input_text (str): The text to classify.

    Returns:
        dict: The classification result.
    """
    try:
        pipe = pipeline(task="text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
        result = pipe(input_text)[0]
        return {"label": result['label'], "score": result['score']}
    except Exception as e:
        return {"error": str(e)}