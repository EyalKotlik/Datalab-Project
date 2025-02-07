import pandas as pd
import pickle as pkl

def load_data(file_path):
    """Load data from a PKL file."""
    data = pkl.load(open(file_path, 'rb'))
    return data

def preprocess_data(data):
    """Preprocess the data for analysis."""
    # Example preprocessing steps
    data = data.dropna()  # Remove missing values
    data['industries'] = data['industries'].str.lower()  # Convert industries to lowercase
    return data

def load_and_preprocess(file_path):
    """Load and preprocess data from a given file path."""
    data = load_data(file_path)
    processed_data = preprocess_data(data)
    return processed_data