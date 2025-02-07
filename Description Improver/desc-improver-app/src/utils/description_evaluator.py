import os
import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer  # added import

# Define a named function for conversion to dense.
def to_dense(x):
    return x.toarray() if hasattr(x, "toarray") else x

# Train evaluator (pipeline) for a specific cluster using companies_meta_updated.
def train_evaluator_for_cluster(cluster_id, companies_meta):
    # Filter rows for the current cluster.
    data = companies_meta[companies_meta["cluster"] == cluster_id]
    if data.empty:
        return None
    # Extract features and target funding.
    descriptions = data["description"].tolist()
    fundings = data["funding"].tolist()
    # Build a pipeline: TfidfVectorizer converts text to features,
    # FunctionTransformer converts sparse matrix to dense,
    # then regressor predicts funding.
    pipeline = make_pipeline(
        TfidfVectorizer(),
        FunctionTransformer(to_dense, accept_sparse=True),
        HistGradientBoostingRegressor(random_state=42)
    )
    pipeline.fit(descriptions, fundings)
    # Calculate and print R2 score for model evaluation.
    r2_score = pipeline.score(descriptions, fundings)
    print(f"Cluster {cluster_id} R2 score: {r2_score:.4f}")
    return pipeline

# Train evaluators for all clusters and save the trained pipelines.
def train_evaluators(companies_meta_path="src/data/companies_meta_updated.pkl", evaluators_dir="src/utils/evaluators"):
    companies_meta = pd.read_pickle(companies_meta_path)
    # Identify unique clusters.
    clusters = companies_meta["cluster"].unique()
    evaluators = {}
    os.makedirs(evaluators_dir, exist_ok=True)
    for cluster_id in clusters:
        pipeline = train_evaluator_for_cluster(cluster_id, companies_meta)
        if pipeline is not None:
            evaluators[cluster_id] = pipeline
            save_path = os.path.join(evaluators_dir, f"evaluator_cluster_{cluster_id}.joblib")
            joblib.dump(pipeline, save_path)
    return evaluators

if __name__ == "__main__":
    evaluators = train_evaluators()
    print("Trained evaluators for clusters:", list(evaluators.keys()))
