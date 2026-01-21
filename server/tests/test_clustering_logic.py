
import sys
import os

# Add server directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clustering.model import cluster_service

def test_clustering():
    print("Training model...")
    res = cluster_service.train()
    print("Training result:", res)
    
    print("Top terms per cluster:")
    top_terms = cluster_service.get_top_terms(10)
    for label, terms in top_terms.items():
        print(f"{label}: {terms}")

    test_cases = [

        ("The company's stock rose by 5% due to strong earnings.", "Business"),
        ("The new movie released this weekend is a box office hit.", "Entertainment"),
        ("Eating vegetables and exercising daily improves heart health.", "Health"),
        ("Apple announced a new iPhone today.", "Business"),
        ("The singer performed live at the stadium.", "Entertainment"),
        ("Flu vaccination rates are low this season.", "Health"),
        ("Inflation is a major concern for the central bank.", "Business"),
        ("The actor won an award for best performance.", "Entertainment"),
        ("Diabetes requires careful monitoring of sugar levels.", "Health")
    ]
    
    correct = 0
    for text, expected in test_cases:
        prediction = cluster_service.predict(text)
        print(f"Text: '{text}' -> Predicted: {prediction} (Expected: {expected})")
        if prediction == expected:
            correct += 1
            
    print(f"Accuracy on test cases: {correct}/{len(test_cases)}")
        
if __name__ == "__main__":
    test_clustering()
