import pandas as pd
import numpy as np
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from nltk.stem import PorterStemmer  # changed: using stemming instead of lemmatization
import re


print("Loading data...")
# Load data
file_path = "../data/companies_meta_updated.pkl"
data = pd.read_pickle(file_path)

# Preprocess text: fill missing and apply stemming.
data["description"] = data["description"].fillna("")

# Updated preprocessing: using stemming for word normalization.
stemmer = PorterStemmer()
def stem_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    stemmed = [stemmer.stem(token) for token in tokens]
    return " ".join(stemmed)
data["text"] = data["description"].apply(stem_text)

# Dictionary to store word effects by cluster.
cluster_word_effects = {}

# Group by cluster column (assumed column name 'cluster')
for cluster, group in data.groupby("cluster"):
    texts = group["text"].values
    y_funding = group["funding"].values
    if len(texts) < 5:
        continue
    
    # Vectorize text using TF-IDF.
    vectorizer = TfidfVectorizer(stop_words="english", max_features=1000, strip_accents="unicode")
    X = vectorizer.fit_transform(texts)
    
    # Train Ridge regression to capture word effect.
    model = Ridge()
    model.fit(X, y_funding)
    
    # Map each word to its impact (coefficient).
    word_effect = dict(zip(vectorizer.get_feature_names_out(), model.coef_))
    
    # Sort words by absolute impact (preserving sign).
    sorted_effects = sorted(word_effect.items(), key=lambda x: abs(x[1]), reverse=True)
    cluster_word_effects[str(cluster)] = sorted_effects

# Save the resulting word effects for each cluster.
with open("../data/cluster_word_effects.json", "w") as f:
    json.dump(cluster_word_effects, f, indent=2)

print("Word effects for each cluster saved to cluster_word_effects.json")
