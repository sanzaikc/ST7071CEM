"""
Classification Model Service

Implements a supervised text classification pipeline using:
- TF-IDF Vectorization for text representation
- Multinomial Naive Bayes for classification

This approach is academically sound for text classification tasks and provides:
- Explicit class labels (Business, Entertainment, Health)
- Probability/confidence scores for predictions
- Clear separation between training and inference
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from typing import Dict, Tuple, Optional
from .data import get_documents, CATEGORIES


class ClassifierService:
    """
    Supervised text classification service using Multinomial Naive Bayes.
    
    Unlike clustering (unsupervised), this classifier:
    - Uses labeled training data explicitly
    - Learns the relationship between text features and categories
    - Provides probability-based predictions with confidence scores
    """
    
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.classifier: Optional[MultinomialNB] = None
        self.is_trained: bool = False
        self.categories: list = CATEGORIES
        self.training_accuracy: float = 0.0
        self.validation_accuracy: float = 0.0
    
    def train(self, test_size: float = 0.2) -> Dict:
        """
        Train the Multinomial Naive Bayes classifier on labeled documents.
        
        Args:
            test_size: Fraction of data to use for validation (default 20%)
            
        Returns:
            Dictionary containing training metrics and model information
        """
        # 1. Load labeled documents
        documents = get_documents()
        df = pd.DataFrame(documents)
        
        texts = df['text'].tolist()
        labels = df['label'].tolist()
        
        # 2. Split into training and validation sets
        X_train, X_val, y_train, y_val = train_test_split(
            texts, labels, 
            test_size=test_size, 
            random_state=42,
            stratify=labels  # Maintain class distribution
        )
        
        # 3. Text Vectorization using TF-IDF
        # - Converts text to numerical features
        # - Removes English stop words
        # - Uses unigrams for simplicity and interpretability
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            max_features=5000,  # Limit vocabulary size
            ngram_range=(1, 2),  # Unigrams and bigrams
            sublinear_tf=True   # Apply log scaling to term frequency
        )
        
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_val_tfidf = self.vectorizer.transform(X_val)
        
        # 4. Train Multinomial Naive Bayes Classifier
        # - Well-suited for text classification with TF-IDF features
        # - Fast training and prediction
        # - Provides probability estimates
        self.classifier = MultinomialNB(alpha=0.1)  # Laplace smoothing
        self.classifier.fit(X_train_tfidf, y_train)
        
        # 5. Evaluate on training and validation sets
        train_predictions = self.classifier.predict(X_train_tfidf)
        val_predictions = self.classifier.predict(X_val_tfidf)
        
        self.training_accuracy = accuracy_score(y_train, train_predictions)
        self.validation_accuracy = accuracy_score(y_val, val_predictions)
        
        self.is_trained = True
        
        return {
            "status": "trained",
            "algorithm": "Multinomial Naive Bayes",
            "vectorization": "TF-IDF",
            "categories": self.categories,
            "training_samples": len(X_train),
            "validation_samples": len(X_val),
            "training_accuracy": round(self.training_accuracy, 4),
            "validation_accuracy": round(self.validation_accuracy, 4),
            "vocabulary_size": len(self.vectorizer.vocabulary_)
        }
    
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Predict the category of a given text document.
        
        Args:
            text: The input document text to classify
            
        Returns:
            Tuple of (predicted_label, confidence_score)
        """
        if not self.is_trained:
            self.train()
        
        # Vectorize the input text using the fitted vectorizer
        X_new = self.vectorizer.transform([text])
        
        # Get predicted label
        predicted_label = self.classifier.predict(X_new)[0]
        
        # Get probability scores for all classes
        probabilities = self.classifier.predict_proba(X_new)[0]
        
        # Get the confidence (probability) of the predicted class
        label_index = list(self.classifier.classes_).index(predicted_label)
        confidence = float(probabilities[label_index])
        
        return predicted_label, confidence
    
    def predict_with_all_probabilities(self, text: str) -> Dict:
        """
        Predict category and return probabilities for all classes.
        
        Args:
            text: The input document text to classify
            
        Returns:
            Dictionary with prediction details and all class probabilities
        """
        if not self.is_trained:
            self.train()
        
        X_new = self.vectorizer.transform([text])
        predicted_label = self.classifier.predict(X_new)[0]
        probabilities = self.classifier.predict_proba(X_new)[0]
        
        # Map class names to their probabilities
        class_probabilities = {
            cls: round(float(prob), 4) 
            for cls, prob in zip(self.classifier.classes_, probabilities)
        }
        
        label_index = list(self.classifier.classes_).index(predicted_label)
        confidence = float(probabilities[label_index])
        
        return {
            "predicted_label": predicted_label,
            "confidence": round(confidence, 4),
            "probabilities": class_probabilities
        }
    
    def get_feature_importance(self, n_features: int = 10) -> Dict[str, list]:
        """
        Get the most important features (words) for each category.
        
        This helps explain what terms the model associates with each class.
        
        Args:
            n_features: Number of top features to return per class
            
        Returns:
            Dictionary mapping each class to its top features
        """
        if not self.is_trained:
            return {}
        
        feature_names = self.vectorizer.get_feature_names_out()
        top_features = {}
        
        for idx, class_name in enumerate(self.classifier.classes_):
            # Get log probabilities for this class
            log_probs = self.classifier.feature_log_prob_[idx]
            
            # Get indices of top features
            top_indices = np.argsort(log_probs)[-n_features:][::-1]
            
            top_features[class_name] = [feature_names[i] for i in top_indices]
        
        return top_features
    
    def get_model_info(self) -> Dict:
        """
        Get information about the trained model.
        
        Returns:
            Dictionary with model statistics and configuration
        """
        if not self.is_trained:
            return {"status": "not trained"}
        
        return {
            "status": "trained",
            "algorithm": "Multinomial Naive Bayes",
            "categories": list(self.classifier.classes_),
            "training_accuracy": round(self.training_accuracy, 4),
            "validation_accuracy": round(self.validation_accuracy, 4),
            "vocabulary_size": len(self.vectorizer.vocabulary_)
        }


# Global instance - singleton pattern for the classifier service
classifier_service = ClassifierService()
