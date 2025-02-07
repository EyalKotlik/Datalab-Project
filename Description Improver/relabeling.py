import pandas as pd

# Load the existing companies_meta.pkl DataFrame
df = pd.read_pickle('data/companies_meta.pkl')

# Read the updated meta industry labels from the text file and create a mapping
label_mapping = {}
with open('meta_industry_labels.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Expected format: "Cluster X: Label"
        parts = line.split(':', 1)
        if len(parts) != 2:
            continue
        cluster_str, label = parts
        # Remove "Cluster" word and extra spaces to get the cluster number
        try:
            cluster_id = int(cluster_str.replace("Cluster", "").strip())
            label_mapping[cluster_id] = label.strip()
        except ValueError:
            continue

# Update the meta_industry column using the mapping based on the cluster column
df['meta_industry'] = df['cluster'].map(label_mapping)

# Save the updated dataframe to a new pickle file
output_path = 'data/companies_meta_updated.pkl'
df.to_pickle(output_path)
print(f"Updated meta industry labels saved to {output_path}")