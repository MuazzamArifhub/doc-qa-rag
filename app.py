"""PART 3: the web API (FastAPI).

What this file does
-------------------
Wraps the Q&A system in a web API so any app (a website, a chatbot, a gamified
learning platform) can use it over HTTP:

    GET  /health   is the service up, and is the LLM enabled?
    POST /ask      body: {"question": "...", "k": 4}
                   returns the answer, the mode and the sources used

FastAPI validates every request with Pydantic (e.g. an empty question is rejected
with a clear error) and generates interactive documentation automatically at
http://127.0.0.1:8000/docs, where you can try the API in the browser.

Run it:
    uv run python -m uvicorn app:app --reload

How to explain it in one sentence
---------------------------------
"FastAPI exposes the Q&A system as a /ask endpoint with validated input, and it
generates interactive docs so you can try it in the browser."
"""

from __future__ import annotations

import os
import warnings
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

warnings.filterwarnings("ignore", category=DeprecationWarning)  # langchain-community sunset notice

from rag.qa import QASystem  # noqa: E402

# The index is loaded once when the server starts, not on every request (loading is slow).
state: dict[str, QASystem] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    index_dir = Path(os.environ.get("RAG_INDEX_DIR", "index"))
    state["qa"] = QASystem(index_dir=index_dir)
    yield
    state.clear()


app = FastAPI(
    title="Course Notes Q&A",
    description="Ask questions about CS1 course notes. Answers are grounded in retrieved passages (RAG).",
    lifespan=lifespan,
)


# ---- Request and response shapes. Pydantic checks these automatically. ----

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500, examples=["What does IndexError mean?"])
    k: int = Field(default=4, ge=1, le=10, description="How many chunks to retrieve")


class SourceOut(BaseModel):
    source: str
    title: str
    distance: float = Field(description="Lower = closer match")
    text: str


class AskResponse(BaseModel):
    question: str
    answer: str
    mode: str = Field(description="llm, retrieval_only or not_found")
    sources: list[SourceOut]


# ---- Endpoints ----

@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    """Opening the plain address sends you to the interactive docs page."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict:
    """Quick check that the service is running."""
    return {"status": "ok", "llm_enabled": state["qa"].use_llm}


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    """Answer a question from the course notes."""
    result = state["qa"].ask(req.question, k=req.k)
    return AskResponse(
        question=result.question,
        answer=result.answer,
        mode=result.mode,
        sources=[SourceOut(**vars(s)) for s in result.sources],
    )
