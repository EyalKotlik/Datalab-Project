import pandas as pd
from sklearn.metrics import silhouette_score
from utils.data_loader import load_data
from clustering.sentence_bert import SentenceBERT
from clustering.agglomerative import AgglomerativeClustering

def evaluate_clustering(data_source):
    # Load raw data
    data = load_data(data_source)
    # Generate sentence embeddings
    sentence_bert = SentenceBERT()
    embeddings = sentence_bert.transform(data['industries'].tolist())
    embeddings = embeddings.astype('float32')
    # Perform clustering with 30 clusters (for evaluation purposes)
    clustering = AgglomerativeClustering(n_clusters=30)
    cluster_labels = clustering.fit(embeddings)
    # Calculate silhouette score using cosine metric
    score = silhouette_score(embeddings, cluster_labels, metric='cosine')
    print("Silhouette Score:", score)
    return score
