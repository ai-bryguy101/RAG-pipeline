from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from .config import RagConfig
from .loader import load_documents
from .retriever import RetrievalIndex, build_index, retrieve
from .types import Chunk, Document, RetrievalResult


class RagPipeline:
    def __init__(self, config: RagConfig | None = None):
        self.config = config or RagConfig()

    def ingest(self, path: str | Path) -> list[Document]:
        return load_documents(path)

    def chunk_documents(self, documents: list[Document]) -> list[Chunk]:
        chunked: list[Chunk] = []
        step = self.config.chunk_size_words - self.config.chunk_overlap_words

        for doc in documents:
            words = doc.text.split()
            if not words:
                continue

            if len(words) <= self.config.chunk_size_words:
                chunked.append(
                    Chunk(
                        id=doc.id,
                        title=doc.title,
                        source=doc.source,
                        chunk_index=0,
                        text=" ".join(words),
                    )
                )
                continue

            chunk_index = 0
            for start in range(0, len(words), step):
                window = words[start : start + self.config.chunk_size_words]
                if len(window) < self.config.min_chunk_words:
                    break
                chunked.append(
                    Chunk(
                        id=doc.id,
                        title=doc.title,
                        source=doc.source,
                        chunk_index=chunk_index,
                        text=" ".join(window),
                    )
                )
                chunk_index += 1

        return chunked

    def build_retrieval_index(self, input_path: str | Path) -> RetrievalIndex:
        docs = self.ingest(input_path)
        chunks = self.chunk_documents(docs)
        if not chunks:
            raise ValueError("No chunks available after ingestion and chunking")
        return build_index(chunks)

    def ask(
        self,
        index: RetrievalIndex,
        question: str,
        top_k: int | None = None,
    ) -> tuple[str, list[RetrievalResult]]:
        k = top_k or self.config.default_top_k
        hits = retrieve(index=index, question=question, top_k=k)
        answer = self._synthesize_answer(question=question, hits=hits)
        return answer, hits

    def _synthesize_answer(self, question: str, hits: list[RetrievalResult]) -> str:
        if not hits:
            return (
                "I could not find relevant troubleshooting context in the current index. "
                "Try rephrasing the question or indexing additional documentation."
            )

        lines = ["Troubleshooting guidance based on retrieved runbooks:"]
        for i, hit in enumerate(hits, start=1):
            title = hit.chunk.title or hit.chunk.id
            source = hit.chunk.source or "unknown-source"
            evidence = hit.chunk.text.strip()
            lines.append(
                f"{i}. [{title}] (source: {source}, score: {hit.score:.3f}) {evidence}"
            )

        lines.append(
            f"\nQuestion addressed: {question}\n"
            "Use the steps above in order, validate after each step, and escalate if the symptom persists."
        )
        return "\n".join(lines)

    @staticmethod
    def retrieval_results_to_dict(results: list[RetrievalResult]) -> list[dict]:
        output: list[dict] = []
        for item in results:
            row = asdict(item.chunk)
            row["score"] = item.score
            output.append(row)
        return output
