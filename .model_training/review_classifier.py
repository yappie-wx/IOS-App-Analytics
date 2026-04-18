import pandas as pd
import re
import sys
import warnings
import pickle
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, f1_score, balanced_accuracy_score
from sklearn.utils import resample


# ── Text cleaning ──────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


# ── Oversampling ───────────────────────────────────────────────────────────────
def oversample_minority(df: pd.DataFrame, label_col: str,
                        target_ratio: float = 0.5) -> pd.DataFrame:
    """
    Upsample minority classes so each has at least
    target_ratio * majority_count samples.
    """
    counts = df[label_col].value_counts()
    majority_n = counts.iloc[0]
    target_n   = max(int(majority_n * target_ratio), counts.iloc[-1] * 2)

    parts = []
    for cls, cnt in counts.items():
        subset = df[df[label_col] == cls]
        if cnt < target_n:
            parts.append(resample(subset, replace=True,
                                  n_samples=target_n, random_state=42))
        else:
            parts.append(subset)
    return (pd.concat(parts)
              .sample(frac=1, random_state=42)
              .reset_index(drop=True))


# ── Pipeline factory ───────────────────────────────────────────────────────────
def make_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=40_000,
            sublinear_tf=True,
            min_df=2,
            strip_accents="unicode",
        )),
        ("clf", LogisticRegression(
            C=5,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )),
    ])


# ── Train & evaluate ───────────────────────────────────────────────────────────
def train(csv_path: str = "Labelled.csv"):
    df = pd.read_csv(csv_path)[["review", "sentiment", "intent"]].dropna()
    df["review"] = df["review"].astype(str).str.strip()
    df = df[df["review"].str.len() > 2].reset_index(drop=True)
    df["clean"] = df["review"].apply(clean_text)

    print(f"Dataset: {len(df):,} rows")
    print("\nSentiment distribution:")
    print(df["sentiment"].value_counts().to_string())
    print("\nIntent distribution:")
    print(df["intent"].value_counts().to_string())

    models = {}
    for target in ["sentiment", "intent"]:
        print(f"\n{'='*60}")
        print(f"TARGET: {target.upper()}")
        print(f"{'='*60}")

        X_raw, y_raw = df["clean"].values, df[target].values

        # Stratified split — test preserves real class distribution
        X_tr_raw, X_te, y_tr_raw, y_te = train_test_split(
            X_raw, y_raw, test_size=0.2, stratify=y_raw, random_state=42
        )

        # Oversample ONLY training data
        tr_df = pd.DataFrame({"text": X_tr_raw, "label": y_tr_raw})
        tr_os = oversample_minority(tr_df, "label", target_ratio=0.5)
        X_tr, y_tr = tr_os["text"].values, tr_os["label"].values

        print(f"Train (after oversampling): {len(X_tr):,}")
        print(f"Test  (original dist.)    : {len(X_te):,}")

        pipe = make_pipeline()
        pipe.fit(X_tr, y_tr)
        y_pred = pipe.predict(X_te)

        f1  = f1_score(y_te, y_pred, average="macro")
        bal = balanced_accuracy_score(y_te, y_pred)
        print(f"\nMacro F1   : {f1:.4f}")
        print(f"Balanced Acc: {bal:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_te, y_pred, digits=3))

        model_path = f"{target}_classifier.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(pipe, f)
        print(f"Model saved → {model_path}")
        models[target] = pipe

    return models


# ── Inference helper ───────────────────────────────────────────────────────────
def load_models():
    models = {}
    for target in ["sentiment", "intent"]:
        with open(f"{target}_classifier.pkl", "rb") as f:
            models[target] = pickle.load(f)
    return models


def predict(text: str, models: dict) -> dict:
    cleaned = clean_text(text)
    return {
        "sentiment": models["sentiment"].predict([cleaned])[0],
        "intent":    models["intent"].predict([cleaned])[0],
    }


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "predict":
        models = load_models()
        print("Review Classifier — type a review, or 'quit' to exit")
        while True:
            txt = input("\nReview: ").strip()
            if txt.lower() in ("quit", "exit", "q"):
                break
            if txt:
                r = predict(txt, models)
                print(f"  Sentiment : {r['sentiment']}")
                print(f"  Intent    : {r['intent']}")
    else:
        train("/mnt/user-data/uploads/Labelled.csv")
