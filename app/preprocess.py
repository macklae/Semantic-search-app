"""
Text preprocessing, ported directly from the notebook's preprocess_text().
"""
import re
import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_REQUIRED_NLTK = {
    "stopwords": "corpora/stopwords",
    "wordnet": "corpora/wordnet",
    "omw-1.4": "corpora/omw-1.4",
    "punkt": "tokenizers/punkt",
    "punkt_tab": "tokenizers/punkt_tab",
}


def ensure_nltk_data() -> None:
    """Download any missing NLTK corpora needed for preprocessing."""
    for package, lookup_path in _REQUIRED_NLTK.items():
        try:
            nltk.data.find(lookup_path)
        except LookupError:
            nltk.download(package, quiet=True)


ensure_nltk_data()

_stop_words = set(stopwords.words("english"))
_lemmatizer = WordNetLemmatizer()


def preprocess_text(text: str) -> str:
    """Lowercase, strip noise, tokenize, remove stopwords, and lemmatize."""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"\d+", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()

    tokens = word_tokenize(text)
    tokens = [w for w in tokens if w not in _stop_words]
    tokens = [_lemmatizer.lemmatize(w) for w in tokens]

    return " ".join(tokens)
