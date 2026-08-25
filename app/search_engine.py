"""
Semantic search engine, ported from the notebook:
  - build combined text column
  - preprocess it
  - train a Word2Vec model on the corpus
  - average word vectors into a document embedding
  - rank documents by cosine similarity to the query embedding

Trained artifacts are cached to disk so the API doesn't retrain on every
restart. Call SemanticSearchEngine.load_or_train(force_retrain=True) (or hit
POST /api/retrain) after replacing data/knowledge_base.csv with your real
dataset.
"""
import os
from typing import List, Optional

import numpy as np
import pandas as pd
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity

from app.preprocess import preprocess_text

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "word2vec.model")
EMBEDDINGS_PATH = os.path.join(MODEL_DIR, "document_embeddings.npy")
PROCESSED_DATA_PATH = os.path.join(MODEL_DIR, "processed_data.pkl")

REQUIRED_COLUMNS = {"document_id", "category", "title", "content", "keywords"}

os.makedirs(MODEL_DIR, exist_ok=True)


class SemanticSearchEngine:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.model: Optional[Word2Vec] = None
        self.document_embeddings: Optional[np.ndarray] = None

    def load_or_train(self, force_retrain: bool = False) -> None:
        cached = (
            os.path.exists(MODEL_PATH)
            and os.path.exists(EMBEDDINGS_PATH)
            and os.path.exists(PROCESSED_DATA_PATH)
        )
        if cached and not force_retrain:
            self.df = pd.read_pickle(PROCESSED_DATA_PATH)
            self.model = Word2Vec.load(MODEL_PATH)
            self.document_embeddings = np.load(EMBEDDINGS_PATH)
            return
        self._train_from_scratch()

    def _train_from_scratch(self) -> None:
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(
                f"No dataset found at {DATA_PATH}. Add your CSV there "
                f"(or run data/generate_data.py for a sample dataset) first."
            )

        df = pd.read_csv(DATA_PATH, encoding="latin1")
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        df["text"] = (
            df["title"].astype(str) + " " +
            df["keywords"].astype(str) + " " +
            df["content"].astype(str)
        )
        df["clean_text"] = df["text"].apply(preprocess_text)

        corpus = df["clean_text"].apply(lambda x: x.split()).tolist()

        model = Word2Vec(
            sentences=corpus,
            vector_size=100,
            window=5,
            min_count=2,
            workers=4,
            sg=1,       # skip-gram
            epochs=20,
            seed=42,
        )

        embeddings = np.array(
            [self._document_vector(t, model) for t in df["clean_text"]]
        )

        df.to_pickle(PROCESSED_DATA_PATH)
        model.save(MODEL_PATH)
        np.save(EMBEDDINGS_PATH, embeddings)

        self.df = df
        self.model = model
        self.document_embeddings = embeddings

    @staticmethod
    def _document_vector(text: str, model: Word2Vec) -> np.ndarray:
        words = text.split()
        vectors = [model.wv[w] for w in words if w in model.wv]
        if not vectors:
            return np.zeros(model.vector_size)
        return np.mean(vectors, axis=0)

    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> List[dict]:
        if self.model is None or self.df is None or self.document_embeddings is None:
            raise RuntimeError("Model not loaded. Call load_or_train() first.")

        cleaned_query = preprocess_text(query)
        query_embedding = self._document_vector(cleaned_query, self.model)

        df = self.df
        embeddings = self.document_embeddings
        if category:
            mask = (df["category"] == category).values
            df = df[mask]
            embeddings = embeddings[mask]
            if len(df) == 0:
                return []

        scores = cosine_similarity([query_embedding], embeddings)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            row = df.iloc[idx]
            results.append({
                "document_id": str(row["document_id"]),
                "title": str(row["title"]),
                "category": str(row["category"]),
                "content": str(row["content"]),
                "score": round(float(scores[idx]), 4),
            })
        return results

    def categories(self) -> List[str]:
        if self.df is None:
            return []
        return sorted(self.df["category"].unique().tolist())


# Single shared instance used by the FastAPI app.
engine = SemanticSearchEngine()
