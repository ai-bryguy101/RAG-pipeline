"""
store.py — Vector Store (ChromaDB)
Handles storing embeddings and querying for similar chunks.

ChromaDB runs as a Python library — no server process, no Docker.
Data persists to disk in the chroma_db/ folder.
"""

import logging
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

_client_cache = {}


def get_client(persist_dir: str = "./chroma_db") -> chromadb.ClientAPI:
    """Get or create a persistent ChromaDB client."""
    if persist_dir not in _client_cache:
        logger.info(f"Initializing ChromaDB at: {persist_dir}")
        _client_cache[persist_dir] = chromadb.PersistentClient(path=persist_dir)
    return _client_cache[persist_dir]


def get_collection(
    collection_name: str = "rag_docs",
    persist_dir: str = "./chroma_db",
) -> chromadb.Collection:
    """Get or create a named collection in ChromaDB."""
    client = get_client(persist_dir)
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # use cosine similarity
    )
    return collection


def store_chunks(chunks: list, embeddings: list, config: dict) -> int:
    """
    Store chunks and their embeddings in ChromaDB.
    
    Args:
        chunks: List of Chunk objects
        embeddings: List of embedding vectors (parallel to chunks)
        config: Parsed config.yaml
    
    Returns:
        Number of chunks stored
    """
    vs_cfg = config["vector_store"]
    collection = get_collection(vs_cfg["collection_name"], vs_cfg["persist_dir"])

    # Prepare data for ChromaDB
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        # Create a unique ID from source + chunk index
        source = chunk.metadata.get("source", "unknown")
        chunk_idx = chunk.metadata.get("chunk_index", i)
        chunk_id = f"{source}::chunk_{chunk_idx}"

        ids.append(chunk_id)
        documents.append(chunk.content)
        metadatas.append(chunk.metadata)

    # Upsert in batches (ChromaDB has a batch size limit)
    batch_size = 500
    total_stored = 0

    for start in range(0, len(ids), batch_size):
        end = min(start + batch_size, len(ids))
        collection.upsert(
            ids=ids[start:end],
            documents=documents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )
        total_stored += end - start
        logger.debug(f"Stored batch {start}-{end}")

    logger.info(f"Stored {total_stored} chunks in collection '{vs_cfg['collection_name']}'")
    return total_stored


def query_store(
    query_embedding: list,
    config: dict,
    top_k: int | None = None,
    where_filter: dict | None = None,
) -> dict:
    """
    Query ChromaDB for the most similar chunks.
    
    Args:
        query_embedding: Vector for the query
        config: Parsed config.yaml
        top_k: Override number of results (defaults to config value)
        where_filter: Optional metadata filter (e.g., {"domain": "networking"})
    
    Returns:
        ChromaDB query result dict with 'documents', 'metadatas', 'distances'
    """
    vs_cfg = config["vector_store"]
    ret_cfg = config["retrieval"]
    
    k = top_k or ret_cfg["top_k"]
    collection = get_collection(vs_cfg["collection_name"], vs_cfg["persist_dir"])

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": k,
        "include": ["documents", "metadatas", "distances"],
    }

    if where_filter:
        query_params["where"] = where_filter

    results = collection.query(**query_params)

    n_found = len(results["documents"][0]) if results["documents"] else 0
    logger.info(f"Retrieved {n_found} chunks (requested {k})")

    return results


def get_collection_stats(config: dict) -> dict:
    """Get stats about what's stored in the vector DB."""
    vs_cfg = config["vector_store"]
    collection = get_collection(vs_cfg["collection_name"], vs_cfg["persist_dir"])
    count = collection.count()
    return {
        "collection": vs_cfg["collection_name"],
        "total_chunks": count,
        "persist_dir": vs_cfg["persist_dir"],
    }


def reset_collection(config: dict) -> None:
    """Delete all data in the collection. Use when re-ingesting from scratch."""
    vs_cfg = config["vector_store"]
    client = get_client(vs_cfg["persist_dir"])
    try:
        client.delete_collection(vs_cfg["collection_name"])
        logger.info(f"Deleted collection '{vs_cfg['collection_name']}'")
    except ValueError:
        logger.info("Collection didn't exist, nothing to delete")
