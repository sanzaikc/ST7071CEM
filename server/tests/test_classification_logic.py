"""
Test suite for the supervised text classification module.

This replaces the previous clustering tests with proper classification tests.
The classifier uses Multinomial Naive Bayes with TF-IDF vectorization.
"""

import sys
import os

# Add server directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classification.model import classifier_service


def test_classification():
    """
    Test the text classification model.
    
    This test:
    1. Trains the Naive Bayes classifier on labeled data
    2. Checks model performance metrics
    3. Tests predictions on sample documents
    4. Verifies confidence scores are returned
    """
    print("=" * 60)
    print("TEXT CLASSIFICATION TEST - Multinomial Naive Bayes")
    print("=" * 60)
    
    # Train the model
    print("\n[1] Training classifier...")
    result = classifier_service.train()
    
    print(f"    Algorithm: {result['algorithm']}")
    print(f"    Vectorization: {result['vectorization']}")
    print(f"    Categories: {result['categories']}")
    print(f"    Training samples: {result['training_samples']}")
    print(f"    Validation samples: {result['validation_samples']}")
    print(f"    Training accuracy: {result['training_accuracy']:.2%}")
    print(f"    Validation accuracy: {result['validation_accuracy']:.2%}")
    print(f"    Vocabulary size: {result['vocabulary_size']}")
    
    # Get feature importance (top terms per class)
    print("\n[2] Top features per class:")
    top_features = classifier_service.get_feature_importance(10)
    for label, terms in top_features.items():
        print(f"    {label}: {', '.join(terms[:5])}...")
    
    # Test prediction on sample documents
    print("\n[3] Testing predictions on sample documents:")
    print("-" * 60)
    
    test_cases = [
        # Business examples
        ("The company's stock rose by 5% due to strong quarterly earnings.", "Business"),
        ("Apple announced record revenue and increased dividends for shareholders.", "Business"),
        ("Inflation is a major concern for the central bank policy makers.", "Business"),
        ("The Federal Reserve raised interest rates to combat rising prices.", "Business"),
        ("Tech startups are attracting significant venture capital investments.", "Business"),
        
        # Entertainment examples
        ("The new movie released this weekend is a box office hit with audiences.", "Entertainment"),
        ("The singer performed live at the stadium to a sold-out crowd.", "Entertainment"),
        ("The actor won an award for best performance at the ceremony.", "Entertainment"),
        ("The streaming service announced a new original series starring famous actors.", "Entertainment"),
        ("Fans are excited about the upcoming sequel to the popular franchise.", "Entertainment"),
        
        # Health examples
        ("Eating vegetables and exercising daily improves heart health significantly.", "Health"),
        ("Flu vaccination rates are lower than expected this season.", "Health"),
        ("Diabetes requires careful monitoring of blood sugar levels daily.", "Health"),
        ("New research shows meditation reduces stress and improves mental wellness.", "Health"),
        ("Doctors recommend regular check-ups to detect health problems early.", "Health"),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for text, expected in test_cases:
        label, confidence = classifier_service.predict(text)
        is_correct = label == expected
        status = "✓" if is_correct else "✗"
        
        if is_correct:
            correct += 1
        
        # Truncate text for display
        display_text = text[:50] + "..." if len(text) > 50 else text
        print(f"    {status} '{display_text}'")
        print(f"      Predicted: {label} ({confidence:.1%}) | Expected: {expected}")
    
    accuracy = correct / total
    print("-" * 60)
    print(f"\n[4] Test Results:")
    print(f"    Correct: {correct}/{total}")
    print(f"    Accuracy: {accuracy:.1%}")
    
    # Verify model info
    print("\n[5] Model Info:")
    info = classifier_service.get_model_info()
    for key, value in info.items():
        print(f"    {key}: {value}")
    
    print("\n" + "=" * 60)
    if accuracy >= 0.8:
        print("TEST PASSED: Classification accuracy is acceptable (≥80%)")
    else:
        print("TEST WARNING: Classification accuracy is below 80%")
    print("=" * 60)
    
    return accuracy >= 0.8


def test_predict_with_probabilities():
    """Test the predict_with_all_probabilities method."""
    print("\n[EXTRA] Testing probability output for a sample document:")
    
    sample_text = "The stock market reached new highs as investors remained optimistic."
    result = classifier_service.predict_with_all_probabilities(sample_text)
    
    print(f"    Text: '{sample_text}'")
    print(f"    Predicted label: {result['predicted_label']}")
    print(f"    Confidence: {result['confidence']:.1%}")
    print(f"    All probabilities:")
    for cls, prob in result['probabilities'].items():
        print(f"      - {cls}: {prob:.1%}")


if __name__ == "__main__":
    test_classification()
    test_predict_with_probabilities()
