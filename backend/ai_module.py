# backend/ai_module.py
from transformers import pipeline
from PIL import Image
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Initialize the toxicity detection pipeline
print("Loading AI models... this may take a moment.")
try:
    text_classifier = pipeline("text-classification", model="unitary/toxic-bert", return_all_scores=True)
    print("AI Text model loaded successfully.")
except Exception as e:
    print(f"Error loading AI Text model: {e}")
    text_classifier = None

# Initialize Image Classification pipeline
try:
    # Using a standard ViT model for general object/scene classification
    # For bullying, we might want a specific model, but for this demo, general classification proves the integration.
    image_classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
    print("AI Image model loaded successfully.")
except Exception as e:
    print(f"Error loading AI Image model: {e}")
    image_classifier = None


def analyze_text(text: str) -> str:
    """
    Analyzes text for toxicity using a pre-trained BERT model.
    Returns a summary string of the findings.
    """
    if not text:
        return "No text provided."

    if not text_classifier:
        return "AI Model not available. (Check logs)"

    try:
        results = text_classifier(text[:512]) # Truncate to 512 tokens for BERT
        # results is a list of lists of dicts: [[{'label': 'toxic', 'score': 0.9}, ...]]
        scores = results[0]
        
        # Filter for high confidence toxicity
        toxic_labels = [item['label'] for item in scores if item['score'] > 0.5 and item['label'] != 'neutral']
        
        if toxic_labels:
            return f"Potential bullying detected. Flags: {', '.join(toxic_labels)}"
        
        return "No clear bullying indicators detected in text."
    except Exception as e:
        return f"Error during analysis: {str(e)}"


def analyze_image(image_path: str | None) -> str:
    """
    Analyzes image using a pre-trained ViT model.
    """
    if not image_path:
        return "No image provided for analysis."
    
    if not image_classifier:
        return "AI Image Model not available."

    try:
        image = Image.open(image_path)
        results = image_classifier(image)
        # results is a list of dicts: [{'score': 0.9, 'label': '...'}, ...]
        
        # Get top 3 labels
        top_labels = [f"{res['label']} ({res['score']:.2f})" for res in results[:3]]
        
        return f"Image Analysis: {', '.join(top_labels)}"
    except Exception as e:
        return f"Error during image analysis: {str(e)}"
