import json
import re
from difflib import get_close_matches
from pprint import pprint


def load_kb():
    with open("kb/knowledge_base.json", "r") as f:
        return json.load(f)


def search_kb(query: str, category: str = None, top_k: int = 3):
    kb = load_kb()
    query_lower = query.lower()

    results = []

    # Search specific category if provided
    if category and category in kb:
        for key, value in kb[category].items():
            score = fuzzy_match(query_lower, key.lower(), value.lower())
            if score > 0.3:
                results.append(
                    {"category": category, "question": key, "answer": value, "score": score})

    # Search all categories
    else:
        for cat, entries in kb.items():
            for key, value in entries.items():
                score = fuzzy_match(query_lower, key.lower(), value.lower())
                if score > 0.3:
                    results.append(
                        {"category": cat, "question": key, "answer": value, "score": score})

    return sorted(results[:top_k], key=lambda x: x["score"], reverse=True)


def fuzzy_match(query, key, value):
    # Simple fuzzy matching (you can use embeddings for better results)
    matches = sum(1 for word in query.split() if word in key or word in value)
    return matches / max(len(query.split()), 1)


# Test it
if __name__ == "__main__":
    pprint(search_kb("What's My Bill due date?"))
