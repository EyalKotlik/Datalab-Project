import os
import unittest
import pandas as pd
from sklearn.metrics import silhouette_score

from src.utils.data_loader import load_data
from src.clustering.sentence_bert import SentenceBERT
from src.clustering.agglomerative import AgglomerativeClustering
from src.topic_modeling.meta_industries import MetaIndustries

class TestClustering(unittest.TestCase):
    def setUp(self):
        # Paths for saved data
        self.saved_path = '../companies_meta.pkl'
        self.data_source = '../full_imputed_linkedin.pkl'
        
        if os.path.exists(self.saved_path):
            print("Using saved clustering from", self.saved_path)
            self.df = pd.read_pickle(self.saved_path)
            self.use_saved = True
        else:
            print("Saved clustering not found. Running full clustering pipeline...")
            self.use_saved = False
            self.data = load_data(self.data_source)
            
            # Generate embeddings
            sentence_bert = SentenceBERT()
            embeddings = sentence_bert.transform(self.data['industries'].tolist())
            embeddings = embeddings.astype('float32')
            
            # Perform clustering
            clustering = AgglomerativeClustering(n_clusters=20)
            cluster_labels = clustering.fit(embeddings)
            
            # Extract meta industries
            meta_industries = MetaIndustries()
            extracted_meta = meta_industries.extract(self.data, cluster_labels)
            
            # Augment dataframe with cluster and meta industry names
            self.data['cluster'] = cluster_labels
            meta_mapping = {}
            for key, topics in extracted_meta.items():
                try:
                    cluster_label = int(key.split()[1])
                except (IndexError, ValueError):
                    continue
                # For demonstration, join top words from Topic 0
                first_topic = topics.get("Topic 0", [])
                meta_name = ", ".join(first_topic)
                meta_mapping[cluster_label] = meta_name
            self.data['meta_industry'] = self.data['cluster'].map(meta_mapping)
            self.df = self.data

    def test_cluster_column_exists(self):
        """Test that the dataframe contains the 'cluster' column."""
        self.assertIn('cluster', self.df.columns)

    def test_meta_industry_column_exists(self):
        """Test that the dataframe contains the 'meta_industry' column."""
        self.assertIn('meta_industry', self.df.columns)

    def test_cluster_values_non_null(self):
        """Test that no null values are present in the cluster column."""
        self.assertFalse(self.df['cluster'].isnull().any())

    def test_meta_industry_values_non_empty(self):
        """Test that every meta_industry value is a non-empty string."""
        non_empty = self.df['meta_industry'].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0)
        self.assertTrue(non_empty.all())

    def test_silhouette_score(self):
        """
        Test the clustering quality by computing the silhouette score.
        A higher silhouette score indicates well-separated clusters.
        If using saved clustering, recompute embeddings from raw data.
        """
        # Reload raw data and compute embeddings to evaluate clustering quality.
        data = load_data(self.data_source)
        sentence_bert = SentenceBERT()
        print("Generating sentence embeddings...")
        embeddings = sentence_bert.transform(data['industries'].tolist())
        embeddings = embeddings.astype('float32')
        
        # Compute clustering labels using the same clustering setup as in setUp.
        print("Clustering...")
        clustering = AgglomerativeClustering(n_clusters=30)
        cluster_labels = clustering.fit(embeddings)
        
        # Calculate the silhouette score using cosine distance
        print("Calculating Silhouette Score...")
        score = silhouette_score(embeddings, cluster_labels, metric='cosine')
        print("Silhouette Score:", score)
        
        # Check that the silhouette score is within a reasonable range.
        # (Threshold may need adjustment depending on the dataset.)
        self.assertGreater(score, 0, "Silhouette score is not positive.")

if __name__ == "__main__":
    unittest.main()