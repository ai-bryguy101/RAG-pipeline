from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RagConfig:
    """Configuration for ingestion, retrieval, and generation."""

    chunk_size_words: int = 120
    chunk_overlap_words: int = 30
    min_chunk_words: int = 25
    default_top_k: int = 3
