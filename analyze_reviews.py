import csv
import json
import random
import urllib.request
import urllib.error

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "alibayram/mimo-7b-rl:latest"
INPUT_CSV = "product_reviews_mock_data.csv"
OUTPUT_JSON = "results.json"
OUTPUT_SAMPLE_CSV = "sample_input.csv"
SAMPLE_SIZE = 100

SYSTEM_PROMPT = """You are a product review classifier.
Analyze the review and return ONLY a valid JSON object with these fields:
- sentiment: one of "positive", "negative", or "neutral"
- topic: main topic of the review (1-3 words, e.g. "product quality", "customer service", "value for money")
- confidence: number from 0.0 to 1.0

Return only the JSON object, no explanation."""


def load_sample(filepath, n):
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    random.seed(42)
    return random.sample(rows, min(n, len(rows)))


def call_llm(review_text):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Review: {review_text}"},
        ],
        "stream": False,
        "format": "json",
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    content = body["message"]["content"]
    return json.loads(content)


def save_sample_csv(rows, filepath):
    if not rows:
        return
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def main():
    sample = load_sample(INPUT_CSV, SAMPLE_SIZE)
    save_sample_csv(sample, OUTPUT_SAMPLE_CSV)
    print(f"Loaded {len(sample)} reviews. Starting analysis...")

    results = []
    for i, row in enumerate(sample, 1):
        review_id = row["ReviewID"]
        text = row["ReviewText"]
        rating = row["Rating"]
        print(f"[{i}/{len(sample)}] {review_id}: {text[:60]}...")
        try:
            analysis = call_llm(text)
            results.append(
                {
                    "review_id": review_id,
                    "product_id": row["ProductID"],
                    "rating": rating,
                    "review_text": text,
                    "sentiment": analysis.get("sentiment"),
                    "topic": analysis.get("topic"),
                    "confidence": analysis.get("confidence"),
                }
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append(
                {
                    "review_id": review_id,
                    "product_id": row["ProductID"],
                    "rating": rating,
                    "review_text": text,
                    "sentiment": None,
                    "topic": None,
                    "confidence": None,
                    "error": str(e),
                }
            )

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    success = sum(1 for r in results if r.get("sentiment"))
    print(f"\nDone! {success}/{len(results)} reviews classified.")
    print(f"Results saved to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
