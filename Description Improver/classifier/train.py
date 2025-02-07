import pandas as pd
from model import DescriptionClassifier
from sklearn.metrics import f1_score, confusion_matrix
from sklearn.model_selection import train_test_split  # new import
import matplotlib.pyplot as plt  # new import
import seaborn as sns  # new import

def main():
    # Load the companies_meta.pkl DataFrame (ensure the file is located one level up)
    print(f"Loading the data...")
    df = pd.read_pickle("../companies_meta_updated.pkl")
    descriptions = df['description'].tolist()  # adjust the column name if necessary
    targets = df['cluster'].tolist()  # column containing the existing cluster labels
    # Compute mapping: each cluster -> meta industry (using mode)
    cluster_map = df.groupby('cluster')['meta_industry'].agg(lambda x: x.mode()[0]).to_dict()

    # Split data into train and test sets
    print(f"Splitting the data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(descriptions, targets, test_size=0.2, random_state=42)

    # Instantiate and train the classifier with training set
    print(f"Fitting the classifier...")
    classifier = DescriptionClassifier()
    classifier.fit(X_train, y_train)
    
    # Predict clusters on test set and display evaluation
    print(f"Evaluating the classifier...")
    predictions = classifier.predict(X_test)
    f1 = f1_score(y_test, predictions, average='weighted')
    
    # Ensure confusion matrix is ordered by clusters present in the mapping
    unique_clusters = sorted(cluster_map.keys())
    cm = confusion_matrix(y_test, predictions, labels=unique_clusters)
    
    # Normalize row-wise: each cell becomes percentage of that row's total
    cm_norm = cm.astype('float') / cm.sum(axis=1, keepdims=True)
    print(f"Weighted F1 Score: {f1}")
    print("Confusion Matrix (raw):")
    print(cm)

    # Plot the normalized confusion matrix with proper labels
    plot_labels = [cluster_map[c] for c in unique_clusters]
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                xticklabels=plot_labels, yticklabels=plot_labels)
    plt.xlabel('Predicted Meta Industry')
    plt.ylabel('True Meta Industry')
    plt.title('Normalized Confusion Matrix (Row-wise Percentage)')
    plt.show()

    # Save the trained classifier to a file
    classifier.save("meta_industry_classifier.pkl")

if __name__ == '__main__':
    main()
