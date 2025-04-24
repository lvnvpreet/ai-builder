# server/metadata-extraction-service/custom_ner/ner_trainer.py
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import json
import os
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomNERTrainer:
    """Train custom NER models for domain-specific entities."""
    
    def __init__(self, base_model: str = "en_core_web_sm"):
        self.base_model = base_model
        self.nlp = spacy.load(base_model)
        
    def prepare_training_data(self, data_path: str) -> List[Tuple[str, Dict]]:
        """
        Load and prepare training data for NER.
        Expected format: [{"text": "...", "entities": [[start, end, label], ...]}]
        """
        with open(data_path, 'r') as f:
            raw_data = json.load(f)
        
        training_data = []
        for item in raw_data:
            text = item["text"]
            entities = {"entities": item["entities"]}
            training_data.append((text, entities))
        
        return training_data
    
    def train(self, training_data: List[Tuple[str, Dict]], 
              output_dir: str, 
              n_iter: int = 30,
              dropout: float = 0.5):
        """Train the NER model."""
        
        # Add custom NER labels to the model
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner", last=True)
        else:
            ner = self.nlp.get_pipe("ner")
        
        # Add custom labels
        custom_labels = set()
        for _, annotations in training_data:
            for ent in annotations.get("entities", []):
                custom_labels.add(ent[2])
        
        for label in custom_labels:
            ner.add_label(label)
        
        # Get the training data examples
        example_data = []
        for text, annotations in training_data:
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            example_data.append(example)
        
        # Disable other pipes during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        
        # Training loop
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.create_optimizer()
            
            for itn in range(n_iter):
                random.shuffle(example_data)
                losses = {}
                
                # Batch the examples
                batches = minibatch(example_data, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    self.nlp.update(batch, drop=dropout, losses=losses, sgd=optimizer)
                
                logger.info(f"Iteration {itn + 1}/{n_iter}, Loss: {losses.get('ner', 0)}")
        
        # Save the trained model
        os.makedirs(output_dir, exist_ok=True)
        self.nlp.to_disk(output_dir)
        logger.info(f"Model saved to {output_dir}")
        
        return self.nlp
    
    def evaluate(self, test_data: List[Tuple[str, Dict]]) -> Dict:
        """Evaluate the model on test data."""
        from spacy.scorer import Scorer
        
        scorer = Scorer()
        examples = []
        
        for text, annotations in test_data:
            doc = self.nlp(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        scores = scorer.score(examples)
        return scores

# Entity pattern matcher for custom entities
class EntityPatternMatcher:
    """Define patterns for custom entities."""
    
    def __init__(self, nlp):
        self.nlp = nlp
        self.matcher = spacy.matcher.Matcher(nlp.vocab)
        self.define_patterns()
    
    def define_patterns(self):
        """Define patterns for custom entities."""
        
        # Business-specific patterns
        patterns = {
            "BUSINESS_MODEL": [
                [{"LOWER": {"IN": ["b2b", "b2c", "saas", "marketplace", "subscription"]}}],
                [{"LOWER": "business"}, {"LOWER": "to"}, {"LOWER": "business"}],
                [{"LOWER": "business"}, {"LOWER": "to"}, {"LOWER": "consumer"}],
            ],
            "TECH_STACK": [
                [{"LOWER": {"IN": ["react", "angular", "vue", "django", "flask", "nodejs"]}}],
                [{"LOWER": {"IN": ["python", "javascript", "typescript", "java", "c#"]}}],
            ],
            "MARKET_SEGMENT": [
                [{"LOWER": {"IN": ["enterprise", "smb", "startup", "corporate", "consumer"]}}],
                [{"LOWER": "small"}, {"LOWER": "business"}],
                [{"LOWER": "medium"}, {"LOWER": "business"}],
            ],
            "PRICING_MODEL": [
                [{"LOWER": {"IN": ["freemium", "subscription", "pay-per-use", "one-time"]}}],
                [{"LOWER": "per"}, {"LOWER": "user"}],
                [{"LOWER": "per"}, {"LOWER": "month"}],
            ]
        }
        
        for label, pattern_list in patterns.items():
            self.matcher.add(label, pattern_list)
    
    def find_matches(self, text: str) -> List[Dict]:
        """Find matches in text."""
        doc = self.nlp(text)
        matches = self.matcher(doc)
        
        results = []
        for match_id, start, end in matches:
            span = doc[start:end]
            label = self.nlp.vocab.strings[match_id]
            results.append({
                "text": span.text,
                "label": label,
                "start": span.start_char,
                "end": span.end_char
            })
        
        return results