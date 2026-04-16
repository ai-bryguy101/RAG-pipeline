"""
embedder.py — Embedding Model Wrapper
Wraps sentence-transformers to convert text into vectors.

First run downloads the model (~80MB). After that it loads from cache.
"""

import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_model_cache = {}


def get_model(model_name: str = "all-MiniLM-L6-v2", device: str = "cpu") -> SentenceTransformer:
    """
    Load the embedding model (cached after first call).
    
    Args:
        model_name: HuggingFace model identifier
        device: "cpu" or "cuda"
    
    Returns:
        Loaded SentenceTransformer model
    """
    if model_name not in _model_cache:
        logger.info(f"Loading embedding model: {model_name} (device={device})")
        logger.info("First run will download the model — ~80MB, one time only.")
        _model_cache[model_name] = SentenceTransformer(model_name, device=device)
        logger.info(f"Model loaded. Vector dimensions: {_model_cache[model_name].get_sentence_embedding_dimension()}")

    return _model_cache[model_name]


def embed_texts(texts: list[str], model_name: str = "all-MiniLM-L6-v2", device: str = "cpu") -> list:
    """
    Embed a list of text strings into vectors.
    
    Args:
        texts: List of strings to embed
        model_name: Model to use
        device: "cpu" or "cuda"
    
    Returns:
        List of numpy arrays (vectors)
    """
    model = get_model(model_name, device)
    logger.info(f"Embedding {len(texts)} texts...")
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)
    logger.info(f"Embedded {len(texts)} texts into {embeddings.shape[1]}-dim vectors")
    return embeddings.tolist()


def embed_query(query: str, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu") -> list:
    """
    Embed a single query string. Used at retrieval time.
    
    Args:
        query: The question/search string
    
    Returns:
        Single vector as a list of floats
    """
    model = get_model(model_name, device)
    embedding = model.encode([query])
    return embedding[0].tolist()
