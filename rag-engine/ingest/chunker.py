"""
chunker.py — Document Chunker
Splits documents into overlapping chunks suitable for embedding.

Uses LangChain's RecursiveCharacterTextSplitter which is smart about
splitting on natural boundaries (headers, paragraphs, sentences).
"""

import logging
from dataclasses import dataclass, field
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """A chunk of text ready for embedding."""
    content: str
    metadata: dict = field(default_factory=dict)

    def __repr__(self):
        src = self.metadata.get("source", "unknown")
        idx = self.metadata.get("chunk_index", "?")
        return f"Chunk(source='{src}', idx={idx}, chars={len(self.content)})"


def chunk_documents(
    documents: list,
    chunk_size: int = 768,
    chunk_overlap: int = 150,
    separators: list[str] | None = None,
) -> list[Chunk]:
    """
    Split documents into overlapping chunks.
    
    Args:
        documents: List of Document objects from the loader
        chunk_size: Target size per chunk in characters
        chunk_overlap: Overlap between consecutive chunks
        separators: Priority order for split points
    
    Returns:
        List of Chunk objects with inherited + chunk-specific metadata
    """
    if separators is None:
        separators = ["\n## ", "\n### ", "\n\n", "\n", " "]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks = []

    for doc in documents:
        # Split the document content
        splits = splitter.split_text(doc.content)

        for i, text in enumerate(splits):
            # Inherit document metadata and add chunk-specific info
            chunk_meta = {
                **doc.metadata,
                "chunk_index": i,
                "chunk_total": len(splits),
                "chunk_chars": len(text),
            }

            all_chunks.append(Chunk(content=text, metadata=chunk_meta))

        logger.debug(
            f"  {doc.metadata.get('source', '?')}: "
            f"{len(splits)} chunks from {doc.metadata.get('char_count', '?')} chars"
        )

    logger.info(
        f"Chunked {len(documents)} documents into {len(all_chunks)} chunks "
        f"(avg {sum(len(c.content) for c in all_chunks) // max(len(all_chunks), 1)} chars/chunk)"
    )

    return all_chunks
