# Semantic Knowledge Base Search

FastAPI backend + a single static HTML/JS frontend, wrapping a Word2Vec-based
semantic search pipeline originally developed in
`Semantic_Similarity_Search_System.ipynb`.

## How the semantic search works

The application converts both the knowledge-base documents and the user's
search query into numerical vector representations and compares them using
cosine similarity.

```text
Knowledge Base CSV
       ↓
Text preprocessing
       ↓
Tokenisation / lemmatisation
       ↓
Word2Vec training
       ↓
Word vectors
       ↓
Document embeddings
       ↓
User query
       ↓
Query preprocessing
       ↓
Query embedding
       ↓
Cosine similarity
       ↓
Top-K ranked results
       ↓
FastAPI API
       ↓
HTML/JavaScript frontend

```
## Project structure

semantic-search-app/
├── app/
│   ├── main.py            FastAPI app (API routes + serves static/)
│   ├── search_engine.py   preprocessing → Word2Vec → cosine similarity search
│   └── preprocess.py      text cleaning (ported from the notebook)
├── data/
│   ├── generate_data.py   builds a sample knowledge_base.csv
│   └── knowledge_base.csv sample dataset (replace with your real export)
├── static/
│   └── index.html         frontend (no build step)
├── models/                generated model + embedding cache (not committed)
├── requirements.txt
├── Dockerfile
└── README.md
```


```
## 1. About the dataset

The notebook trained on `knowledge_base_improved 1.csv`, which wasn't
included with it. `data/knowledge_base.csv` here is a **generated sample
dataset** (~320 rows across 8 categories) so the app runs end to end out of
the box.

**To use your real data:** replace `data/knowledge_base.csv` with your CSV
(same columns: `document_id, category, title, content, keywords`), delete
the `models/` folder (or call `POST /api/retrain`), and restart the server.

## 2. Run it locally (VS Code terminal)

```bash
cd semantic-search-app

# create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# (optional) regenerate the sample dataset
python data/generate_data.py

# start the API + frontend (first run also trains the model, ~1-2 min)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000** for the frontend.
API docs (Swagger UI) are auto-generated at **http://localhost:8000/docs**.

## 3. API reference

| Method | Path             | Body                                              | Description                       |
|--------|------------------|----------------------------------------------------|------------------------------------|
| GET    | `/api/health`    | –                                                  | Status + document count           |
| GET    | `/api/categories`| –                                                  | List of categories for the filter |
| POST   | `/api/search`    | `{"query": "...", "top_k": 5, "category": null}`   | Ranked semantic search results    |
| POST   | `/api/retrain`   | –                                                  | Retrain from `data/knowledge_base.csv` |

Quick test:

```bash
curl http://localhost:8000/api/health

curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "my password is not working", "top_k": 5}'
```

## 4. Deploy

### Option A — Docker (any host: a VPS, EC2, Fly.io, etc.)

```bash
docker build -t semantic-search-app .
docker run -p 8000:8000 semantic-search-app
```

Visit `http://<server-ip>:8000`.

### Option B — Render / Railway (free-tier friendly)

1. Push this folder to a GitHub repo.
2. Create a new **Web Service** on Render (or Railway) pointing at that repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Deploy. Render/Railway auto-detect Python and expose a public URL.

### Option C — Any VM with systemd

```bash
# on the server, after cloning the repo and creating the venv as in step 2:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```
Put this behind nginx / a reverse proxy with TLS for production use.

## 5. Notes / things to know before going further

- The model retrains from scratch on first boot if `models/` is empty
  (a few minutes for a large CSV). Cached artifacts are reused after that.
- `min_count=2` in `Word2Vec` means very rare words are dropped from the
  vocabulary — this mirrors the notebook's original training config.
- The current implementation uses Word2Vec. Words that were not observed
  during Word2Vec training are not represented in its vocabulary and therefore
  cannot receive a learned word vector at query time. FastText could be used as
  a future enhancement because it represents words using character subword
  information, making it more robust for rare words, misspellings and unseen
  word forms.
