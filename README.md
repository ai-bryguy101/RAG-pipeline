# Extensible RAG Pipeline for Network/IT Troubleshooting

This repository provides a starter Retrieval-Augmented Generation (RAG) pipeline focused on network and IT troubleshooting.

## What you get

- **Ingestion** from JSONL, CSV, or TXT files
- **Chunking + metadata support** for source attribution
- **Retrieval** using TF-IDF + cosine similarity
- **Answer generation** with a deterministic local synthesizer (no API key required)
- **Pluggable datasets** so you can swap in other domains later
- **Simple CLI** to build an index and ask questions

> The generation step can be swapped for a hosted LLM later while keeping ingestion/retrieval intact.

---

## Project structure

```
.
├── data/
│   └── network_it_troubleshooting.jsonl
├── src/
│   └── rag_pipeline/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── loader.py
│       ├── pipeline.py
│       ├── retriever.py
│       └── types.py
├── tests/
│   └── test_pipeline.py
├── requirements.txt
└── README.md
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Data format

### JSONL (recommended)
Each line should be a JSON object with at least a `text` field:

```json
{"id": "doc-1", "title": "DNS timeout", "text": "Clients cannot resolve internal hostnames...", "source": "runbook/dns.md"}
```

### CSV
- Must include a `text` column.
- Optional: `id`, `title`, `source`.

### TXT
- Whole file becomes one document.

---

## Quickstart

Build an index from the included network/IT dataset:

```bash
PYTHONPATH=src python -m rag_pipeline.cli build-index \
  --input data/network_it_troubleshooting.jsonl \
  --output artifacts/network_index.pkl
```

Ask a question:

```bash
PYTHONPATH=src python -m rag_pipeline.cli ask \
  --index artifacts/network_index.pkl \
  --question "Why are users getting APIPA addresses?"
```

Ask with verbose evidence:

```bash
PYTHONPATH=src python -m rag_pipeline.cli ask \
  --index artifacts/network_index.pkl \
  --question "How do I troubleshoot high packet loss over VPN?" \
  --top-k 4 \
  --show-context
```

---

## Extending to other datasets

1. Add your new dataset in JSONL/CSV/TXT.
2. Rebuild the index with `build-index`.
3. Ask questions against the new index.

No code changes are required unless you want to customize chunking/retrieval/generation behavior.

---

## Future upgrades (drop-in)

- Replace TF-IDF with vector embeddings + vector DB
- Add reranking model
- Add LLM provider for more natural responses
- Add evaluation harness (retrieval precision / answer faithfulness)

