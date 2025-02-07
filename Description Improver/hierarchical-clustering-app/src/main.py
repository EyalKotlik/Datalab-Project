import pandas as pd
import umap
from clustering.sentence_bert import SentenceBERT
from clustering.agglomerative import AgglomerativeClustering
from topic_modeling.meta_industries import MetaIndustries
from utils.data_loader import load_data
from utils.data_saver import augment_and_save
from evaluation.evaluate_clustering import evaluate_clustering

def main():
    # Load data
    print("Loading data...")
    data = load_data('../../data/full_imputed_linkedin.pkl')
    
    # Generate sentence embeddings
    print("Generating sentence embeddings...")
    sentence_bert = SentenceBERT()
    embeddings = sentence_bert.transform(data['industries'].tolist())
    
    # Ensure embeddings are float32
    print("Converting embeddings to float32...")
    embeddings = embeddings.astype('float32')
    
    # Optionally, you can do dimensionality reduction with UMAP
    # reducer = umap.UMAP(n_components=50, metric='cosine', random_state=42)
    # embeddings = reducer.fit_transform(embeddings)
    
    # Perform clustering
    print("Performing hierarchical agglomerative clustering...")
    clustering = AgglomerativeClustering(n_clusters=40)  # Adjust number of clusters as needed
    cluster_labels = clustering.fit(embeddings)
    
    # Extract meta industries from clustered data
    print("Extracting meta industries...")
    meta_industries = MetaIndustries()
    extracted_meta = meta_industries.extract(data, cluster_labels)
    
    # Augment dataframe with cluster and meta industry names and save result
    output_path = '../../data/companies_meta.pkl'
    augment_and_save(data, cluster_labels, extracted_meta, output_path)
    
    # Evaluate clustering quality
    print("Evaluating clustering quality...")
    score = evaluate_clustering('../../data/full_imputed_linkedin.pkl')
    print("Evaluation Silhouette Score:", score)

if __name__ == "__main__":
    main()