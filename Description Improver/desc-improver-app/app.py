import streamlit as st
import re
from src.utils.prompt_engineering import PromptEngineer
from src.utils.llm_interface import OllamaProvider, GeminiProvider

# Define a named function for conversion to dense.
def to_dense(x):
    return x.toarray() if hasattr(x, "toarray") else x

# Load industries from meta_industry_labels.txt
industries = []
try:
    with open("src/data/meta_industry_labels.txt", "r") as f:
        for line in f:
            # Extract the label after "Cluster <number>:"
            match = re.match(r"Cluster\s+\d+:\s+(.+)", line)
            if match:
                label = match.group(1).strip()
                industries.append(label)
except Exception as e:
    st.error("Error loading industries: " + str(e))
industries = sorted(industries)

# Title of the Web App
st.title("Funding Focused Company Description Enhancer")

api_token = st.text_input("Enter your Gemini API token:", placeholder="Your Gemini API token here...", type="password")

# Step 1: Input for Company Description
description = st.text_area("Enter your company description:", placeholder="Type your company description here...")

# Step 2: Dropdown for Industry Selection with Search
industry = st.selectbox(
    "Select your company's industry (type to search):",
    options=industries
)

# Step 3: Generate Improved Description
if st.button("Generate Improved Description"):
    if not description:
        st.warning("Please enter a company description.")
    elif not api_token:
        st.warning("Please enter your Gemini API token.")
    else:
        # Utilize prompt_engineering to improve the description
        # ollama_provider = OllamaProvider(
        # "token", "http://localhost:11434/api/generate", "deepseek-r1:8b"
        # )
        gemini_provider = GeminiProvider(api_token)
        engineer = PromptEngineer(llm_provider=gemini_provider)
        improved_description = engineer.improve_desc(description, industry)
        
        # Step 4: Display the improved description
        st.subheader("Improved Company Description:")
        st.text_area("Your Enhanced Description:", improved_description, height=150)
