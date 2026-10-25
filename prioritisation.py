"""Transparent opportunity scoring (a project heuristic, not a search algorithm)."""
import pandas as pd

WEIGHTS = {"business_relevance": .25, "visibility_gap": .25, "potential_impact": .20, "implementation_ease": .15, "evidence_confidence": .15}

def score_opportunity(scores: dict, weights: dict = WEIGHTS) -> float:
    if set(weights) - set(scores): raise ValueError("A component score is missing")
    if any(float(scores[k]) < 0 or float(scores[k]) > 100 for k in weights): raise ValueError("Scores must be in the 0–100 range")
    total = sum(float(scores[k]) * float(weights[k]) for k in weights)
    weight_sum = sum(weights.values())
    return round(total / weight_sum, 1) if weight_sum else 0.0

def rank_opportunities(df: pd.DataFrame) -> pd.DataFrame:
    components = list(WEIGHTS)
    out = df.copy()
    for name in components:
        out[name] = pd.to_numeric(out.get(name, 0), errors="coerce").fillna(0).clip(0, 100)
    out["priority_score"] = out.apply(lambda row: score_opportunity(row.to_dict()), axis=1)
    out["priority"] = pd.cut(out.priority_score, [-1, 39.99, 69.99, 100], labels=["Low", "Medium", "High"])
    return out.sort_values("priority_score", ascending=False)
