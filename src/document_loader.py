"""
Document loader: PDF and web content extraction with multi-strategy fallback.
"""
import logging
import re
from typing import List, Optional
from urllib.parse import urlparse, unquote

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

try:
    from langchain_community.document_loaders import PyPDFLoader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

try:
    from readability import Document as ReadabilityDocument
    READABILITY_AVAILABLE = True
except ImportError:
    READABILITY_AVAILABLE = False

try:
    import wikipedia
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


class DocumentLoader:

    def load_pdf(self, path: str) -> List[Document]:
        if not PDF_AVAILABLE:
            raise ImportError("pip install langchain-community pypdf")
        try:
            docs = PyPDFLoader(path).load()
            logger.info("PDF loaded: %s (%d pages)", path, len(docs))
            return docs
        except Exception as e:
            logger.error("PDF load failed: %s", e)
            raise

    def load_url(self, url: str) -> List[Document]:
        doc = self._try_wikipedia(url)
        if doc:
            return [doc]

        html = self._fetch_html(url)
        if not html:
            return []

        meta = {"source": url, "title": self._page_title(html, url)}
        text = (
            (TRAFILATURA_AVAILABLE and self._try_trafilatura(html, url))
            or (READABILITY_AVAILABLE and self._try_readability(html, url))
            or self._try_bs4(html, url)
        )
        if text:
            logger.info("Extracted %d chars from %s", len(text), url)
            return [Document(page_content=text, metadata=meta)]

        logger.warning("All extraction strategies failed for %s", url)
        return []

    def _try_wikipedia(self, url: str) -> Optional[Document]:
        if not WIKIPEDIA_AVAILABLE or "wikipedia.org" not in url:
            return None
        try:
            path = unquote(urlparse(url).path)
            m = re.search(r"/wiki/(.+?)(?:#|$)", path)
            if not m:
                return None
            title = m.group(1).replace("_", " ")
            page = wikipedia.page(title, auto_suggest=False)
            text = _clean(page.content)
            if len(text) >= 200:
                return Document(
                    page_content=text,
                    metadata={"source": url, "title": page.title, "method": "wikipedia_api"},
                )
        except Exception as e:
            logger.debug("Wikipedia API failed: %s", e)
        return None

    def _try_trafilatura(self, html: str, url: str) -> Optional[str]:
        try:
            text = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=True,
                include_links=False,
                favor_precision=True,
                url=url,
            )
            if text and len(text.strip()) >= 200:
                return _clean(text)
        except Exception as e:
            logger.debug("trafilatura error: %s", e)
        return None

    def _try_readability(self, html: str, url: str) -> Optional[str]:
        try:
            doc = ReadabilityDocument(html)
            soup = BeautifulSoup(doc.summary(), "lxml")
            text = soup.get_text("\n", strip=True)
            if len(text.strip()) >= 200:
                return _clean(text)
        except Exception as e:
            logger.debug("readability error: %s", e)
        return None

    def _try_bs4(self, html: str, url: str) -> Optional[str]:
        try:
            soup = BeautifulSoup(html, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()
            best, best_len = soup.body or soup, 0
            for tag in soup.find_all(["article", "main", "section", "div"]):
                txt = tag.get_text(strip=True)
                if len(txt) > best_len:
                    best_len, best = len(txt), tag
            text = best.get_text("\n", strip=True)
            if len(text.strip()) >= 200:
                return _clean(text)
        except Exception as e:
            logger.debug("bs4 error: %s", e)
        return None

    def _fetch_html(self, url: str) -> Optional[str]:
        try:
            resp = _make_session().get(url, headers=_HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.error("Fetch failed for %s: %s", url, e)
            return None

    def _page_title(self, html: str, url: str) -> str:
        try:
            soup = BeautifulSoup(html, "lxml")
            t = soup.find("title")
            if t and t.text.strip():
                return t.text.strip()
        except Exception:
            pass
        return urlparse(url).netloc