"""
query.py — Query & Retrieval
Embeds your question, searches ChromaDB, optionally re-ranks results.

This is the module where retrieval quality lives or dies.
"""

import logging
from embed.embedder import embed_query
from embed.store import query_store

logger = logging.getLogger(__name__)


def retrieve(question: str, config: dict) -> list[dict]:
    """
    Full retrieval pipeline: embed question → search → optional re-rank.
    
    Args:
        question: The user's question
        config: Parsed config.yaml
    
    Returns:
        List of result dicts with 'content', 'metadata', 'score'
    """
    emb_cfg = config["embedding"]
    ret_cfg = config["retrieval"]

    # Step 1: Embed the question
    logger.info(f"Query: {question[:80]}...")
    query_vec = embed_query(
        question,
        model_name=emb_cfg["model_name"],
        device=emb_cfg["device"],
    )

    # Step 2: Search ChromaDB
    # Fetch more than top_k if we're going to re-rank
    search_k = ret_cfg["top_k"] * 3 if ret_cfg.get("use_reranker") else ret_cfg["top_k"]
    raw_results = query_store(query_vec, config, top_k=search_k)

    if not raw_results["documents"][0]:
        logger.warning("No results found!")
        return []

    # Package results into a cleaner format
    results = []
    for doc, meta, dist in zip(
        raw_results["documents"][0],
        raw_results["metadatas"][0],
        raw_results["distances"][0],
    ):
        results.append({
            "content": doc,
            "metadata": meta,
            "score": 1 - dist,  # convert distance to similarity score
        })

    # Step 3: Optional re-ranking
    if ret_cfg.get("use_reranker") and results:
        results = rerank(question, results, config)

    return results


def rerank(question: str, results: list[dict], config: dict) -> list[dict]:
    """
    Re-rank results using a cross-encoder model.
    Cross-encoders are slower but more accurate than bi-encoders for ranking.
    
    Args:
        question: The original question
        results: Initial retrieval results
        config: Parsed config.yaml
    
    Returns:
        Re-ranked and trimmed results
    """
    from sentence_transformers import CrossEncoder

    ret_cfg = config["retrieval"]
    model_name = ret_cfg.get("reranker_model", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    final_k = ret_cfg.get("reranker_top_k", 3)

    logger.info(f"Re-ranking {len(results)} results with {model_name}")
    model = CrossEncoder(model_name)

    # Score each (question, chunk) pair
    pairs = [(question, r["content"]) for r in results]
    scores = model.predict(pairs)

    # Attach re-rank scores and sort
    for result, score in zip(results, scores):
        result["rerank_score"] = float(score)

    results.sort(key=lambda x: x["rerank_score"], reverse=True)

    logger.info(f"Top re-ranked score: {results[0]['rerank_score']:.4f}")

    return results[:final_k]
