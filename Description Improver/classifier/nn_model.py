import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

class CompanyDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.tokenizer = tokenizer
        self.texts = texts
        self.labels = labels
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        encoding = self.tokenizer(self.texts[idx],
                                  truncation=True,
                                  padding='max_length',
                                  max_length=self.max_length,
                                  return_tensors='pt')
        encoding = {key: val.squeeze() for key, val in encoding.items()}
        encoding['labels'] = torch.tensor(self.labels[idx], dtype=torch.long)
        return encoding

def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    f1 = f1_score(p.label_ids, preds, average='weighted')
    return {"weighted_f1": f1}

def main():
    # Load the data
    print("Loading data...")
    df = pd.read_pickle("../companies_meta_updated.pkl")
    texts = df['description'].tolist()
    labels = df['cluster'].tolist()  # assumed integer labels
    
    # Split data into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
    
    # Initialize tokenizer and model
    model_name = "distilbert-base-uncased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    num_labels = len(set(labels))
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    
    # Create training and evaluation datasets
    train_dataset = CompanyDataset(X_train, y_train, tokenizer)
    test_dataset = CompanyDataset(X_test, y_test, tokenizer)
    
    # Set up training arguments to leverage GPU and fp16 precision
    training_args = TrainingArguments(
        output_dir="./nn_model",
        evaluation_strategy="epoch",
        save_strategy="epoch",  # updated to match eval strategy
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        learning_rate=3e-5,           # increased learning rate
        warmup_ratio=0.05,            # reduced warmup period
        gradient_accumulation_steps=1,  # reduced accumulation to update parameters more frequently
        weight_decay=0.01,
        fp16=True,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="weighted_f1",
        logging_steps=50,
        logging_dir='./logs',
    )
    
    # Optionally, add an early stopping callback:
    # from transformers import EarlyStoppingCallback
    # trainer = Trainer(
    #     ...,
    #     callbacks=[EarlyStoppingCallback(early_stopping_patience=2)]
    # )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )
    
    # Train the model
    trainer.train()
    
    # Evaluate the model
    eval_results = trainer.evaluate()
    print("Evaluation results:", eval_results)
    
    # Save the model and tokenizer
    model.save_pretrained("./nn_model2")
    tokenizer.save_pretrained("./nn_model2")

if __name__ == "__main__":
    main()
