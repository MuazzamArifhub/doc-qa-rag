"""Ask a question from the terminal.

    uv run python ask.py "What does IndexError mean?"
    uv run python ask.py "How do I stop an infinite loop?" --k 3

Prints the answer, the mode (llm / retrieval_only / not_found) and the retrieved
chunks with their distances, so you can see what the system based its answer on.
"""

from __future__ import annotations

import argparse
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)  # langchain-community sunset notice

from rag.qa import QASystem  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the course notes a question.")
    parser.add_argument("question")
    parser.add_argument("--k", type=int, default=4, help="How many chunks to retrieve")
    args = parser.parse_args()

    result = QASystem(k=args.k).ask(args.question)
    print(f"\nQ: {result.question}\n")
    print(f"A ({result.mode}):\n{result.answer}\n")
    print("Retrieved chunks (lower distance = closer match):")
    for i, s in enumerate(result.sources, 1):
        preview = " ".join(s.text.split())[:90]
        print(f"  {i}. {s.source:<28} distance {s.distance:.3f}  {preview}...")


if __name__ == "__main__":
    main()
