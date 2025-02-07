import pandas as pd

def augment_and_save(data: pd.DataFrame, cluster_labels, extracted_meta, output_path: str):
    """
    Adds cluster and meta industry columns to data and saves it as a pickle file.
    
    extracted_meta: dict mapping "Cluster {id}" to a topics dictionary.
    For demonstration, we take the top words from "Topic 0" of each cluster.
    """
    # Add cluster labels column
    data['cluster'] = cluster_labels

    # Build a mapping from cluster id to a meaningful meta industry name.
    meta_mapping = {}
    for key, topics in extracted_meta.items():
        # key format: "Cluster {label}"
        try:
            cluster_label = int(key.split()[1])
        except (IndexError, ValueError):
            continue
        
        # For demonstration, use the top words from the first topic (Topic 0)
        first_topic = topics.get("Topic 0", [])
        meta_name = ", ".join(first_topic)
        meta_mapping[cluster_label] = meta_name

    # Add meta industry column
    data['meta_industry'] = data['cluster'].map(meta_mapping)
    
    # Save augmented dataframe
    data.to_pickle(output_path)
    print(f"Saved augmented data to {output_path}")