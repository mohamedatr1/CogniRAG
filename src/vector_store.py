"""
Vector store manager — ChromaDB with Windows-safe reset.

ROOT CAUSE FIX:
  On Windows, ChromaDB holds SQLite file locks via the chromadb client.
  The old code set self._store = None after closing, then raised RuntimeError
  on the very next add_documents call — because the init only ran once.

  Solution: NEVER set _store to None. Instead:
    1. Use chromadb's built-in .delete_collection() to wipe all vectors in-place.
    2. Re-create the collection immediately in the same client instance.
    3. Wrap the Chroma LangChain object around the fresh collection.
  This keeps file handles open and valid throughout — no rename, no rmtree.
"""
import logging
import os
from typing import List

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config.settings import settings
from src.embeddings import get_embeddings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "cognirag"


class VectorStoreManager:
    """ChromaDB vector store with bullet-proof in-process reset (Windows safe)."""

    def __init__(self):
        self.embeddings = get_embeddings()
        self._client: chromadb.ClientAPI = self._make_client()
        self._store: Chroma = self._wrap_store()

    # ── Private helpers ───────────────────────────────────────────────────────

    def _make_client(self) -> chromadb.ClientAPI:
        """Create (or reuse) a persistent ChromaDB client."""
        os.makedirs(settings.PERSIST_DIRECTORY, exist_ok=True)
        return chromadb.PersistentClient(path=settings.PERSIST_DIRECTORY)

    def _wrap_store(self) -> Chroma:
        """Wrap existing (or newly created) collection with LangChain Chroma."""
        return Chroma(
            client=self._client,
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def add_documents(self, docs: List[Document]) -> None:
        if not docs:
            logger.warning("add_documents: empty list, nothing to do")
            return
        self._store.add_documents(docs)
        logger.info(f"Added {len(docs)} chunks to vector store")

    def get_retriever(self, k: int = None):
        return self._store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k or settings.TOP_K},
        )

    def get_mmr_retriever(self, k: int = None, fetch_k: int = None, lambda_mult: float = 0.5):
        """Maximal Marginal Relevance retriever — more diverse results."""
        k = k or settings.TOP_K
        return self._store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": fetch_k or k * 3,
                "lambda_mult": lambda_mult,
            },
        )

    def count(self) -> int:
        try:
            return self._client.get_collection(COLLECTION_NAME).count()
        except Exception:
            return 0

    def reset(self) -> None:
        """
        Wipe ALL vectors without touching file handles.

        Strategy (Windows-safe):
          1. delete_collection()  — removes all data inside ChromaDB's SQLite
          2. create_collection()  — makes a fresh empty collection
          3. Re-wrap with Chroma  — LangChain layer sees the new collection

        No shutil.rmtree, no os.rename, no file locking issues.
        """
        try:
            self._client.delete_collection(COLLECTION_NAME)
            logger.info("Collection deleted")
        except Exception as e:
            logger.warning(f"delete_collection failed (maybe didn't exist): {e}")

        # Re-create immediately
        self._client.get_or_create_collection(COLLECTION_NAME)
        self._store = self._wrap_store()
        logger.info("Vector store reset — fresh and empty")

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Direct similarity search (tests + debug)."""
        return self._store.similarity_search(query, k=k)

    def similarity_search_with_score(self, query: str, k: int = 4):
        """Return (doc, score) pairs for relevance display."""
        return self._store.similarity_search_with_relevance_scores(query, k=k)

    def get_all_sources(self) -> List[str]:
        """Return unique source metadata values stored in the collection."""
        try:
            col = self._client.get_collection(COLLECTION_NAME)
            result = col.get(include=["metadatas"])
            sources = set()
            for meta in result.get("metadatas", []):
                if meta and meta.get("source"):
                    sources.add(meta["source"])
            return sorted(sources)
        except Exception:
            return []