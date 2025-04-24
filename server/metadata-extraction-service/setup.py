# server/metadata-extraction-service/setup.py
import nltk
import spacy
import os

def setup_nltk():
    """Download necessary NLTK data."""
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('averaged_perceptron_tagger')
    print("NLTK data downloaded successfully")

def setup_spacy():
    """Download spaCy models."""
    try:
        spacy.load("en_core_web_sm")
        print("spaCy model already installed")
    except OSError:
        print("Downloading spaCy model...")
        os.system("python -m spacy download en_core_web_sm")
        print("spaCy model downloaded successfully")

def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "models",
        "models/custom_ner",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Directories created successfully")

if __name__ == "__main__":
    print("Setting up Metadata Extraction Service...")
    setup_nltk()
    setup_spacy()
    create_directories()
    print("Setup completed successfully!")