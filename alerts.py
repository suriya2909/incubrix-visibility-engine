"""Evidence-linked comparisons across observation runs."""
import pandas as pd

KEY = ["question_id", "market", "platform"]

def compare_runs(observations: pd.DataFrame, earlier: str, later: str) -> pd.DataFrame:
    if observations.empty: return pd.DataFrame(columns=[*KEY, "alert_type", "before", "after", "before_date", "after_date", "note"])
    df = observations.copy()
    df["measurement_date"] = pd.to_datetime(df["measurement_date"], errors="coerce")
    old = df[df.measurement_date.eq(pd.Timestamp(earlier))].sort_values("measurement_date").drop_duplicates(KEY, keep="last").set_index(KEY)
    new = df[df.measurement_date.eq(pd.Timestamp(later))].sort_values("measurement_date").drop_duplicates(KEY, keep="last").set_index(KEY)
    rows = []
    for key in old.index.union(new.index):
        a = old.loc[key] if key in old.index else None
        b = new.loc[key] if key in new.index else None
        if a is None or b is None: continue
        for col, added, lost in [("brand_mentioned", "New brand mention", "Lost brand mention"), ("brand_cited", "New citation", "Lost citation")]:
            av, bv = bool(a[col]) if pd.notna(a[col]) else False, bool(b[col]) if pd.notna(b[col]) else False
            if av != bv: rows.append(dict(zip(KEY,key), alert_type=added if bv else lost, before=av, after=bv, before_date=str(a.measurement_date.date()), after_date=str(b.measurement_date.date()), note="Recorded observation difference; sampling and response variation may explain change."))
        if pd.notna(a.get("position")) and pd.notna(b.get("position")) and a.position != b.position:
            rows.append(dict(zip(KEY,key), alert_type="Google position change", before=a.position, after=b.position, before_date=str(a.measurement_date.date()), after_date=str(b.measurement_date.date()), note="Recorded rank difference; location, device and sampling may differ."))
        prior={x.strip() for x in str(a.get("competitors", "")).split(",") if x.strip()}
        current={x.strip() for x in str(b.get("competitors", "")).split(",") if x.strip()}
        if prior != current:
            rows.append(dict(zip(KEY,key), alert_type="Competitor visibility difference", before=", ".join(sorted(prior)), after=", ".join(sorted(current)), before_date=str(a.measurement_date.date()), after_date=str(b.measurement_date.date()), note="Competitors recorded in sampled answers differ; not a market-wide trend."))
        mentioned=b.get("brand_mentioned", False); cited=b.get("brand_cited", False)
        if not (pd.notna(mentioned) and bool(mentioned)) and not (pd.notna(cited) and bool(cited)):
            rows.append(dict(zip(KEY,key), alert_type="Repeated visibility gap", before="observed run", after="no brand mention/citation", before_date=str(a.measurement_date.date()), after_date=str(b.measurement_date.date()), note="No brand presence in either of these two comparable observations."))
    return pd.DataFrame(rows)

def generate_alerts(observations: pd.DataFrame) -> pd.DataFrame:
    if observations.empty: return pd.DataFrame(columns=["alert_type", *KEY, "note"])
    dates = pd.to_datetime(observations.measurement_date, errors="coerce").dropna().dt.strftime("%Y-%m-%d").drop_duplicates().sort_values().tolist()
    alerts=compare_runs(observations, dates[-2], dates[-1]) if len(dates) >= 2 else pd.DataFrame()
    latest=pd.to_datetime(observations.measurement_date,errors="coerce").max()
    if pd.notna(latest) and (pd.Timestamp.today().normalize()-latest.normalize()).days > 30:
        alerts=pd.concat([alerts,pd.DataFrame([{"alert_type":"Stale measurements", "note":f"Latest observation is {(pd.Timestamp.today().normalize()-latest.normalize()).days} days old."}])],ignore_index=True)
    if len(dates) < 2:
        alerts=pd.concat([alerts,pd.DataFrame([{"alert_type":"Incomplete comparison", "note":"At least two dated runs are required for change detection."}])],ignore_index=True)
    return alerts
