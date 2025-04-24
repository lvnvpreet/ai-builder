import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server configuration
PORT = int(os.getenv("PORT", "3007"))

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
TOP_K_RECOMMENDATIONS = int(os.getenv("TOP_K_RECOMMENDATIONS", "5"))

# Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
TEMPLATES_PATH = os.path.join(DATA_DIR, "templates.json")
INDUSTRY_MAPPINGS_PATH = os.path.join(DATA_DIR, "industry_mappings.json")
EMBEDDINGS_DIR = os.path.join(DATA_DIR, "embeddings")
TEMPLATE_EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, "template_embeddings.pkl")

# Make sure directories exist
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)