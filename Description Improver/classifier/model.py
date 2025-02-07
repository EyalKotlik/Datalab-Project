import re
#from sklearn.feature_extraction.text import TfidfVectorizer  # removed TFIDF
#from sklearn.linear_model import LogisticRegression  # removed
from sklearn.ensemble import HistGradientBoostingClassifier  # new import
import pickle
#from nltk.stem import WordNetLemmatizer              # removed preprocessing imports
#from nltk.corpus import stopwords                   # removed preprocessing imports
from sentence_bert import SentenceBERT                 # new import

class DescriptionClassifier:
    def __init__(self):
        # Use SentenceBERT for embeddings instead of TFIDF
        self.embedder = SentenceBERT()
        # Replace LogisticRegression with Gradient Boosting Classifier
        self.classifier = HistGradientBoostingClassifier(random_state=42)

    def fit(self, descriptions, targets):
        # Generate embeddings with SentenceBERT and fit the classifier
        X = self.embedder.transform(descriptions)
        self.classifier.fit(X, targets)
        return self

    def predict(self, descriptions):
        # Generate embeddings and predict cluster labels
        X = self.embedder.transform(descriptions)
        return self.classifier.predict(X)

    def save(self, filepath):
        # Save the classifier state
        with open(filepath, 'wb') as f:
            pickle.dump({
                'embedder': self.embedder,
                'classifier': self.classifier
            }, f)
    
    @classmethod
    def load(cls, filepath):
        # Load a saved classifier state
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        instance = cls()
        instance.embedder = data['embedder']
        instance.classifier = data['classifier']
        return instance
