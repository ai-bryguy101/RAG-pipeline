from __future__ import annotations

import csv
import json
from pathlib import Path

from .types import Document


def load_documents(path: str | Path) -> list[Document]:
    input_path = Path(path)
    suffix = input_path.suffix.lower()

    if suffix == ".jsonl":
        return _load_jsonl(input_path)
    if suffix == ".csv":
        return _load_csv(input_path)
    if suffix == ".txt":
        return _load_txt(input_path)

    raise ValueError(f"Unsupported file extension: {input_path.suffix}")


def _load_jsonl(path: Path) -> list[Document]:
    docs: list[Document] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            text = payload.get("text", "").strip()
            if not text:
                continue
            docs.append(
                Document(
                    id=str(payload.get("id", f"jsonl-{i}")),
                    title=payload.get("title"),
                    source=payload.get("source", str(path)),
                    text=text,
                )
            )
    return docs


def _load_csv(path: Path) -> list[Document]:
    docs: list[Document] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            text = (row.get("text") or "").strip()
            if not text:
                continue
            docs.append(
                Document(
                    id=str(row.get("id") or f"csv-{i}"),
                    title=(row.get("title") or None),
                    source=(row.get("source") or str(path)),
                    text=text,
                )
            )
    return docs


def _load_txt(path: Path) -> list[Document]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [Document(id=path.stem, title=path.stem, source=str(path), text=text)]
