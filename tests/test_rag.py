"""Tests for loading, chunking, retrieval, the not-covered check and the API.

The retrieval and API tests build a real index from data/ into a temporary folder,
so they use the local embedding model (free, no API key).
"""

import warnings

import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi.testclient import TestClient  # noqa: E402

from rag.ingest import CHUNK_SIZE, build_index, load_documents, split_documents  # noqa: E402
from rag.qa import QASystem, build_prompt, build_request  # noqa: E402


@pytest.fixture(scope="module")
def index_dir(tmp_path_factory):
    """Build the index once for all tests in this file."""
    path = tmp_path_factory.mktemp("index")
    build_index(index_dir=path)
    return path


def test_documents_load_with_source_and_title():
    docs = load_documents()
    assert len(docs) == 7
    lists = next(d for d in docs if d.metadata["source"] == "04-lists-and-indexing.md")
    assert lists.metadata["title"] == "Week 4: Lists and indexing"


def test_chunks_are_small_and_keep_their_source():
    """Every chunk fits the size limit (plus the short title prefix) and remembers its file."""
    chunks = split_documents(load_documents())
    assert len(chunks) > 7  # documents were actually split
    for c in chunks:
        assert len(c.page_content) <= CHUNK_SIZE + 60
        assert c.metadata["source"].endswith(".md")


def test_retrieval_finds_the_right_document(index_dir):
    qa = QASystem(index_dir=index_dir, use_llm=False)
    assert qa.retrieve("What does list index out of range mean?")[0].source == "04-lists-and-indexing.md"
    assert qa.retrieve("How much is the late penalty?")[0].source == "07-course-policies.md"


def test_off_topic_question_is_refused(index_dir):
    """The system should say the notes don't cover it, not make something up."""
    result = QASystem(index_dir=index_dir, use_llm=False).ask("What is the capital of France?")
    assert result.mode == "not_found"


def test_retrieval_only_mode_returns_best_passage(index_dir):
    result = QASystem(index_dir=index_dir, use_llm=False).ask("How do I stop an infinite loop?")
    assert result.mode == "retrieval_only"
    assert "03-loops.md" in result.answer


def test_prompt_labels_each_note_with_its_source(index_dir):
    sources = QASystem(index_dir=index_dir, use_llm=False).retrieve("What is an IndexError?", k=2)
    prompt = build_prompt("What is an IndexError?", sources)
    assert f'<note source="{sources[0].source}">' in prompt
    assert prompt.endswith("Question: What is an IndexError?")


def test_llm_request_shape_without_calling_the_api(index_dir):
    sources = QASystem(index_dir=index_dir, use_llm=False).retrieve("What is an IndexError?", k=2)
    request = build_request("claude-opus-5-5", "What is an IndexError?", sources)
    assert request["output_config"]["effort"] == "low"
    assert request["fallbacks"] == "default"
    assert "only the course notes" in request["system"]


def test_api_answers_and_validates_input(index_dir, monkeypatch):
    monkeypatch.setenv("RAG_INDEX_DIR", str(index_dir))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from app import app

    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"

        response = client.post("/ask", json={"question": "What does IndexError mean?", "k": 3})
        assert response.status_code == 200
        body = response.json()
        assert body["mode"] == "retrieval_only"
        assert len(body["sources"]) == 3
        assert body["sources"][0]["source"] == "04-lists-and-indexing.md"

        # Pydantic rejects a too-short question with a 422 validation error.
        assert client.post("/ask", json={"question": "a"}).status_code == 422
