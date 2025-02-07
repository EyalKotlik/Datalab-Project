import re
import statistics
import pandas as pd

path = "../data/companies_meta_updated.pkl"
data = pd.read_pickle(path)
print(data.head())