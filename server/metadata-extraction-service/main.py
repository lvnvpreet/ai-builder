# server/metadata-extraction-service/main.py
import os
import sys
import spacy
from fastapi import FastAPI, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add path to import custom modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from custom_ner.ner_trainer import CustomNERTrainer, EntityPatternMatcher
from topic_modeling import TopicModeler
from structure_extraction import DocumentStructureExtractor

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Metadata Extraction Service",
    description="Extracts entities, keywords, topics, and document structure from text.",
    version="2.0.0"
)

# Global variables
nlp = None
custom_ner_model = None
pattern_matcher = None
structure_extractor = None
thread_pool = ThreadPoolExecutor(max_workers=4)

# Load models on startup
@app.on_event("startup")
async def load_models():
    global nlp, custom_ner_model, pattern_matcher, structure_extractor
    
    # Load base spaCy model
    try:
        nlp = spacy.load("en_core_web_sm")
        print("SpaCy model 'en_core_web_sm' loaded successfully.")
    except OSError:
        print("Could not find spaCy model 'en_core_web_sm'.")
        print("Download it by running: python -m spacy download en_core_web_sm")
        nlp = None
    
    # Load custom NER model if available
    custom_model_path = os.getenv("CUSTOM_NER_MODEL_PATH", "models/custom_ner")
    if os.path.exists(custom_model_path):
        try:
            custom_ner_model = spacy.load(custom_model_path)
            print(f"Custom NER model loaded from {custom_model_path}")
        except Exception as e:
            print(f"Error loading custom NER model: {e}")
            custom_ner_model = None
    
    # Initialize pattern matcher
    if nlp:
        pattern_matcher = EntityPatternMatcher(nlp)
        print("Entity pattern matcher initialized")
    
    # Initialize structure extractor
    structure_extractor = DocumentStructureExtractor(nlp)
    print("Document structure extractor initialized")

# Data Models
class ExtractionInput(BaseModel):
    text: str
    extract_entities: bool = True
    extract_keywords: bool = True
    extract_topics: bool = True
    extract_structure: bool = True
    topic_modeling_method: str = Field(default="lda", description="Method for topic modeling: lda, nmf, or gensim")
    num_topics: int = Field(default=5, ge=2, le=20)
    document_format: str = Field(default="text", description="Format of the document: text, html, or markdown")
    use_custom_ner: bool = True
    sessionId: Optional[str] = None

class EntityOutput(BaseModel):
    text: str
    label: str
    start_char: int
    end_char: int
    confidence: Optional[float] = None

class TopicOutput(BaseModel):
    topic_id: int
    words: List[str]
    weights: List[float]
    coherence_score: Optional[float] = None

class DocumentTopicOutput(BaseModel):
    topic_id: int
    probability: float
    top_words: List[str]

class StructureOutput(BaseModel):
    headings: List[Dict[str, Any]] = []
    sections: List[Dict[str, Any]] = []
    lists: List[Dict[str, Any]] = []
    hierarchy: Dict[str, Any] = {}
    complexity_metrics: Dict[str, Any] = {}

class ExtractionOutput(BaseModel):
    entities: List[EntityOutput] = []
    keywords: List[str] = []
    topics: List[TopicOutput] = []
    document_topics: List[DocumentTopicOutput] = []
    structure: Optional[StructureOutput] = None
    custom_entities: List[EntityOutput] = []
    pattern_matches: List[EntityOutput] = []

# Helper functions
async def extract_entities_async(text: str, use_custom: bool = True) -> tuple:
    """Extract entities using both standard and custom NER models."""
    loop = asyncio.get_event_loop()
    
    async def _extract_standard():
        if nlp is None:
            return []
        
        doc = await loop.run_in_executor(thread_pool, nlp, text)
        return [
            EntityOutput(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char
            ) for ent in doc.ents
        ]
    
    async def _extract_custom():
        if not use_custom or custom_ner_model is None:
            return []
        
        doc = await loop.run_in_executor(thread_pool, custom_ner_model, text)
        return [
            EntityOutput(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char,
                confidence=getattr(ent, 'confidence', None)
            ) for ent in doc.ents
        ]
    
    async def _extract_patterns():
        if pattern_matcher is None:
            return []
        
        matches = await loop.run_in_executor(thread_pool, pattern_matcher.find_matches, text)
        return [
            EntityOutput(
                text=match["text"],
                label=match["label"],
                start_char=match["start"],
                end_char=match["end"]
            ) for match in matches
        ]
    
    # Run all extractions concurrently
    standard_entities, custom_entities, pattern_matches = await asyncio.gather(
        _extract_standard(),
        _extract_custom(),
        _extract_patterns()
    )
    
    return standard_entities, custom_entities, pattern_matches

async def extract_keywords_async(text: str) -> List[str]:
    """Extract keywords from text."""
    if nlp is None:
        return []
    
    loop = asyncio.get_event_loop()
    doc = await loop.run_in_executor(thread_pool, nlp, text)
    
    # Extract keywords (non-stopword nouns/proper nouns)
    keywords = list(set(
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.pos_ in ["NOUN", "PROPN"]
    ))
    
    return keywords

