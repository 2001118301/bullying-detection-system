# backend/ai_module.py
import os
import warnings
from PIL import Image

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Check for Mock Mode (for low-memory environments like Render Free Tier)
MOCK_MODE = os.environ.get('MOCK_AI', 'false').lower() == 'true'

text_classifier = None
image_classifier = None

if MOCK_MODE:
    print("WARNING: Running in MOCK AI MODE. Real models will not be loaded.")
else:
    print("Loading AI models... this may take a moment.")
    try:
        from transformers import pipeline
        try:
            text_classifier = pipeline("text-classification", model="unitary/toxic-bert", return_all_scores=True)
            print("AI Text model loaded successfully.")
        except Exception as e:
            print(f"Error loading AI Text model: {e}")

        try:
            image_classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
            print("AI Image model loaded successfully.")
        except Exception as e:
            print(f"Error loading AI Image model: {e}")
            
    except ImportError:
        print("Transformers library not found. Falling back to mock mode.")
        MOCK_MODE = True


def analyze_text(text: str) -> str:
    """
    Analyzes text for toxicity.
    """
    if not text:
        return "No text provided."

    if MOCK_MODE:
        # Simple keyword matching for demo purposes
        bad_words = ['stupid', 'idiot', 'hate', 'kill', 'ugly']
        if any(word in text.lower() for word in bad_words):
            return "Potential bullying detected. Flags: toxic, insult (MOCK)"
        return "No clear bullying indicators detected in text. (MOCK)"

    if not text_classifier:
        return "AI Model not available. (Check logs)"

    try:
        results = text_classifier(text[:512]) # Truncate to 512 tokens for BERT
        scores = results[0]
        toxic_labels = [item['label'] for item in scores if item['score'] > 0.5 and item['label'] != 'neutral']
        
        if toxic_labels:
            return f"Potential bullying detected. Flags: {', '.join(toxic_labels)}"
        
        return "No clear bullying indicators detected in text."
    except Exception as e:
        return f"Error during analysis: {str(e)}"


def analyze_image(image_path: str | None) -> str:
    """
    Analyzes image.
    """
    if not image_path:
        return "No image provided for analysis."
    
    if MOCK_MODE:
        return "Image Analysis: school_supplies (0.95), classroom (0.88) (MOCK)"
    
    if not image_classifier:
        return "AI Image Model not available."

    try:
        image = Image.open(image_path)
        results = image_classifier(image)
        top_labels = [f"{res['label']} ({res['score']:.2f})" for res in results[:3]]
        return f"Image Analysis: {', '.join(top_labels)}"
    except Exception as e:
        return f"Error during image analysis: {str(e)}"
