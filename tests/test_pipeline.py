from pathlib import Path

from rag_pipeline.pipeline import RagPipeline


def test_index_and_query_round_trip(tmp_path: Path) -> None:
    pipeline = RagPipeline()
    index = pipeline.build_retrieval_index("data/network_it_troubleshooting.jsonl")

    output_index = tmp_path / "index.pkl"
    index.save(output_index)

    loaded = type(index).load(output_index)
    answer, hits = pipeline.ask(
        index=loaded,
        question="How should I troubleshoot APIPA 169.254 addresses?",
        top_k=2,
    )

    assert "Troubleshooting guidance" in answer
    assert hits
    assert any("169.254" in h.chunk.text for h in hits)


def test_chunking_handles_small_document() -> None:
    pipeline = RagPipeline()
    docs = pipeline.ingest("data/network_it_troubleshooting.jsonl")[:1]
    chunks = pipeline.chunk_documents(docs)

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
