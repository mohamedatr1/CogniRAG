from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import settings


def get_text_splitter(chunk_size: int = None, chunk_overlap: int = None):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or settings.CHUNK_SIZE,
        chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )