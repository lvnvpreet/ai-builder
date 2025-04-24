import os
import subprocess
import sys

def setup_spacy_model():
    """Download the spaCy English model."""
    try:
        import spacy
        spacy.load("en_core_web_sm")
        print("spaCy model already installed")
    except OSError:
        print("Downloading spaCy model...")
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("spaCy model downloaded successfully")

def create_directories():
    """Create necessary directories."""
    directories = [
        "analyzers",
        "logs",
        "data",
        "tests"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create __init__.py for Python packages
        if directory != "logs" and directory != "data":
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    pass
    
    print("Directories created successfully")

if __name__ == "__main__":
    print("Setting up SEO Analyzer Service...")
    setup_spacy_model()
    create_directories()
    print("Setup completed successfully!")