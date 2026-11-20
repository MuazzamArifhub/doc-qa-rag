# Course Notes Q&A (RAG)

Ask questions about CS1 course notes and get answers grounded in the notes, with sources. Built with **LangChain**, **FAISS** and **FastAPI**, using retrieval-augmented generation (RAG).

```
INDEXING (once)                                   ANSWERING (every question)
data/*.md ─► chunk ─► embed ─► FAISS index        question ─► embed ─► FAISS: 4 closest chunks
            (500 chars,  (384-number                                    │
             80 overlap)  vectors)                too far away? ─► "the notes don't cover that"
                                                                        │
                                                  Claude answers ONLY from those chunks, with citations
                                                  (no API key: returns the best passage instead)
```

The sample documents in `data/` are short, fictional CS1 notes: variables, conditionals, loops, lists, functions, debugging and course policies.

## Run it

Requires [uv](https://docs.astral.sh/uv/). Everything below is free. The embedding model runs locally (downloaded once, about 70 MB).

```powershell
uv sync                                                  # install
uv run python -m rag.ingest                              # build the index
uv run python ask.py "What does IndexError mean?"        # ask from the terminal
uv run python evaluate.py                                # measure retrieval quality
uv run python -m pytest -q                               # run the tests
uv run python -m uvicorn app:app --reload                # start the API
```

With the API running, open **http://127.0.0.1:8000/docs** to try `/ask` in the browser.

To have Claude write the answers (costs a fraction of a cent per question), set `ANTHROPIC_API_KEY` and install the extra:

```powershell
uv sync --extra llm
uv run --extra llm python ask.py "What does IndexError mean?"
```

## Files

| File | What it does |
|---|---|
| `rag/ingest.py` | **Indexing.** Load documents, split into overlapping chunks, embed, save to FAISS. |
| `rag/qa.py` | **Answering.** Embed the question, retrieve the closest chunks, refuse if nothing is close enough, then generate a cited answer with Claude (or return the best passage). |
| `app.py` | **FastAPI** web API: `GET /health`, `POST /ask`, with interactive docs at `/docs`. |
| `ask.py` | Terminal interface. Shows the answer and the retrieved chunks with distances. |
| `evaluate.py` | Retrieval evaluation on 12 questions with known sources, plus 3 off-topic questions. |
| `tests/test_rag.py` | 8 tests: loading, chunking, retrieval, refusal, prompt, request shape, API. |

## Results

`evaluate.py` on the sample notes (k = 4):

| Metric | Result |
|---|---|
| hit@1 (correct document ranked first) | 12/12 |
| recall@4 (correct document in the top 4) | 12/12 |
| MRR (mean reciprocal rank) | 1.00 |
| Off-topic questions correctly refused | 3/3 |

**How to read this:** the test set is small and the notes are short and clearly separated by topic, so perfect scores are expected here. A real evaluation needs more documents, more questions (ideally written by students) and harder cases, such as questions whose answer spans two documents.

## Design decisions

- **Local embeddings (FastEmbed, bge-small).** Free, private and no API key needed, so indexing and retrieval work offline.
- **Chunk size 500, overlap 80, split on headings first.** The notes are short and organised by section, so chunks follow the sections. Each chunk is prefixed with its document title so a chunk like "use range(1, 11)" still matches loop questions.
- **A "not covered" check.** If the closest chunk's distance is above 0.85, the system says the notes don't cover the question instead of guessing. The cutoff was calibrated on this data: on-topic questions scored 0.23 to 0.64, off-topic ones 0.98 to 1.16.
- **Grounded prompt.** Claude is told to answer only from the notes, to cite them, and to say so when the notes don't contain the answer. The notes are marked as reference material, not instructions.
- **Retrieval is evaluated separately.** If the right chunk isn't retrieved, no LLM can fix the answer.

## Limitations and next steps

- Tiny, synthetic document set. Real course material would test chunking much harder (code blocks, tables, PDFs).
- Pure vector search can miss exact keywords. **Hybrid search** (BM25 keywords plus vectors) and a **reranker** would help on a larger corpus.
- The distance cutoff must be recalibrated whenever the documents or embedding model change.
- Answer quality (correctness, faithfulness to the notes) isn't measured yet, only retrieval.
- `langchain-community` is being phased out in favour of standalone integration packages. A longer-lived version would migrate.

## Possible connection to adaptive learning

The same retrieval step could ground automated feedback in course material: a student who keeps hitting `IndexError` gets a tip that links to the exact section of the notes, not generic advice.
