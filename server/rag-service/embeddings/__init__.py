from .ollama_embedding import OllamaEmbedding
from .openai_embedding import OpenAIEmbedding
from .sentence_transformers import SentenceTransformerEmbedding
from .cohere_embedding import CohereEmbedding


# Registry of available embedding models
_EMBEDDINGS = {
    "sentence-transformers": SentenceTransformerEmbedding,
    "openai": OpenAIEmbedding,
    "cohere": CohereEmbedding,
    "ollama": OllamaEmbedding,
    # Add more embedding models as they are implemented
}