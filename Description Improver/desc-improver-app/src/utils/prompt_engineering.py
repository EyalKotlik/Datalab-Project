import random
import time
import json
import re
import joblib  # import for loading evaluators
from nltk.stem import PorterStemmer
from src.utils.llm_interface import OllamaProvider, OpenAIProvider

# Updated choose_word_changes: it now computes word impact scores along with top recommended words,
# then creates a prompt message to be passed to the LLM.
def choose_word_changes(description, industry):
    # Load cluster word effects mapping.
    with open("src/data/cluster_word_effects.json", "r") as f:
        cluster_word_effects = json.load(f)
        
    # Load meta industry labels mapping.
    meta_mapping = {}
    with open("src/data/meta_industry_labels.txt", "r") as f:
        for line in f:
            match = re.match(r"Cluster\s+(\d+):\s+(.+)", line)
            if match:
                cluster = match.group(1)
                label = match.group(2).strip().lower()
                meta_mapping[label] = cluster

    # Process description using stemming.
    stemmer = PorterStemmer()
    desc_processed = description.lower()
    desc_processed = re.sub(r'[^a-z\s]', '', desc_processed)
    tokens = desc_processed.split()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    
    # Determine the cluster by matching the provided industry with meta labels.
    chosen_cluster = None
    for meta_label, cluster in meta_mapping.items():
        if industry.lower() in meta_label or meta_label in industry.lower():
            chosen_cluster = cluster
            break
    if chosen_cluster is None:
        return {"changes_prompt": "No matching cluster found for provided industry."}
    
    # Get word effects for the chosen cluster.
    effects_list = cluster_word_effects.get(chosen_cluster, [])
    effects_dict = {word: float(effect) for word, effect in effects_list}
    
    # Compute scores for each stemmed word in the description.
    word_scores = {token: effects_dict.get(token, 0.0) for token in stemmed_tokens}
    # Identify candidate positive-impact words not present in the description.
    positive_candidates = [
        word for word, effect in sorted(effects_dict.items(), key=lambda x: x[1], reverse=True)
        if effect > 0 and word not in stemmed_tokens
    ]
    
    # Select the top 20% of words with a positive effect.
    top_20_percent_index = max(1, int(len(positive_candidates) * 0.2))
    positive_candidates = positive_candidates[:top_20_percent_index]

    # For the prompt, choose 10 sample words randomly from the candidate pool.
    if len(positive_candidates) >= 10:
        recommended_added_words = random.sample(positive_candidates, 10)
    else:
        recommended_added_words = positive_candidates

    # Build a dynamic prompt text to pass to the LLM.
    changes_prompt = (
        f"Word Impact Analysis (using stemmed words):\n"
        f"Stemmed Scores: {word_scores}\n"
        f"Suggested positive stemmed words to consider adding: {recommended_added_words}\n"
        f"Industry Context: {industry}\n"
        f"Please suggest modifications to the description based on the above.\n"
        f"The goal is to enhance the description based on our recommendation while keeping it focused on the core ideas presented in the original description.\n" 
        f"You should add and remove words according to the scores provided, removing words with negative scores and trying to add some from the suggested words.\n"
        f"Remember, our suggestions are stemmed, so you may need to adjust them to fit the context.\n"
        f"Feel free to sligthly lengthen the description if needed.\n"
        f"Output only the improved description.\n"
    )
    
    return {"changes_prompt": changes_prompt}

def load_meta_mapping(mapping_path="src/data/meta_industry_labels.txt"):
    meta_mapping = {}
    with open(mapping_path, "r") as f:
        for line in f:
            match = re.match(r"Cluster\s+(\d+):\s+(.+)", line)
            if match:
                cluster = match.group(1)
                label = match.group(2).strip().lower()
                meta_mapping[label] = cluster
    return meta_mapping

class PromptEngineer:
    # Modified constructor to accept an external llm provider.
    def __init__(self, llm_provider=None):
        # If no provider is supplied, use a simulated LLM.
        self.llm = llm_provider

    # New implementation: evaluates a candidate based on the evaluator for its industry.
    def evaluate_candidate(self, candidate, industry):
        meta_mapping = load_meta_mapping()
        chosen_cluster = None
        for meta_label, cluster in meta_mapping.items():
            if industry.lower() in meta_label or meta_label in industry.lower():
                chosen_cluster = cluster
                break
        if chosen_cluster is None:
            return 0  # fallback score if no cluster found
        evaluator_path = f"src/utils/evaluators/evaluator_cluster_{chosen_cluster}.joblib"
        try:
            evaluator = joblib.load(evaluator_path)
            # evaluator.predict expects a list of texts; get the first prediction.
            predicted_funding = evaluator.predict([candidate])[0]
            return predicted_funding
        except Exception as e:
            print(f"Error loading evaluator for cluster {chosen_cluster}: {e}")
            return 0

    # Retained simulation method for fallback if no provider given.
    def simulate_llm(self, prompt):
        time.sleep(0.1)  # simulate processing delay
        return prompt + " [LLM revised]"

    # Unified method to send prompt using either the external llm or simulator.
    def send_to_llm(self, prompt):
        if self.llm is not None:
            print("Sending prompt to external LLM provider.")
            return self.llm.send_prompt(prompt)
        else:
            print("Sending prompt to simulated LLM.")
            return self.simulate_llm(prompt)

    def improve_desc(self, original_description, industry, iterations=3):
        best_candidate = original_description
        best_score = self.evaluate_candidate(original_description, industry)
        base_prompt = f"Industry: {industry}. Original Description: {original_description}"
        for i in range(iterations):
            changes = choose_word_changes(best_candidate, industry)
            changes_prompt = changes.get("changes_prompt", "")
            refined_prompt = f"{base_prompt}\nCurrent best description: {best_candidate}\nAdditional context:\n{changes_prompt}"
            print(f"\nIteration {i+1} prompt:\n{refined_prompt}")
            candidate = self.send_to_llm(refined_prompt).split("</think>")[-1]
            score = self.evaluate_candidate(candidate, industry)
            base_prompt = base_prompt + f"\nCandidate {i+1} Description: {candidate} Candidate Score: {score}"
            if score > best_score:
                best_score = score
                best_candidate = candidate
        return best_candidate

# ...existing code...
if __name__ == "__main__":
    # Example: You can integrate an external LLM provider (such as OllamaProvider)
    # by importing and providing it here. For now, if none is provided, the simulation is used.
    ollama_provider = OllamaProvider(
        "token", "http://localhost:11434/api/generate", "deepseek-r1:8b"
    )
    engineer = PromptEngineer(llm_provider=ollama_provider)
    original = "This is the original description."
    industry = "Oil & Gas"
    improved = engineer.improve_desc(original, industry)
    print("Improved Prompt:", improved)
