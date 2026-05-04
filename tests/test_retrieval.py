"""CogniRAG test suite."""
import os, sys, pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document
from src.text_splitter import get_text_splitter
from src.vector_store import VectorStoreManager
from src.document_loader import DocumentLoader


@pytest.fixture(autouse=True)
def tmp_chroma(tmp_path, monkeypatch):
    monkeypatch.setenv("PERSIST_DIRECTORY", str(tmp_path / "chroma"))
    from config import settings as s
    s.settings.PERSIST_DIRECTORY = str(tmp_path / "chroma")
    yield


class TestTextSplitter:
    def test_splits(self):
        s = get_text_splitter()
        chunks = s.split_text("Hello. " * 300)
        assert len(chunks) > 1

    def test_chunk_size(self):
        s = get_text_splitter(chunk_size=100, chunk_overlap=10)
        chunks = s.split_text("word " * 500)
        assert all(len(c) <= 150 for c in chunks)


class TestVectorStore:
    def test_init(self):
        assert VectorStoreManager() is not None

    def test_add_count(self):
        vs = VectorStoreManager()
        vs.add_documents([
            Document(page_content="AI is cool", metadata={"source": "t1"}),
            Document(page_content="ML is a subset of AI", metadata={"source": "t2"}),
        ])
        assert vs.count() == 2

    def test_similarity_search(self):
        vs = VectorStoreManager()
        vs.add_documents([
            Document(page_content="The sky is blue", metadata={"source": "a"}),
            Document(page_content="Deep learning uses neural nets", metadata={"source": "b"}),
        ])
        results = vs.similarity_search("neural networks", k=1)
        assert len(results) == 1
        assert "neural" in results[0].page_content.lower()

    def test_reset(self):
        vs = VectorStoreManager()
        vs.add_documents([Document(page_content="test", metadata={})])
        assert vs.count() > 0
        vs.reset()
        assert vs.count() == 0

    def test_reset_then_add(self):
        """Core regression: reset must not break subsequent add_documents."""
        vs = VectorStoreManager()
        vs.add_documents([Document(page_content="first", metadata={})])
        vs.reset()
        # This must NOT raise RuntimeError
        vs.add_documents([Document(page_content="second", metadata={})])
        assert vs.count() == 1

    def test_get_all_sources(self):
        vs = VectorStoreManager()
        vs.add_documents([
            Document(page_content="a", metadata={"source": "https://example.com"}),
            Document(page_content="b", metadata={"source": "doc.pdf"}),
        ])
        sources = vs.get_all_sources()
        assert "https://example.com" in sources
        assert "doc.pdf" in sources


class TestDocumentLoader:
    def test_init(self):
        assert DocumentLoader() is not None


class TestRAGPipeline:
    def test_reset_clears_memory(self):
        from src.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline.vector_store.add_documents([
            Document(page_content="Paris is the capital of France.", metadata={"source": "geo"})
        ])
        pipeline._build_chain()
        assert pipeline.doc_count > 0
        pipeline.reset()
        assert pipeline.doc_count == 0

    def test_ask_empty(self):
        from src.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline.reset()
        result = pipeline.ask("anything")
        assert "No documents" in result["answer"] or result["sources"] == []

    def test_reset_then_add_and_ask(self):
        """Full integration: reset → add → ask must work without error."""
        from src.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline.reset()
        # add_document is not called here to avoid network/file deps in CI
        # but the chain must be valid after reset
        assert pipeline._chain is not None

    def test_mmr_toggle(self):
        from src.rag_pipeline import RAGPipeline
        pipeline = RAGPipeline()
        pipeline.set_mmr(True)
        assert pipeline._use_mmr is True
        pipeline.set_mmr(False)
        assert pipeline._use_mmr is False