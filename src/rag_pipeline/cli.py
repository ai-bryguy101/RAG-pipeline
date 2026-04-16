from __future__ import annotations

import argparse
import json

from .pipeline import RagPipeline
from .retriever import RetrievalIndex


def _build_index(args: argparse.Namespace) -> int:
    pipeline = RagPipeline()
    index = pipeline.build_retrieval_index(args.input)
    index.save(args.output)
    print(f"Index written to {args.output} with {len(index.chunks)} chunks")
    return 0


def _ask(args: argparse.Namespace) -> int:
    pipeline = RagPipeline()
    index = RetrievalIndex.load(args.index)
    answer, hits = pipeline.ask(index=index, question=args.question, top_k=args.top_k)

    print(answer)

    if args.show_context:
        print("\nRetrieved context as JSON:")
        print(json.dumps(pipeline.retrieval_results_to_dict(hits), indent=2))
    return 0


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG pipeline CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_index_parser = subparsers.add_parser("build-index", help="Build retrieval index")
    build_index_parser.add_argument("--input", required=True, help="Path to dataset file")
    build_index_parser.add_argument("--output", required=True, help="Path to output index (.pkl)")
    build_index_parser.set_defaults(func=_build_index)

    ask_parser = subparsers.add_parser("ask", help="Query an existing index")
    ask_parser.add_argument("--index", required=True, help="Path to index file")
    ask_parser.add_argument("--question", required=True, help="Question to answer")
    ask_parser.add_argument("--top-k", type=int, default=3, help="How many chunks to retrieve")
    ask_parser.add_argument(
        "--show-context",
        action="store_true",
        help="Print retrieved chunks as JSON for inspection",
    )
    ask_parser.set_defaults(func=_ask)

    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
