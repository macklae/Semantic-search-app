# Semantic Knowledge Base Search

FastAPI backend + a single static HTML/JS frontend, wrapping the Word2Vec
semantic search pipeline from `Semantic_Similarity_Search_System.ipynb`.

```
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
├── models/                 trained model + embeddings cache (generated)
├── requirements.txt
├── Dockerfile
└── README.md
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
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```
Put this behind nginx / a reverse proxy with TLS for production use.

## 5. Notes / things to know before going further

- The model retrains from scratch on first boot if `models/` is empty
  (a few minutes for a large CSV). Cached artifacts are reused after that.
- `min_count=2` in `Word2Vec` means very rare words are dropped from the
  vocabulary — this mirrors the notebook's original training config.
- Words never seen during training return a zero vector at query time
  (same limitation flagged in the notebook re: FastText for unseen words).
  Swap `Word2Vec` for `FastText` in `search_engine.py` if you want subword
  handling for typos/rare terms.
