"""PART 1 OF RAG: indexing. Run once, ahead of time.

What this file does
-------------------
Turns a folder of documents into a searchable FAISS index:

    1. LOAD   read every .md, .txt and .pdf file in data/
    2. CHUNK  split each document into pieces of about 500 characters, with
              80 characters of overlap so a sentence cut at a boundary still
              appears whole in one of the chunks. Splits prefer section
              headings, then paragraphs, then lines.
    3. EMBED  turn each chunk into a vector of 384 numbers with a small local
              embedding model (BAAI/bge-small-en-v1.5 via FastEmbed). Chunks
              with similar meaning get vectors that are close together.
    4. STORE  put the vectors in a FAISS index and save it to index/.

Run it:
    uv run python -m rag.ingest

How to explain it in one sentence
---------------------------------
"Indexing splits the documents into overlapping chunks, turns each chunk into an
embedding vector, and stores them in FAISS so we can search by meaning later."
"""

from __future__ import annotations

import argparse
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path("data")
INDEX_DIR = Path("index")

# A small, free embedding model that runs on your own computer (no API key, no cost).
# 384 numbers per chunk. Downloaded once (~70 MB) into .fastembed_cache/.
EMBED_MODEL = "BAAI/bge-small-en-v1.5"

# Chunking settings. Smaller chunks = more precise matches but less context;
# larger chunks = more context but more irrelevant text. These suit short notes.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


def get_embeddings() -> FastEmbedEmbeddings:
    """The embedding model. Indexing and searching MUST use the same model,
    otherwise question vectors and chunk vectors aren't comparable."""
    return FastEmbedEmbeddings(model_name=EMBED_MODEL, cache_dir=".fastembed_cache")


def load_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    """Step 1: read every supported file. Each Document remembers which file it came from."""
    docs: list[Document] = []
    for path in sorted(data_dir.iterdir()):
        if path.suffix.lower() in {".md", ".txt"}:
            loaded = TextLoader(str(path), encoding="utf-8").load()
        elif path.suffix.lower() == ".pdf":
            loaded = PyPDFLoader(str(path)).load()  # one Document per page
        else:
            continue
        for doc in loaded:
            # Use the document's first heading as its title, for citations.
            first_line = doc.page_content.strip().splitlines()[0] if doc.page_content.strip() else path.stem
            doc.metadata.update(source=path.name, title=first_line.lstrip("# ").strip())
            docs.append(doc)
    return docs


def split_documents(docs: list[Document], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[Document]:
    """Step 2: cut documents into overlapping chunks.

    The splitter tries each separator in order: section headings first ("## "),
    then blank lines (paragraphs), then single lines, then spaces. So chunks follow
    the document's structure whenever they can.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n## ", "\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        # Prefix each chunk with its document title. A chunk like "Use range(1, 11)"
        # is easier to match to "loops" questions when it says it comes from the loops notes.
        title = chunk.metadata.get("title", "")
        if title and not chunk.page_content.startswith(f"# {title}"):
            chunk.page_content = f"From: {title}\n\n{chunk.page_content}"
    return chunks


def build_index(data_dir: Path = DATA_DIR, index_dir: Path = INDEX_DIR) -> tuple[int, int]:
    """Steps 3 and 4: embed every chunk and save the FAISS index. Returns (documents, chunks)."""
    docs = load_documents(data_dir)
    if not docs:
        raise SystemExit(f"No .md, .txt or .pdf files found in {data_dir}")
    chunks = split_documents(docs)
    store = FAISS.from_documents(chunks, get_embeddings())  # embeds every chunk, builds the index
    store.save_local(str(index_dir))
    return len(docs), len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the FAISS index from a folder of documents.")
    parser.add_argument("--data", type=Path, default=DATA_DIR, help="Folder of .md/.txt/.pdf files")
    parser.add_argument("--index", type=Path, default=INDEX_DIR, help="Where to save the index")
    args = parser.parse_args()
    n_docs, n_chunks = build_index(args.data, args.index)
    print(f"Indexed {n_docs} documents as {n_chunks} chunks into {args.index}/")


if __name__ == "__main__":
    main()
