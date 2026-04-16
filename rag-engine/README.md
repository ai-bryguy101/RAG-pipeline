# RAG Engine — Domain-Agnostic Retrieval Pipeline

A local-first RAG (Retrieval Augmented Generation) pipeline that gives Claude
deep knowledge about any domain you feed it. Currently loaded with networking
and IT docs, but swap the `domains/` folder for anything.

## Quick Start

### 1. Setup (one time)

```bash
# Clone or copy this project
cd rag-engine

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (will take a few minutes — downloads PyTorch)
pip install -r requirements.txt
```

### 2. Add Your Docs

Drop markdown, PDF, HTML, or plain text files into the domain folder:

```
domains/networking/
├── rfcs/                  # Drop RFC text files here
├── linux-networking/      # Linux networking guides
├── troubleshooting/       # Runbooks and troubleshooting guides
└── vendor-docs/           # Cisco, Juniper, Arista docs
```

Two sample docs are included so you can test immediately.

### 3. Ingest (Phase 1)

```bash
python cli.py ingest
```

This will: load all docs → split into chunks → embed → store in ChromaDB.
First run downloads the embedding model (~80MB). Takes ~30 seconds after that.

### 4. Test Retrieval (Phase 2)

```bash
# See what chunks come back for a question (no Claude needed)
python cli.py query "Why is my OSPF adjacency stuck in exstart?"
python cli.py query "How do I troubleshoot DNS failures?"
```

This is your debugging step. If the right chunks aren't coming back here,
Claude won't have the right context to answer well. Tune chunking settings
in `config.yaml` if needed.

### 5. Full RAG with Claude (Phase 3)

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Ask a question — retrieves context, sends to Claude, streams answer
python cli.py ask "My DNS resolution is slow and intermittent. What should I check?"
```

### 6. Other Commands

```bash
python cli.py stats    # See what's in the vector store
python cli.py reset    # Wipe the vector store and start fresh
```

## Switching Domains

1. Create a new folder: `domains/your-new-domain/`
2. Add docs (md, pdf, html, txt)
3. Edit `config.yaml`: change `domain.name` and `domain.docs_path`
4. Run `python cli.py reset` then `python cli.py ingest`

The pipeline code never changes — only the docs and config.

## Tuning Retrieval Quality

The most impactful settings in `config.yaml`:

| Setting | Default | What it does |
|---------|---------|-------------|
| `chunking.chunk_size` | 768 | Bigger = more context per chunk, smaller = more precise |
| `chunking.chunk_overlap` | 150 | Prevents cutting concepts in half |
| `retrieval.top_k` | 5 | More chunks = more context but also more noise |
| `retrieval.use_reranker` | false | Enable for better precision (slower) |
| `generation.model` | claude-sonnet | Switch to opus for complex troubleshooting |
| `generation.temperature` | 0.3 | Lower = more factual, higher = more creative |

## Build Phases

- [x] **Phase 1:** Ingest + Embed (load docs, chunk, embed, store)
- [x] **Phase 2:** Retrieve + CLI (query from terminal, see raw chunks)
- [x] **Phase 3:** Claude Integration (full RAG pipeline)
- [ ] **Phase 4:** Tune + Expand (re-ranker, new domains, web UI)

## Project Structure

```
rag-engine/
├── config.yaml          # All settings — edit this, not code
├── cli.py               # Main entry point
├── ingest/
│   ├── loader.py        # File readers (md, pdf, html)
│   ├── chunker.py       # Text splitting logic
│   └── pipeline.py      # Orchestrates load → chunk
├── embed/
│   ├── embedder.py      # Embedding model wrapper
│   └── store.py         # ChromaDB operations
├── retrieve/
│   ├── query.py         # Search + optional re-rank
│   └── prompt.py        # Prompt template builder
├── generate/
│   └── claude_client.py # Claude API integration
└── domains/
    └── networking/      # ← Swap this for any domain
```
