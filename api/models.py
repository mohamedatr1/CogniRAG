from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class DocumentSource(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float = 1.0


class AskResponse(BaseModel):
    answer: str
    sources: List[DocumentSource]
    elapsed: Optional[float] = None


class UploadResponse(BaseModel):
    document_id: str
    status: str
    chunks: Optional[int] = None