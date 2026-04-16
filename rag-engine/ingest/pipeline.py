"""
pipeline.py — Ingest Pipeline Orchestrator
Ties together: load docs → chunk → embed → store

Run this whenever you add new docs to a domain folder.
"""

import logging
from .loader import load_documents
from .chunker import chunk_documents

logger = logging.getLogger(__name__)


def run_ingest(config: dict) -> list:
    """
    Full ingest pipeline: load → chunk → return chunks ready for embedding.
    
    The embedding + storage step is handled by embed/store.py so we keep
    a clean separation between "document processing" and "vector operations."
    
    Args:
        config: Parsed config.yaml as a dictionary
    
    Returns:
        List of Chunk objects ready to be embedded and stored
    """
    domain_cfg = config["domain"]
    chunk_cfg = config["chunking"]

    logger.info(f"=== Starting ingest for domain: {domain_cfg['name']} ===")
    logger.info(f"Docs path: {domain_cfg['docs_path']}")

    # Step 1: Load documents
    documents = load_documents(
        docs_path=domain_cfg["docs_path"],
        file_types=domain_cfg["file_types"],
    )

    if not documents:
        logger.warning("No documents found! Check your docs_path and file_types in config.yaml")
        return []

    # Step 2: Chunk documents
    chunks = chunk_documents(
        documents=documents,
        chunk_size=chunk_cfg["chunk_size"],
        chunk_overlap=chunk_cfg["chunk_overlap"],
        separators=chunk_cfg.get("separators"),
    )

    logger.info(f"=== Ingest complete: {len(documents)} docs → {len(chunks)} chunks ===")

    return chunks
