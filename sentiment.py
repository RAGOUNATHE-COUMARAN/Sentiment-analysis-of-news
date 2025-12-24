import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer
import string

# -------------------- Downloads (runs once) --------------------
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)
nltk.download("vader_lexicon", quiet=True)

# -------------------- Initialize --------------------
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()
sia = SentimentIntensityAnalyzer()

# -------------------- Safe Lemmatizer --------------------
def safe_lemmatize(word: str) -> str:
    """Safely lemmatize, fallback to original word if error."""
    try:
        return lemmatizer.lemmatize(word)
    except Exception:
        return word

# -------------------- Preprocessing --------------------
def preprocess_text(text: str) -> str:
    """Clean, tokenize, remove stopwords, and lemmatize text."""
    # Lowercase + remove punctuation
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    
    # Tokenize
    tokens = nltk.word_tokenize(text)

    # Remove stopwords + lemmatize
    cleaned_tokens = [safe_lemmatize(word) for word in tokens if word not in stop_words]

    return " ".join(cleaned_tokens)

# -------------------- Sentiment Function --------------------
def get_sentiment(text: str):
    """
    Returns (compound_score, sentiment_label)
    Compound score ranges [-1, 1]:
        - Positive: >= 0.05
        - Negative: <= -0.05
        - Neutral: otherwise
    """
    processed = preprocess_text(text)
    scores = sia.polarity_scores(processed)
    compound = scores["compound"]

    if compound >= 0.05:
        sentiment = "Positive"
    elif compound <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return compound, sentiment

# -------------------- Testing --------------------
if __name__ == "__main__":
    sample_texts = [
        "The economy is doing well, stocks are rising!",
        "I'm very sad about the current situation.",
        "The news today was just okay, nothing special.",
        "Terrible policies ruined the market.",
        "Absolutely fantastic progress has been made!"
    ]

    for t in sample_texts:
        score, label = get_sentiment(t)
        print(f"{t}\n  → Score: {score:.2f}, Sentiment: {label}\n")
