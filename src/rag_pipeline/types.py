from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Document:
    """A raw document record before chunking."""

    id: str
    text: str
    title: str | None = None
    source: str | None = None


@dataclass(slots=True)
class Chunk:
    """A chunked document used for retrieval."""

    id: str
    text: str
    title: str | None
    source: str | None
    chunk_index: int


@dataclass(slots=True)
class RetrievalResult:
    """One retrieved chunk with its relevance score."""

    chunk: Chunk
    score: float
