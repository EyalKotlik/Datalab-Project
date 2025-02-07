import os
import json
from abc import ABC, abstractmethod
from openai import OpenAI
import google.generativeai as genai
import requests


import requests  # new import for OpenWebUI HTTP requests

def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

# Abstract LLM provider interface e
class LLMProvider(ABC):
    def __init__(self, api_token):
        self.api_token = api_token

    @abstractmethod
    def send_prompt(self, prompt: str) -> str:
        pass

# Implementation for OpenAI with persistent conversation history.
class OpenAIProvider(LLMProvider):
    def __init__(self, api_token):
        super().__init__(api_token)
        self.message_history = [
            {"role": "system", "content": "You are an assistant."}
        ]

    def send_prompt(self, prompt: str) -> str:
        # Append user's message to history.
        self.message_history.append({"role": "user", "content": prompt})
        # Combine conversation history into a single text.
        conversation_text = "\n".join([
            f"{m['role'].capitalize()}: {m['content']}" for m in self.message_history
        ])
        # Call the Completion endpoint instead of ChatCompletion.
        response = client.completions.create(model="gpt-3.5-turbo-instruct",
        prompt=conversation_text + "\nAssistant:",
        max_tokens=150,
        temperature=0.7,
        stop=["User:", "Assistant:"])
        message = response.choices[0].text.strip()
        # Append assistant's reply to history.
        self.message_history.append({"role": "assistant", "content": message})
        return message

# Updated implementation for GeminiProvider using a hypothetical Gemini API endpoint.

class GeminiProvider(LLMProvider):
    def __init__(self, api_token):
        super().__init__(api_token)
        genai.configure(api_key=api_token)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def send_prompt(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

# Reworked implementation for OllamaProvider using ollama-python package with adjusted base_url
class OllamaProvider(LLMProvider):
    def __init__(self, api_token, base_url, model):
        super().__init__(api_token)
        self.base_url = base_url
        self.model = model  # e.g., "deepseek-r1:7b"
        # Pass the base_url as is without appending '/api'
        self.message_history = [{"role": "system", "content": "You are an assistant."}]

    def send_prompt(self, prompt: str) -> str:
        self.message_history.append({"role": "user", "content": prompt})
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            }
            result = requests.post(self.base_url, json=payload, timeout=30)
            result.raise_for_status()
            reply = result.json().get("response", "")
        except Exception as e:
            reply = f"Error calling Ollama: {e}"
            raise e
        self.message_history.append({"role": "assistant", "content": reply})
        return reply

def get_llm_provider(config):
    provider = config.get("provider", "openai").lower()
    token = config.get("api_token", "")
    if provider == "openai":
        return OpenAIProvider(token)
    elif provider == "gemini":
        return GeminiProvider(token)
    elif provider == "ollama":
        base_url = config.get("ollama_url", "http://localhost:11434")
        model = config.get("ollama_model", "llama2")
        return OllamaProvider(token, base_url, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def conversation_loop(llm):
    print("Starting conversation with the LLM. Type 'exit' to quit.")
    while True:
        user_input = input("User: ").strip()
        if user_input.lower() == "exit":
            print("Conversation ended.")
            break
        response = llm.send_prompt(user_input)
        print("Assistant:", response)

# Example usage:
if __name__ == "__main__":
    config = load_config()  # alternatively, load from environment variables
    llm = get_llm_provider(config)
    conversation_loop(llm)
