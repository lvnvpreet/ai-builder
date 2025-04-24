# Template Embeddings Cache

This directory stores cached embeddings for templates to avoid recomputing them on every service startup.

## File Structure

- `template_embeddings.pkl`: Pickle file containing a dictionary mapping template IDs to their embedding vectors.

## Generation Process

Embeddings are automatically generated and cached during service initialization. The process works as follows:

1. The service loads template data from `../templates.json`
2. For each template, it creates a rich text representation combining:
   - Template name
   - Template description
   - Industries served
   - Key features
   - Design style
3. This text is passed through a sentence transformer model to generate an embedding vector
4. The embedding is cached in `template_embeddings.pkl` for future use

## Notes

- The directory is created automatically if it doesn't exist
- If `template_embeddings.pkl` exists, it will be loaded on service startup
- When templates are added or modified, their embeddings will be regenerated
- The cache is saved to disk after initializing all templates