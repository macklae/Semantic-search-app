"""
FastAPI backend for the semantic similarity search system.

Serves:
  - REST API under /api/*
  - the static frontend (static/index.html) at /

Run locally with:
    uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.search_engine import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Loads the cached model/embeddings, or trains from data/knowledge_base.csv
    # if no cache exists yet.
    engine.load_or_train()
    yield


app = FastAPI(title="Semantic Similarity Search API", version="1.0.0", lifespan=lifespan)

# Wide-open CORS is fine here because the frontend is served from this same
# app. Tighten allow_origins if you split the frontend onto another domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Free-text search query")
    top_k: int = Field(5, ge=1, le=50)
    category: Optional[str] = None


class SearchResult(BaseModel):
    document_id: str
    title: str
    category: str
    content: str
    score: float


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "documents_loaded": int(len(engine.df)) if engine.df is not None else 0,
    }


@app.get("/api/categories")
def categories():
    return {"categories": engine.categories()}


@app.post("/api/search", response_model=List[SearchResult])
def search(payload: SearchRequest):
    try:
        return engine.search(payload.query, top_k=payload.top_k, category=payload.category)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/retrain")
def retrain():
    """Retrain from data/knowledge_base.csv (use after replacing it with real data)."""
    try:
        engine.load_or_train(force_retrain=True)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "retrained", "documents": int(len(engine.df))}


# Serve the frontend last so it doesn't shadow the /api routes above.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
