"""Measure how well RETRIEVAL works, using questions with known answers.

Why this matters
----------------
If retrieval doesn't find the right chunk, the answer will be wrong no matter how
good the LLM is. So we test retrieval on its own first. It's free and needs no API key.

What it measures
----------------
For each test question we know which file(s) contain the answer. Then:

    hit@1      was the TOP result from a correct file?
    recall@k   was ANY of the top k results from a correct file?
    MRR        mean reciprocal rank: 1 if the first correct result is ranked 1st,
               0.5 if 2nd, 0.33 if 3rd... averaged over questions. Higher is better.

It also checks that off-topic questions are correctly refused ("not covered").

Run it:
    uv run python evaluate.py

How to explain it in one sentence
---------------------------------
"I built a small test set of questions with known source documents and measured
retrieval separately: hit@1, recall@k and MRR, plus whether off-topic questions
are correctly refused."
"""

from __future__ import annotations

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from rag.qa import MAX_DISTANCE, QASystem  # noqa: E402

# (question, files that contain the answer). Written to be phrased differently from
# the notes, so the test checks matching by meaning, not just copied words.
TEST_SET = [
    ("What does 'list index out of range' mean?", {"04-lists-and-indexing.md"}),
    ("My program never stops repeating. What's going on?", {"03-loops.md"}),
    ("Why can't I do maths with what the user types in?", {"01-variables-and-types.md"}),
    ("What's the difference between return and print?", {"05-functions.md"}),
    ("Python says a variable is not defined. How do I fix it?", {"06-debugging-and-errors.md", "05-functions.md"}),
    ("How many marks do I lose for handing in an assignment late?", {"07-course-policies.md"}),
    ("When should I use == instead of =?", {"02-conditionals.md"}),
    ("Which numbers does range(1, 6) give me?", {"03-loops.md"}),
    ("When can I get help from the instructor?", {"07-course-policies.md"}),
    ("How do I work out the average of some numbers?", {"04-lists-and-indexing.md", "05-functions.md"}),
    ("Why am I getting an error when I add text and a number?", {"06-debugging-and-errors.md", "01-variables-and-types.md"}),
    ("Can I use ChatGPT for my assignments?", {"07-course-policies.md"}),
]

OFF_TOPIC = [
    "What is the capital of France?",
    "How do I bake sourdough bread?",
    "Who won the 2022 World Cup?",
]


def main(k: int = 4) -> None:
    qa = QASystem(k=k, use_llm=False)  # retrieval only: free
    hits1 = hitsk = 0
    rr_total = 0.0

    print(f"{'Question':<62} {'rank':>4}  top result")
    print("-" * 100)
    for question, expected in TEST_SET:
        sources = qa.retrieve(question, k)
        ranks = [i for i, s in enumerate(sources, 1) if s.source in expected]
        first = ranks[0] if ranks else None
        hits1 += first == 1
        hitsk += first is not None
        rr_total += 1 / first if first else 0
        print(f"{question:<62} {first or '-':>4}  {sources[0].source} ({sources[0].distance:.2f})")

    n = len(TEST_SET)
    print("-" * 100)
    print(f"hit@1     {hits1}/{n} ({hits1 / n:.0%})")
    print(f"recall@{k}  {hitsk}/{n} ({hitsk / n:.0%})")
    print(f"MRR       {rr_total / n:.2f}")

    print(f"\nOff-topic questions (should be refused, cutoff distance {MAX_DISTANCE}):")
    refused = 0
    for question in OFF_TOPIC:
        result = qa.ask(question)
        refused += result.mode == "not_found"
        print(f"  {'refused' if result.mode == 'not_found' else 'ANSWERED':<9} {result.sources[0].distance:.2f}  {question}")
    print(f"Correctly refused: {refused}/{len(OFF_TOPIC)}")


if __name__ == "__main__":
    main()
