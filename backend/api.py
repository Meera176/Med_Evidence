import os
import shutil
import tempfile
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion.fetcher import fetch_papers
from ingestion.pdf_loader import process_pdf, chunk_text, clean_text
from ingestion.embedder import embed_chunks
from ingestion.vector_store import store_chunks, clear_collection, search
from ingestion.embedder import embed_query
from ingestion.searcher import hybrid_search
from ingestion.retriever import ask

app = FastAPI(title="MedEvidence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    try:
        # auto-fetch papers from PubMed based on the question
        papers = fetch_papers(request.question, max_results=5)

        if papers:
            all_chunks = []
            for paper in papers:
                cleaned = clean_text(paper["text"])
                chunks = chunk_text(cleaned)
                for chunk, _ in chunks:
                    all_chunks.append({"text": chunk, "source": paper["source"], "page": paper["page"]})
            all_chunks = embed_chunks(all_chunks)
            store_chunks(all_chunks)

        # search across everything stored (auto-fetched + any uploaded PDFs)
        top_chunks = hybrid_search(request.question)
        if not top_chunks:
            raise HTTPException(status_code=404, detail="No relevant information found for this question")

        answer = ask(request.question, top_chunks)
        return {
            "answer": answer,
            "citations": [
                {"source": c["source"], "page": c["page"]}
                for c in top_chunks
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get answer: {str(e)}")


@app.post("/ingest/pdf")
def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        chunks = process_pdf(tmp_path)
        if not chunks:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        chunks = embed_chunks(chunks)
        store_chunks(chunks)
        return {"message": f"Ingested {len(chunks)} chunks from {file.filename}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF ingestion failed: {str(e)}")
    finally:
        os.remove(tmp_path)


@app.delete("/clear")
def clear():
    try:
        clear_collection()
        return {"message": "All ingested data cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")
