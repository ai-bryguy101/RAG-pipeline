"""
prompt.py — Prompt Template Builder
Constructs the augmented prompt that gets sent to Claude.

This is where you control HOW Claude uses the retrieved context.
The system prompt is critical — it defines Claude's behavior.
"""

import logging

logger = logging.getLogger(__name__)

# ============================================================
# SYSTEM PROMPT — Edit this to change Claude's behavior
# ============================================================
SYSTEM_PROMPT = """You are an expert IT and networking engineer assistant. You answer questions using ONLY the context provided below. You are thorough, precise, and explain your reasoning.

RULES:
1. Answer based on the provided context. If the context doesn't contain enough information, say so clearly — do NOT make things up.
2. When referencing information, cite the source document (shown in [Source: ...] tags).
3. If the question involves troubleshooting, think step-by-step: identify the likely cause, explain why, then provide the fix.
4. Use technical terminology accurately but explain concepts when they might be unfamiliar.
5. If multiple sources provide conflicting information, note the discrepancy.

You are talking to a systems/network engineer who is learning. Be detailed but clear."""


def build_prompt(question: str, results: list[dict]) -> tuple[str, str]:
    """
    Build the system prompt and user message for Claude.
    
    Args:
        question: The user's question
        results: Retrieved chunks from query.py
    
    Returns:
        Tuple of (system_prompt, user_message)
    """
    # Format retrieved chunks as context
    context_parts = []
    for i, result in enumerate(results, 1):
        source = result["metadata"].get("source", "unknown")
        score = result.get("rerank_score", result.get("score", 0))
        context_parts.append(
            f"--- Context Chunk {i} [Source: {source}] [Relevance: {score:.3f}] ---\n"
            f"{result['content']}\n"
        )

    context_block = "\n".join(context_parts)

    user_message = f"""CONTEXT (retrieved from knowledge base):
{context_block}

QUESTION:
{question}

Please provide a thorough answer based on the context above. Cite your sources."""

    logger.debug(f"Built prompt with {len(results)} context chunks, {len(user_message)} chars")

    return SYSTEM_PROMPT, user_message


def build_debug_prompt(question: str, results: list[dict]) -> str:
    """
    Build a formatted string showing what would be sent to Claude.
    Used for debugging retrieval before wiring up the API.
    """
    system, user = build_prompt(question, results)
    return (
        f"{'='*60}\n"
        f"SYSTEM PROMPT:\n{'='*60}\n{system}\n\n"
        f"{'='*60}\n"
        f"USER MESSAGE:\n{'='*60}\n{user}\n"
    )
