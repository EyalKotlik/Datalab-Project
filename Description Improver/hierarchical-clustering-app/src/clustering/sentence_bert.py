class SentenceBERT:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def load_model(self):
        return self.model

    def transform(self, texts):
        embeddings = self.model.encode(texts, convert_to_tensor=True)
        # Convert to CPU, detach, then cast to float32 to reduce memory usage
        embeddings = embeddings.cpu().detach().numpy().astype('float16')
        return embeddings