"""
RAG Pipeline — load → chunk → embed → store → retrieve → generate.

Features:
  - Session isolation: chain always rebuilt after add / reset
  - MMR retrieval option for diverse results
  - Streaming support
  - Document history tracking
  - Relevance scoring
"""
import logging
import time
from typing import Any, Dict, Generator, List, Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from config.settings import settings
from src.document_loader import DocumentLoader
from src.llm import get_llm
from src.text_splitter import get_text_splitter
from src.vector_store import VectorStoreManager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are CogniRAG, a precise and helpful research assistant.
Answer the user's question using ONLY the context provided below.
- If the context lacks enough information, say so honestly.
- Be concise, structured, and accurate.
- When citing, reference the source naturally.
- Use markdown formatting for clarity (bullets, bold, etc.) when appropriate.

Context:
{context}"""


class RAGPipeline:
    """Full RAG pipeline with correct session isolation and advanced retrieval."""

    def __init__(self):
        self.loader = DocumentLoader()
        self.splitter = get_text_splitter()
        self.vector_store = VectorStoreManager()
        self.llm = get_llm()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
        ])
        self._use_mmr = False
        self._chain = None
        self._ingested_sources: List[Dict] = []  # history of ingested docs
        self._build_chain()

    # ── Chain ────────────────────────────────────────────────────────────────

    def _build_chain(self) -> None:
        """Rebuild LCEL chain with a fresh retriever."""
        if self._use_mmr:
            retriever = self.vector_store.get_mmr_retriever(k=settings.TOP_K)
        else:
            retriever = self.vector_store.get_retriever(k=settings.TOP_K)

        self._chain = (
            {"context": retriever | self._format_docs, "input": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        logger.debug("QA chain rebuilt (mmr=%s)", self._use_mmr)

    @staticmethod
    def _format_docs(docs: List[Document]) -> str:
        parts = []
        for i, d in enumerate(docs, 1):
            source = d.metadata.get("source", "unknown")
            page = d.metadata.get("page", "")
            ref = f"[{i}] ({source}" + (f", p.{page}" if page != "" else "") + ")"
            parts.append(f"{ref}\n{d.page_content}")
        return "\n\n---\n\n".join(parts)

    # ── Retrieval mode ────────────────────────────────────────────────────────

    def set_mmr(self, enabled: bool) -> None:
        """Toggle Maximal Marginal Relevance retrieval."""
        if self._use_mmr != enabled:
            self._use_mmr = enabled
            self._build_chain()

    # ── Ingestion ─────────────────────────────────────────────────────────────

    def add_document(self, source: str, source_type: str = "pdf") -> int:
        """Ingest PDF or URL. Returns chunk count."""
        t0 = time.time()
        if source_type == "pdf":
            docs = self.loader.load_pdf(source)
        elif source_type == "url":
            docs = self.loader.load_url(source)
        else:
            raise ValueError(f"Unknown source_type: {source_type!r}")

        if not docs:
            logger.warning("No content extracted from %s", source)
            return 0

        chunks = self.splitter.split_documents(docs)
        self.vector_store.add_documents(chunks)
        self._build_chain()  # CRITICAL: fresh retriever sees new data

        elapsed = time.time() - t0
        self._ingested_sources.append({
            "source": source,
            "type": source_type,
            "chunks": len(chunks),
            "elapsed": round(elapsed, 2),
        })
        logger.info("Ingested %d chunks from %s in %.1fs", len(chunks), source, elapsed)
        return len(chunks)

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Wipe vector store and history. Chain rebuilt over empty store."""
        self.vector_store.reset()
        self._ingested_sources.clear()
        self._build_chain()  # CRITICAL: retriever over empty store
        logger.info("Pipeline reset — all documents cleared")

    # ── Q&A ──────────────────────────────────────────────────────────────────

    def ask(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """Ask a question; return answer + scored sources."""
        if not question.strip():
            return {"answer": "Please enter a question.", "sources": [], "elapsed": 0}

        if self.vector_store.count() == 0:
            return {
                "answer": (
                    "📭 No documents in the knowledge base yet.\n\n"
                    "Add a URL or PDF from the sidebar to get started."
                ),
                "sources": [],
                "elapsed": 0,
            }

        effective_k = top_k or settings.TOP_K
        if effective_k != settings.TOP_K:
            if self._use_mmr:
                retriever = self.vector_store.get_mmr_retriever(k=effective_k)
            else:
                retriever = self.vector_store.get_retriever(k=effective_k)
            chain = (
                {"context": retriever | self._format_docs, "input": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
        else:
            retriever = (
                self.vector_store.get_mmr_retriever(k=effective_k)
                if self._use_mmr
                else self.vector_store.get_retriever(k=effective_k)
            )
            chain = self._chain

        t0 = time.time()
        try:
            answer = chain.invoke(question)
            # Scored sources for UI display
            scored = self.vector_store.similarity_search_with_score(question, k=effective_k)
            sources = [
                {
                    "text": doc.page_content[:600] + ("…" if len(doc.page_content) > 600 else ""),
                    "metadata": doc.metadata,
                    "score": round(float(score), 3),
                }
                for doc, score in scored
            ]
            return {"answer": answer, "sources": sources, "elapsed": round(time.time() - t0, 2)}
        except Exception as e:
            logger.exception("Error during QA")
            return {"answer": f"⚠️ Error: {e}", "sources": [], "elapsed": 0}

    def stream_ask(self, question: str, top_k: int = None) -> Generator[str, None, None]:
        """Streaming version of ask — yields answer tokens."""
        if self.vector_store.count() == 0:
            yield "📭 No documents indexed yet."
            return

        effective_k = top_k or settings.TOP_K
        retriever = (
            self.vector_store.get_mmr_retriever(k=effective_k)
            if self._use_mmr
            else self.vector_store.get_retriever(k=effective_k)
        )
        docs = retriever.invoke(question)
        context = self._format_docs(docs)
        messages = self.prompt.format_messages(context=context, input=question)
        for chunk in self.llm.stream(messages):
            if hasattr(chunk, "content"):
                yield chunk.content
            else:
                yield str(chunk)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def doc_count(self) -> int:
        return self.vector_store.count()

    @property
    def source_history(self) -> List[Dict]:
        return list(self._ingested_sources)

    @property
    def all_sources(self) -> List[str]:
        return self.vector_store.get_all_sources()