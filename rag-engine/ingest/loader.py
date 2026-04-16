"""
loader.py — Document Loader
Reads files from the domain docs folder and normalizes them into
a common format for the chunker.

Supports: .md, .txt, .html, .pdf, .rst
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """A loaded document with its content and metadata."""
    content: str
    metadata: dict = field(default_factory=dict)

    def __repr__(self):
        src = self.metadata.get("source", "unknown")
        return f"Document(source='{src}', chars={len(self.content)})"


def load_markdown(filepath: str) -> str:
    """Load a markdown or plain text file."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def load_html(filepath: str) -> str:
    """Load an HTML file, strip tags, return text."""
    from bs4 import BeautifulSoup
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def load_pdf(filepath: str) -> str:
    """Load a PDF file and extract text."""
    import fitz  # pymupdf
    text_parts = []
    with fitz.open(filepath) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n\n".join(text_parts)


# Map file extensions to their loader functions
LOADERS = {
    ".md": load_markdown,
    ".txt": load_markdown,      # same logic works
    ".rst": load_markdown,      # good enough for plain text extraction
    ".html": load_html,
    ".htm": load_html,
    ".pdf": load_pdf,
}


def load_documents(docs_path: str, file_types: list[str]) -> list[Document]:
    """
    Recursively load all supported files from a directory.
    
    Args:
        docs_path: Path to the domain docs folder
        file_types: List of extensions to include (e.g., [".md", ".pdf"])
    
    Returns:
        List of Document objects with content and metadata
    """
    documents = []
    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        logger.error(f"Docs path does not exist: {docs_path}")
        return documents

    # Walk through all files recursively
    for filepath in sorted(docs_dir.rglob("*")):
        if not filepath.is_file():
            continue

        ext = filepath.suffix.lower()
        if ext not in file_types:
            continue

        loader = LOADERS.get(ext)
        if not loader:
            logger.warning(f"No loader for {ext}, skipping: {filepath}")
            continue

        try:
            content = loader(str(filepath))

            # Skip empty or near-empty files
            if len(content.strip()) < 50:
                logger.debug(f"Skipping near-empty file: {filepath}")
                continue

            # Build metadata
            relative_path = filepath.relative_to(docs_dir)
            metadata = {
                "source": str(relative_path),
                "filename": filepath.name,
                "extension": ext,
                "domain": docs_dir.name,
                "subdirectory": str(relative_path.parent) if str(relative_path.parent) != "." else "",
                "char_count": len(content),
            }

            documents.append(Document(content=content, metadata=metadata))
            logger.info(f"Loaded: {relative_path} ({len(content)} chars)")

        except Exception as e:
            logger.error(f"Failed to load {filepath}: {e}")

    logger.info(f"Loaded {len(documents)} documents from {docs_path}")
    return documents
