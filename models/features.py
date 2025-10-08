def extract_features(description: str) -> dict:
    return {
        "length": len(description),
        "num_words": len(description.split()),
        "has_keyword_report": int("report" in description.lower()),
        "has_keyword_email": int("email" in description.lower())
    }