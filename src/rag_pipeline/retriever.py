from __future__ import annotations

import math
import pickle
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from .types import Chunk, RetrievalResult

TOKEN_RE = re.compile(r"[a-zA-Z0-9_\-\.]+")


@dataclass(slots=True)
class RetrievalIndex:
    chunks: list[Chunk]
    chunk_vectors: list[dict[str, float]]
    idf: dict[str, float]

    def save(self, path: str | Path) -> None:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: str | Path) -> "RetrievalIndex":
        with Path(path).open("rb") as f:
            index = pickle.load(f)
        if not isinstance(index, cls):
            raise TypeError("File does not contain a valid RetrievalIndex")
        return index


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_RE.findall(text)]


def _normalize(vector: dict[str, float]) -> dict[str, float]:
    norm = math.sqrt(sum(v * v for v in vector.values()))
    if norm == 0:
        return vector
    return {k: v / norm for k, v in vector.items()}


def _tf(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = sum(counts.values()) or 1
    return {term: count / total for term, count in counts.items()}


def build_index(chunks: list[Chunk]) -> RetrievalIndex:
    tokenized_docs: list[list[str]] = [_tokenize(c.text) for c in chunks]
    num_docs = len(tokenized_docs)

    doc_freq: dict[str, int] = defaultdict(int)
    for tokens in tokenized_docs:
        for term in set(tokens):
            doc_freq[term] += 1

    idf: dict[str, float] = {
        term: math.log((1 + num_docs) / (1 + df)) + 1.0 for term, df in doc_freq.items()
    }

    vectors: list[dict[str, float]] = []
    for tokens in tokenized_docs:
        tf = _tf(tokens)
        vec = {term: tf_val * idf.get(term, 0.0) for term, tf_val in tf.items()}
        vectors.append(_normalize(vec))

    return RetrievalIndex(chunks=chunks, chunk_vectors=vectors, idf=idf)


def _query_vector(question: str, idf: dict[str, float]) -> dict[str, float]:
    tokens = _tokenize(question)
    tf = _tf(tokens)
    weighted = {term: tf_val * idf.get(term, 0.0) for term, tf_val in tf.items()}
    return _normalize(weighted)


def _cosine_sparse(lhs: dict[str, float], rhs: dict[str, float]) -> float:
    if len(lhs) > len(rhs):
        lhs, rhs = rhs, lhs
    return sum(value * rhs.get(key, 0.0) for key, value in lhs.items())


def retrieve(index: RetrievalIndex, question: str, top_k: int) -> list[RetrievalResult]:
    q_vec = _query_vector(question, index.idf)
    if not q_vec:
        return []

    scored: list[tuple[int, float]] = []
    for i, vec in enumerate(index.chunk_vectors):
        score = _cosine_sparse(q_vec, vec)
        if score > 0:
            scored.append((i, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        RetrievalResult(chunk=index.chunks[i], score=score)
        for i, score in scored[:top_k]
    ]
