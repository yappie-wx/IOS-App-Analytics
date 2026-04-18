import pickle
import re
import streamlit as st

# ── Load models ────────────────────────────────────────────────────────────────
@st.cache_resource()
def load_classifier_models():
    with open("utils/models/sentiment_classifier.pkl", "rb") as f:
        sentiment_model = pickle.load(f)

    with open("utils/models/intent_classifier.pkl", "rb") as f:
        intent_model = pickle.load(f)

    return sentiment_model, intent_model

# ── Same text cleaner used during training ─────────────────────────────────────
def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

# ── Predict a single review ────────────────────────────────────────────────────
def predict(review: str, sentiment_model, intent_model) -> dict:
    cleaned = clean_text(review)
    return {
        "sentiment": sentiment_model.predict([cleaned])[0],
        "intent":    intent_model.predict([cleaned])[0],
    }

# ── Predict a batch (list or DataFrame column) ─────────────────────────────────
def predict_batch(reviews: list, sentiment_model, intent_model) -> list:
    cleaned = [clean_text(r) for r in reviews]
    sentiments = sentiment_model.predict(cleaned)
    intents    = intent_model.predict(cleaned)
    return [{"sentiment": s, "intent": i} for s, i in zip(sentiments, intents)]