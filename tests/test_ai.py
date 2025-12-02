# backend/test_ai.py
from ai_module import analyze_text

def test_ai():
    print("Testing AI Module...")
    
    # Test Case 1: Neutral / Positive text
    text1 = "I hope you have a wonderful day at school."
    print(f"\nInput: {text1}")
    result1 = analyze_text(text1)
    print(f"Result: {result1}")
    
    # Test Case 2: Toxic text
    text2 = "You are stupid and ugly, nobody likes you."
    print(f"\nInput: {text2}")
    result2 = analyze_text(text2)
    print(f"Result: {result2}")
    
    # Test Case 3: Threat
    text3 = "I am going to hurt you after class."
    print(f"\nInput: {text3}")
    result3 = analyze_text(text3)
    print(f"Result: {result3}")

if __name__ == "__main__":
    test_ai()
