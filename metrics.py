"""CSV loading, schema validation and evidence-based visibility metrics."""
from pathlib import Path
from typing import Iterable
import pandas as pd

QUESTION_COLUMNS = ["question_id", "question", "topic", "why_relevant", "source_url", "source_date", "market", "language", "research_status", "verification_notes"]
VISIBILITY_COLUMNS = ["observation_id", "question_id", "question", "market", "measurement_date", "platform", "location_setting", "position", "answer_box", "ai_overview", "brand_mentioned", "brand_cited", "competitors", "source_urls", "raw_answer", "raw_answer_file", "evidence_file", "verification_status", "limitations"]
CITATION_COLUMNS = ["target_id", "url", "publisher", "page_type", "related_question", "relevance_reason", "observed_evidence", "value_reason", "earning_approach", "content_angle", "status"]

BOOL_COLUMNS = {"answer_box", "ai_overview", "brand_mentioned", "brand_cited"}
NUMERIC_COLUMNS = {"position"}

def empty_frame(columns: Iterable[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=list(columns))

def read_csv(path, columns, *, uploaded=None) -> pd.DataFrame:
    """Read local or uploaded CSV, normalise expected fields, and fail clearly."""
    try:
        df = pd.read_csv(uploaded if uploaded is not None else path, keep_default_na=False)
    except (OSError, UnicodeError, pd.errors.ParserError, ValueError) as exc:
        raise ValueError(f"Could not read CSV: {exc}") from exc
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError("CSV is missing required columns: " + ", ".join(missing))
    for col in BOOL_COLUMNS.intersection(df.columns):
        df[col] = df[col].map(parse_bool).astype("boolean")
    for col in NUMERIC_COLUMNS.intersection(df.columns):
        df[col] = pd.to_numeric(df[col].replace("", pd.NA), errors="coerce")
    return df

def parse_bool(value):
    if pd.isna(value) or str(value).strip() == "": return pd.NA
    if isinstance(value, bool): return value
    val = str(value).strip().lower()
    if val in {"true", "1", "yes", "y"}: return True
    if val in {"false", "0", "no", "n"}: return False
    return pd.NA

def load_data(root="."):
    root = Path(root)
    def load(name, columns):
        path = root / "data" / name
        if not path.exists(): return empty_frame(columns)
        return read_csv(path, columns)
    return (load("questions.csv", QUESTION_COLUMNS), load("visibility.csv", VISIBILITY_COLUMNS), load("citation_targets.csv", CITATION_COLUMNS))

def metrics(questions: pd.DataFrame, observations: pd.DataFrame) -> dict:
    checked = observations[observations.get("verification_status", pd.Series(dtype=str)).eq("verified")].copy() if not observations.empty else observations.copy()
    google = checked[checked.get("platform", pd.Series(dtype=str)).str.lower().eq("google")]
    positions = pd.to_numeric(google.get("position", pd.Series(dtype=float)), errors="coerce").dropna()
    completed = observations[observations.get("verification_status", pd.Series(dtype=str)).isin(["completed", "verified"])] if not observations.empty else observations
    return {"question_count": len(questions), "observation_count": len(observations), "completed_checks": len(completed),
            "google_coverage_pct": round(100 * min(google.loc[google["position"].notna(), "question_id"].nunique(), len(questions)) / len(questions), 1) if len(questions) and len(google) else None,
            "google_avg_position": round(float(positions.mean()), 1) if len(positions) else None,
            "mention_rate": round(100 * checked["brand_mentioned"].fillna(False).astype(bool).mean(), 1) if len(checked) else None,
            "citation_rate": round(100 * checked["brand_cited"].fillna(False).astype(bool).mean(), 1) if len(checked) else None,
            "verified_count": len(checked)}

def export_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")