async def extract_topics_async(text: str, method: str, num_topics: int) -> tuple:
    """Extract topics using topic modeling."""
    loop = asyncio.get_event_loop()
    
    # Initialize topic modeler
    topic_modeler = TopicModeler(n_topics=num_topics, method=method)
    
    # Fit and transform (using the text as a single document for now)
    _, _ = await loop.run_in_executor(thread_pool, topic_modeler.fit_transform, [text])
    
    # Get topics
    topics = await loop.run_in_executor(thread_pool, topic_modeler.get_topics)
    
    # Get document topics
    doc_topics = await loop.run_in_executor(thread_pool, topic_modeler.get_document_topics, text)
    
    # Convert to output format
    topic_outputs = [
        TopicOutput(
            topic_id=topic["id"],
            words=topic["words"],
            weights=topic["weights"]
        ) for topic in topics
    ]
    
    doc_topic_outputs = [
        DocumentTopicOutput(
            topic_id=dt["topic_id"],
            probability=dt["probability"],
            top_words=dt["top_words"]
        ) for dt in doc_topics
    ]
    
    return topic_outputs, doc_topic_outputs

async def extract_structure_async(text: str, format: str) -> StructureOutput:
    """Extract document structure."""
    if structure_extractor is None:
        return StructureOutput()
    
    loop = asyncio.get_event_loop()
    
    # Extract structure
    structure = await loop.run_in_executor(
        thread_pool,
        structure_extractor.extract_structure,
        text,
        format
    )
    
    # Analyze complexity
    complexity = await loop.run_in_executor(
        thread_pool,
        structure_extractor.analyze_document_complexity,
        structure
    )
    
    return StructureOutput(
        headings=structure.get("headings", []),
        sections=structure.get("sections", []),
        lists=structure.get("lists", []),
        hierarchy=structure.get("hierarchy", {}),
        complexity_metrics=complexity
    )

# API Endpoints
@app.get("/")
async def read_root():
    """Basic health check endpoint."""
    return {
        "message": "Metadata Extraction Service v2.0 is running!",
        "features": {
            "standard_ner": nlp is not None,
            "custom_ner": custom_ner_model is not None,
            "pattern_matching": pattern_matcher is not None,
            "topic_modeling": True,
            "structure_extraction": structure_extractor is not None
        }
    }

@app.post("/extract", response_model=ExtractionOutput)
async def extract_metadata(data: ExtractionInput):
    """
    Extract comprehensive metadata from text including entities, keywords, topics, and structure.
    """
    results = ExtractionOutput()
    
    try:
        # Run extractions concurrently
        tasks = []
        
        if data.extract_entities:
            tasks.append(extract_entities_async(data.text, data.use_custom_ner))
        
        if data.extract_keywords:
            tasks.append(extract_keywords_async(data.text))
        
        if data.extract_topics:
            tasks.append(extract_topics_async(data.text, data.topic_modeling_method, data.num_topics))
        
        if data.extract_structure:
            tasks.append(extract_structure_async(data.text, data.document_format))
        
        # Wait for all tasks to complete
        task_results = await asyncio.gather(*tasks)
        
        # Process results
        result_index = 0
        
        if data.extract_entities:
            entities, custom_entities, pattern_matches = task_results[result_index]
            results.entities = entities
            results.custom_entities = custom_entities
            results.pattern_matches = pattern_matches
            result_index += 1
        
        if data.extract_keywords:
            results.keywords = task_results[result_index]
            result_index += 1
        
        if data.extract_topics:
            topics, doc_topics = task_results[result_index]
            results.topics = topics
            results.document_topics = doc_topics
            result_index += 1
        
        if data.extract_structure:
            results.structure = task_results[result_index]
        
        return results
    
    except Exception as e:
        print(f"Error during metadata extraction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train-custom-ner")
async def train_custom_ner(
    background_tasks: BackgroundTasks,
    training_data_path: str = "data/ner_training_data.json",
    output_dir: str = "models/custom_ner"
):
    """
    Train a custom NER model in the background.
    """
    def train_model():
        try:
            trainer = CustomNERTrainer()
            training_data = trainer.prepare_training_data(training_data_path)
            trainer.train(training_data, output_dir)
            
            # Reload the custom model
            global custom_ner_model
            custom_ner_model = spacy.load(output_dir)
            print(f"Custom NER model trained and loaded from {output_dir}")
        except Exception as e:
            print(f"Error training custom NER model: {e}")
    
    background_tasks.add_task(train_model)
    return {"message": "Custom NER training started in background"}

@app.get("/entity-types")
async def get_entity_types():
    """Get available entity types from both standard and custom NER models."""
    entity_types = {
        "standard": [],
        "custom": [],
        "patterns": []
    }
    
    if nlp:
        entity_types["standard"] = list(nlp.get_pipe("ner").labels)
    
    if custom_ner_model:
        entity_types["custom"] = list(custom_ner_model.get_pipe("ner").labels)
    
    if pattern_matcher:
        entity_types["patterns"] = list(pattern_matcher.matcher.vocab.strings)
    
    return entity_types

# Run the server
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3004"))
    print(f"Starting Metadata Extraction Service v2.0 on http://localhost:{port}")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)