import pandas as pd
from pydantic import BaseModel
from typing import Literal
from ollama import AsyncClient
import asyncio
import pandas as pd
from tqdm.asyncio import tqdm_asyncio

MODEL = "qwen2.5:7b"
CONCURRENCY = 20

LABELLING_PROMPT = """
You are building a training dataset for a machine learning model that classifies app store reviews.
Your labels must be consistent, accurate, and justifiable.

Rules:
- Base sentiment on the TONE of the review text, not just the star rating
- A 5-star review can still be negative if the text is sarcastic or complaining  
- A 1-star review can be neutral if it is purely factual with no emotion
- Mark confidence as "low" if the review is ambiguous, sarcastic, very short, or in broken English
- Trolls are reviews that are spam, gibberish, completely off-topic, or clearly fake
- Write the reason in one short sentence explaining your label choice

Sentiment options:  positive | negative | neutral 
Intent options:     bug_report | feature_request | complaint | praise | question | troll

Return ONLY a valid JSON object. No explanation outside the JSON.
""".strip()

class ReviewLabel(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    intent: Literal["bug_report", "feature_request", "complaint", "praise", "question", "troll"]
    confidence: Literal["high", "low"]
    reason: str

def _build_labelling_prompt(row: dict) -> str:
    return (
        f"Star rating: {row['rating']}/5\n"
        f"Title: {row['title']}\n"
        f"Review: {row['review']}"
    )

async def _label_single(client: AsyncClient, sem: asyncio.Semaphore, row: dict) -> dict:
    async with sem:
        try:
            response = await client.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": LABELLING_PROMPT},
                    {"role": "user",   "content": _build_labelling_prompt(row)},
                ],
                format=ReviewLabel.model_json_schema(),
                options={"temperature": 0},
            )
            result = ReviewLabel.model_validate_json(response.message.content)
            return {
                "sentiment":  result.sentiment,
                "intent":     result.intent,
                "confidence": result.confidence,
                "reason":     result.reason,
            }
        except Exception as e:
            return {
                "sentiment":  "neutral",
                "intent":     "troll",
                "confidence": "low",
                "reason":     f"labelling failed: {e}",
            }

async def _label_all(records: list[dict]) -> list[dict]:
    sem = asyncio.Semaphore(CONCURRENCY)
    client = AsyncClient()
    tasks = [_label_single(client, sem, row) for row in records]
    return await tqdm_asyncio.gather(*tasks, desc="Labelling reviews")

def label_reviews(df: pd.DataFrame) -> pd.DataFrame:
    records = df[["title", "rating", "review"]].to_dict(orient="records")
    results = asyncio.run(_label_all(records))

    df = df.copy()
    df["sentiment"]  = [r["sentiment"]  for r in results]
    df["intent"]     = [r["intent"]     for r in results]
    df["confidence"] = [r["confidence"] for r in results]
    df["reason"]     = [r["reason"]     for r in results]
    return df

df = pd.read_csv('reviews.csv')

(label_reviews(df)).to_csv("Labelled.csv")