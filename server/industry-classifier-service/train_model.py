# server/industry-classifier-service/train_model.py
import os
import json
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndustryDataset(Dataset):
    """Custom dataset for industry classification."""
    
    def __init__(self, texts: List[str], labels: List[str], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Convert labels to numeric IDs
        self.label_encoder = LabelEncoder()
        self.label_ids = self.label_encoder.fit_transform(labels)
        
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label_id = self.label_ids[idx]
        
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label_id, dtype=torch.long)
        }
    
    def get_label_mapping(self) -> Dict[int, str]:
        """Return mapping of label IDs to label names."""
        return dict(enumerate(self.label_encoder.classes_))

class IndustryClassifierTrainer:
    """Train custom industry classification model."""
    
    def __init__(self, base_model_name: str = "distilbert-base-uncased"):
        self.base_model_name = base_model_name
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.model = None
        self.label_mapping = None
        
    def prepare_data(self, data_path: str) -> Tuple[Dataset, Dataset]:
        """Load and prepare training data."""
        # Load data - expecting CSV with 'text' and 'industry' columns
        df = pd.read_csv(data_path)
        
        # Split data
        train_texts, val_texts, train_labels, val_labels = train_test_split(
            df['text'].tolist(),
            df['industry'].tolist(),
            test_size=0.2,
            random_state=42,
            stratify=df['industry']
        )
        
        # Create datasets
        train_dataset = IndustryDataset(train_texts, train_labels, self.tokenizer)
        val_dataset = IndustryDataset(val_texts, val_labels, self.tokenizer)
        
        # Store label mapping
        self.label_mapping = train_dataset.get_label_mapping()
        
        return train_dataset, val_dataset
    
    def train(self, train_dataset: Dataset, val_dataset: Dataset, output_dir: str):
        """Train the model."""
        # Initialize model
        num_labels = len(set(train_dataset.label_ids))
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.base_model_name,
            num_labels=num_labels
        )
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=100,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="accuracy"
        )
        
        # Define metrics
        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            predictions = np.argmax(predictions, axis=1)
            accuracy = (predictions == labels).mean()
            return {"accuracy": accuracy}
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=compute_metrics
        )
        
        # Train
        trainer.train()
        
        # Save model and tokenizer
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save label mapping
        with open(f"{output_dir}/label_mapping.json", 'w') as f:
            json.dump(self.label_mapping, f)
        
        logger.info(f"Model trained and saved to {output_dir}")
        
        return trainer

# Training script
if __name__ == "__main__":
    trainer = IndustryClassifierTrainer()
    train_dataset, val_dataset = trainer.prepare_data("data/industry_training_data.csv")
    trainer.train(train_dataset, val_dataset, "models/custom_industry_classifier")