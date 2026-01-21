
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from .data import get_documents

class ClusterService:
    def __init__(self):
        self.vectorizer = None
        self.kmeans = None
        self.cluster_labels = {}
        self.is_trained = False
        self.documents = []

    def train(self):
        """
        Trains the K-Means clustering model on the collected documents.
        """
        # 1. Load Documents
        raw_docs = get_documents()
        self.documents = pd.DataFrame(raw_docs)
        
        # 2. Vectorize (TF-IDF)
        # Using English stop words as requested/implied for robustness
        # sublinear_tf=True replaces tf with 1 + log(tf)
        # ngram_range=(1, 2) to capture bigrams
        
        custom_stop_words = list(TfidfVectorizer(stop_words='english').get_stop_words())
        custom_stop_words.extend(["announced", "new", "today", "year", "released", "latest", "growing", "rising"])
        
        self.vectorizer = TfidfVectorizer(stop_words=custom_stop_words, sublinear_tf=True, ngram_range=(1, 1), min_df=1)
        X = self.vectorizer.fit_transform(self.documents['text'])

        # 3. Cluster (K-Means)
        # We know we have 3 categories, but using more clusters (e.g. 6) allows for sub-topics
        # (e.g. "Stocks" vs "Corporate", "Movies" vs "Music") which might improve separation.
        # We then map each cluster to the majority category.
        true_k = 9
        self.kmeans = KMeans(n_clusters=true_k, init='k-means++', max_iter=300, n_init=50, random_state=42)
        self.kmeans.fit(X)




        # 4. Map Clusters to Labels
        # Since K-Means is unsupervised, we don't know which cluster is which.
        # We will use the provided labels in the data to assign a label to each cluster
        # based on the majority category of the documents in that cluster.
        
        self.documents['cluster'] = self.kmeans.labels_
        
        # Count categories per cluster
        cluster_map = self.documents.groupby(['cluster', 'category']).size().unstack(fill_value=0)
        
        # Assign label to cluster based on max count
        for cluster_id in range(true_k):
            if cluster_id in cluster_map.index:
                # Get the category with the highest count in this cluster
                predicted_label = cluster_map.loc[cluster_id].idxmax()
                self.cluster_labels[cluster_id] = predicted_label
            else:
                self.cluster_labels[cluster_id] = "Unknown"

        self.is_trained = True
        return {
            "clusters": self.cluster_labels,
            "inertia": self.kmeans.inertia_
        }

    def predict(self, text: str) -> str:
        """
        Predicts the category of a given text.
        """
        if not self.is_trained:
            self.train()
            
        # Vectorize the input
        X_new = self.vectorizer.transform([text])
        
        # Predict cluster
        predicted_cluster = self.kmeans.predict(X_new)[0]
        
        # Map to label
        return self.cluster_labels.get(predicted_cluster, "Unknown")

    def get_top_terms(self, n_terms=10):
        """
        Returns the top terms per cluster (for inspection/debugging).
        """
        if not self.is_trained:
            return {}

        order_centroids = self.kmeans.cluster_centers_.argsort()[:, ::-1]
        terms = self.vectorizer.get_feature_names_out()
        
        top_terms = {}
        for i in range(self.kmeans.n_clusters):
            label = self.cluster_labels.get(i, f"Cluster {i}")
            top_terms[label] = [terms[ind] for ind in order_centroids[i, :n_terms]]
            
        return top_terms

# Global instance
cluster_service = ClusterService()
