from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import tempfile, os

from src.rag_pipeline import RAGPipeline
from api.models import AskResponse, UploadResponse

app = FastAPI(title="CogniRAG API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

pipeline = RAGPipeline()


@app.post("/upload", response_model=UploadResponse)
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(None), url: str = None):
    if not file and not url:
        raise HTTPException(400, "Provide file or url")
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            path = tmp.name
        background_tasks.add_task(pipeline.add_document, path, "pdf")
        return UploadResponse(document_id=file.filename, status="processing")
    background_tasks.add_task(pipeline.add_document, url, "url")
    return UploadResponse(document_id=url, status="processing")


@app.post("/ask", response_model=AskResponse)
async def ask(question: str, top_k: int = Query(None)):
    if not question.strip():
        raise HTTPException(400, "Empty question")
    result = pipeline.ask(question, top_k=top_k)
    return AskResponse(**result)


@app.get("/ask/stream")
async def ask_stream(question: str, top_k: int = Query(None)):
    return StreamingResponse(
        pipeline.stream_ask(question, top_k=top_k),
        media_type="text/plain",
    )


@app.delete("/reset")
async def reset():
    pipeline.reset()
    return {"status": "ok"}


@app.get("/status")
async def status():
    return {
        "chunks": pipeline.doc_count,
        "sources": pipeline.all_sources,
        "history": pipeline.source_history,
    }