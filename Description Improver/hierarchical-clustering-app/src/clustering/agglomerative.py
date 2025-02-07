class AgglomerativeClustering:
    def __init__(self, n_clusters=2, n_neighbors=10):
        self.n_clusters = n_clusters
        self.n_neighbors = n_neighbors
        self.labels_ = None

    def fit(self, embeddings):
        from sklearn.cluster import AgglomerativeClustering as SklearnAgglomerativeClustering
        from sklearn.neighbors import kneighbors_graph
        
        # Build a connectivity graph using k-NN; this limits pairwise distance computations
        connectivity = kneighbors_graph(embeddings, n_neighbors=self.n_neighbors, include_self=False)
        
        model = SklearnAgglomerativeClustering(
            n_clusters=self.n_clusters,
            connectivity=connectivity
        )
        self.labels_ = model.fit_predict(embeddings)
        return self.labels_

    def get_labels(self):
        return self.labels_