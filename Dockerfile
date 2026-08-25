FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK data at build time so the container doesn't need
# network access to download it on first request.
RUN python -c "import nltk; [nltk.download(p) for p in ['stopwords','wordnet','omw-1.4','punkt','punkt_tab']]"

COPY app ./app
COPY static ./static
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
