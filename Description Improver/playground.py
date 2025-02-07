import pandas as pd
import pickle as pkl

data = pkl.load(open('data/companies_meta_updated.pkl', 'rb'))
print(data.head())
print(data.columns)

# Count unique clusters in the data
unique_clusters = data['cluster'].nunique()
print(f"Number of unique clusters: {unique_clusters}")

# Extract unique meta industries for each cluster and save to a text file
# industries_by_cluster = data.groupby('cluster')['meta_industry'].unique()
# with open('unique_meta_industries.txt', 'w') as f:
#   for cluster, industries in industries_by_cluster.items():
#       f.write(f"Cluster {cluster}: {', '.join(industries)}\n")
