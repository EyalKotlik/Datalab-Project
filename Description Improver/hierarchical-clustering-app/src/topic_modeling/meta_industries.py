from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

class MetaIndustries:
    def __init__(self, n_topics=5):
        self.n_topics = n_topics
        self.model = None
        self.vectorizer = None

    def fit(self, documents):
        vectorizer = CountVectorizer()
        data_vectorized = vectorizer.fit_transform(documents)
        self.model = LatentDirichletAllocation(n_components=self.n_topics, random_state=42)
        self.model.fit(data_vectorized)
        self.vectorizer = vectorizer

    def get_meta_industries(self):
        if self.model is None:
            raise RuntimeError("Model has not been fitted yet.")
        feature_names = self.vectorizer.get_feature_names_out()
        meta_industries = {}
        # Extract top 10 words for each topic
        for topic_idx, topic in enumerate(self.model.components_):
            meta_industries[f"Topic {topic_idx}"] = [feature_names[i] for i in topic.argsort()[-10:][::-1]]
        return meta_industries

    def extract(self, data, cluster_labels):
        """
        Aggregates texts of each cluster, fits LDA on each aggregated text,
        and returns the key terms per cluster as a dictionary.
        """
        # Group texts by cluster
        clusters = {}
        for label, text in zip(cluster_labels, data['industries'].tolist()):
            clusters.setdefault(label, []).append(text)
        
        cluster_meta = {}
        # For each cluster, fit LDA on the documents in the cluster
        for label, texts in clusters.items():
            self.fit(texts)
            topics = self.get_meta_industries()
            cluster_meta[f"Cluster {label}"] = topics
        
        return cluster_meta