"""IncuBrix visibility research tracker. Run: streamlit run app.py"""
from pathlib import Path
import pandas as pd
import streamlit as st
from metrics import QUESTION_COLUMNS, VISIBILITY_COLUMNS, CITATION_COLUMNS, load_data, read_csv, metrics, export_csv
from prioritisation import rank_opportunities
from alerts import generate_alerts

ROOT = Path(__file__).parent
st.set_page_config(page_title="IncuBrix | Visibility Engine", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
:root { --ink:#142337; --muted:#65758b; --line:#e7edf2; --paper:#f4f7f6; --green:#176b58; }
.stApp { background:var(--paper); color:var(--ink); font-family:Arial,sans-serif; }
.block-container { max-width:1480px; padding:2rem 2.4rem 3rem; }
h1,h2,h3,[data-testid="stMetricValue"] { color:var(--ink); }
[data-testid="stSidebar"] { background:#10291f; border-right:1px solid #264235; }
[data-testid="stSidebar"] * { color:#edf6f0; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.48rem .65rem; border-radius:9px; }
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:#1b3d30; }
[data-testid="stSidebar"] hr { border-color:#365445; }
[data-testid="stMetric"] { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem 1.1rem; box-shadow:0 3px 12px #15233708; }
[data-testid="stMetricLabel"] { color:var(--muted); font-size:.82rem; }
[data-testid="stMetricValue"] { font-size:1.8rem; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
[data-testid="stForm"] { background:#fff; border:1px solid var(--line); border-radius:14px; padding:1.1rem; }
.ib-brand { display:flex; align-items:center; gap:11px; padding:0 0 1rem; }
.ib-mark { display:grid; place-items:center; height:39px; width:39px; border-radius:12px; background:#d2f0df; color:#145640; font:bold 15px Arial,sans-serif; }
.ib-brand-name { font:bold 16px Arial,sans-serif; color:#fff; }
.ib-brand-sub { color:#b9cfc2; font-size:10px; letter-spacing:.12em; text-transform:uppercase; margin-top:2px; }
.ib-hero { display:flex; justify-content:space-between; align-items:flex-end; gap:1rem; border-bottom:1px solid var(--line); padding:0 0 1.25rem; margin-bottom:1.35rem; }
.ib-eyebrow { color:var(--green); font-size:.72rem; font-weight:700; letter-spacing:.15em; text-transform:uppercase; margin-bottom:.35rem; }
.ib-hero h1 { margin:0; font-size:clamp(1.55rem,2.4vw,2.15rem); font-weight:800; letter-spacing:-.04em; }
.ib-hero p { color:var(--muted); margin:.4rem 0 0; font-size:.95rem; }
.ib-tag { border:1px solid #d4e5dc; background:#fafffc; padding:.45rem .7rem; border-radius:999px; color:#426354; font-size:.76rem; white-space:nowrap; }
.ib-section { font-size:1.02rem; font-weight:700; color:var(--ink); margin:.6rem 0 .7rem; }
.ib-note { background:#edf6f1; border-left:3px solid var(--green); border-radius:0 9px 9px 0; padding:.8rem 1rem; color:#365749; font-size:.89rem; }
.stButton button, .stDownloadButton button { border-radius:9px; font-weight:650; }
@media (max-width:700px) { .block-container{padding:1rem 1rem 2rem}.ib-hero{align-items:flex-start;flex-direction:column}.ib-tag{white-space:normal} }
</style>""", unsafe_allow_html=True)
try:
    questions, observations, citations = load_data(ROOT)
except ValueError as exc:
    st.error(f"Data file issue: {exc}")
    questions, observations, citations = pd.DataFrame(columns=QUESTION_COLUMNS), pd.DataFrame(columns=VISIBILITY_COLUMNS), pd.DataFrame(columns=CITATION_COLUMNS)

st.sidebar.markdown('''<div class="ib-brand"><div class="ib-mark">IB</div><div><div class="ib-brand-name">IncuBrix</div><div class="ib-brand-sub">Visibility Engine</div></div></div>''', unsafe_allow_html=True)
nav = st.sidebar.radio("WORKSPACE", ["Executive Overview", "Question Research", "Search and AI Visibility", "Technical SEO Audit", "Prioritisation Engine", "Content Studio", "Citation Opportunity Planner", "Change Alerts", "Reports and Exports", "Assessment Progress"])
st.sidebar.markdown("---")
st.sidebar.caption("Evidence-first SEO, AEO and GEO research. Only verified observations count toward visibility metrics.")
descriptions = {
    "Executive Overview": "A clear view of research coverage, recorded visibility and the next evidence-backed actions.",
    "Question Research": "Manage the question set and keep source research separate from measured results.",
    "Search and AI Visibility": "Record comparable search and assistant observations with traceable evidence.",
    "Technical SEO Audit": "Review observed site issues, recommended fixes and validation status.",
    "Prioritisation Engine": "Rank opportunities using transparent inputs and a documented project heuristic.",
    "Content Studio": "Review research-led content drafts and product-claim verification notes.",
    "Citation Opportunity Planner": "Track relevant pages and the evidence needed to qualify each opportunity.",
    "Change Alerts": "Compare dated observations and flag changes with their supporting records.",
    "Reports and Exports": "Download current datasets and assessment reports.",
    "Assessment Progress": "See which deliverables are ready, partial or still need evidence.",
}
st.markdown(f'<div class="ib-hero"><div><div class="ib-eyebrow">Research workspace / 2027 assessment</div><h1>{nav}</h1><p>{descriptions[nav]}</p></div><div class="ib-tag">Evidence status: actuals only</div></div>', unsafe_allow_html=True)

def download(label, df, filename): st.download_button(label, export_csv(df), file_name=filename, mime="text/csv")
def upload(label, columns, key):
    f=st.file_uploader(label, type=["csv"], key=key)
    if f:
        try:
            frame=read_csv(None,columns,uploaded=f)
            st.success(f"Loaded {len(frame)} rows. Review before replacing or merging the local dataset.")
            st.dataframe(frame, use_container_width=True)
            names={"q_upload":("questions.csv","question_id"),"v_upload":("visibility.csv","observation_id"),"c_upload":("citation_targets.csv","target_id")}
            if st.button("Append reviewed rows to local tracker",key=f"append_{key}"):
                filename,idcol=names[key]
                current=read_csv(ROOT/"data"/filename,columns)
                if frame[idcol].astype(str).str.strip().eq("").any(): st.error(f"Every row needs a {idcol}.")
                elif frame[idcol].duplicated().any(): st.error(f"Uploaded {idcol} values must be unique.")
                elif set(frame[idcol].astype(str)) & set(current[idcol].astype(str)): st.error(f"Some {idcol} values already exist. Resolve duplicates before importing.")
                else:
                    pd.concat([current,frame],ignore_index=True).to_csv(ROOT/"data"/filename,index=False,encoding="utf-8-sig")
                    st.success(f"Appended {len(frame)} rows to data/{filename}; prior records were retained.")
        except ValueError as exc: st.error(str(exc))

if nav == "Executive Overview":
    st.subheader("Executive overview")
    if questions.empty and observations.empty:
        st.info("Your workspace is ready. Import questions or record the first real observation to start building visibility evidence.")
    m=metrics(questions, observations)
    a,b,c,d=st.columns(4)
    a.metric("Research questions",m["question_count"])
    b.metric("Recorded checks",m["completed_checks"])
    c.metric("Google coverage",f'{m["google_coverage_pct"]}%' if m["google_coverage_pct"] is not None else "\u2014")
    d.metric("Average Google position",m["google_avg_position"] if m["google_avg_position"] is not None else "\u2014")
    x,y=st.columns(2); x.metric("Verified mention rate",f'{m["mention_rate"]}%' if m["mention_rate"] is not None else "\u2014"); y.metric("Verified citation rate",f'{m["citation_rate"]}%' if m["citation_rate"] is not None else "\u2014")
    st.caption("A dash means no verified observations are available for that metric; it does not mean zero visibility.")
    st.markdown('<div class="ib-section">Visibility signals</div>', unsafe_allow_html=True)
    verified = observations[observations.verification_status.eq("verified")].copy() if not observations.empty else observations.copy()
    if verified.empty:
        st.markdown('<div class="ib-note">Charts will appear when you add verified observations. Planned or unverified checks stay out of these visibility signals.</div>', unsafe_allow_html=True)
    else:
        chart_left, chart_right = st.columns(2)
        platform_rows = verified.groupby("platform", dropna=False).agg(
            mentions=("brand_mentioned", lambda values: values.fillna(False).astype(bool).mean() * 100),
            citations=("brand_cited", lambda values: values.fillna(False).astype(bool).mean() * 100),
        )
        chart_left.markdown("<div class='ib-section'>Mention and citation rate by platform</div>", unsafe_allow_html=True)
        chart_left.bar_chart(platform_rows[["mentions", "citations"]], y_label="Verified observations (%)", color=["#176b58", "#d89b42"])
        chart_right.markdown("<div class='ib-section'>Verified checks by market</div>", unsafe_allow_html=True)
        chart_right.bar_chart(verified.groupby("market", dropna=False).size().rename("Verified checks"), y_label="Observation count", color="#176b58")
        st.caption("Charts use only rows marked verified. Unknown mention and citation flags count as no, consistent with the metric definition.")
    if not observations.empty:
        st.markdown('<div class="ib-section">Explore recorded observations</div>', unsafe_allow_html=True)
        filters=st.columns(5)
        market=filters[0].selectbox("Market",["All",*sorted(observations.market.dropna().astype(str).unique())])
        platform=filters[1].selectbox("Platform",["All",*sorted(observations.platform.dropna().astype(str).unique())])
        topic=filters[2].selectbox("Topic",["All",*sorted(questions.topic.dropna().astype(str).unique())])
        status=filters[3].selectbox("Verification",["All",*sorted(observations.verification_status.dropna().astype(str).unique())])
        valid_dates=pd.to_datetime(observations.measurement_date,errors="coerce").dropna()
        date_range=filters[4].date_input("Measurement dates",value=(valid_dates.min().date(),valid_dates.max().date()) if len(valid_dates) else ())
        view=observations.copy()
        if market!="All": view=view[view.market.eq(market)]
        if platform!="All": view=view[view.platform.eq(platform)]
        if status!="All": view=view[view.verification_status.eq(status)]
        if len(date_range)==2:
            dates=pd.to_datetime(view.measurement_date,errors="coerce").dt.date
            view=view[(dates>=date_range[0])&(dates<=date_range[1])]
        if topic!="All" and "topic" in questions:
            ids=questions.loc[questions.topic.eq(topic),"question_id"]; view=view[view.question_id.isin(ids)]
        st.dataframe(view,use_container_width=True)
        st.caption("Date range: filter the measurement_date column in the table, or use the visibility page for all recorded runs.")
    else: st.caption("Market, platform and date breakdowns will appear once observations exist.")

elif nav == "Question Research":
    st.subheader("Question research")
    st.write("Research statuses separate proposed questions from researched and verified demand. Programmatic result collection is intentionally not simulated.")
    st.dataframe(questions,use_container_width=True)
    download("Export questions",questions,"questions.csv")
    upload("Import reviewed question CSV",QUESTION_COLUMNS,"q_upload")
    with st.expander("Add a research question"):
        with st.form("question_form"):
            qid=st.text_input("Question ID")
            query=st.text_input("Exact question")
            topic=st.text_input("Topic")
            relevance=st.text_area("Why it is relevant")
            source=st.text_input("Supporting source URL (optional until verified)")
            sourcedate=st.text_input("Source date (YYYY-MM-DD, optional)")
            market=st.selectbox("Market",["United States","United Kingdom","India","Singapore","Other"])
            language=st.text_input("Language",value="English")
            notes=st.text_area("Research and verification notes")
            submitted=st.form_submit_button("Save question as planned")
        if submitted:
            if not qid.strip() or not query.strip(): st.error("Question ID and exact question are required.")
            elif qid in set(questions.question_id): st.error("That question ID already exists.")
            else:
                row={"question_id":qid.strip(),"question":query.strip(),"topic":topic,"why_relevant":relevance,"source_url":source,"source_date":sourcedate,"market":market,"language":language,"research_status":"planned","verification_notes":notes}
                updated=pd.concat([questions,pd.DataFrame([row])],ignore_index=True)
                updated.to_csv(ROOT/"data"/"questions.csv",index=False,encoding="utf-8-sig")
                st.success("Saved as planned. This does not count as demand research until you verify it.")
    st.markdown("**Manual workflow:** select a question, set market/language and capture the exact query, date and location; inspect Google and four available assistants manually; preserve answer text and evidence; mark verified only after a second-person or reproducible check.")

elif nav == "Search and AI Visibility":
    st.subheader("Search and AI visibility")
    st.caption("Supported platforms can be selected per run. Suggested manual panel: Google Search, ChatGPT, Google Gemini, Microsoft Copilot, Perplexity. Availability and access change; record the actual interface/version used.")
    st.dataframe(observations,use_container_width=True)
    download("Export observations",observations,"visibility.csv")
    upload("Import observation CSV",VISIBILITY_COLUMNS,"v_upload")
    with st.expander("Record a manual observation"):
        with st.form("observation_form"):
            oid=st.text_input("Observation ID")
            qid=st.selectbox("Question",questions.question_id.tolist() if len(questions) else [""])
            platform=st.selectbox("Platform",["Google","ChatGPT","Gemini","Copilot","Perplexity","Other"])
            market=st.selectbox("Market",["United States","United Kingdom","India","Singapore","Other"],key="obs_market")
            measured=st.date_input("Measurement date")
            location=st.text_input("Location / language / device setting")
            position=st.text_input("Google organic position (leave blank when not applicable)")
            mentioned=st.selectbox("IncuBrix mentioned?",["Unknown","Yes","No"])
            cited=st.selectbox("IncuBrix cited/linked?",["Unknown","Yes","No"])
            answerbox=st.selectbox("Answer box appeared?",["Unknown","Yes","No"])
            overview=st.selectbox("AI Overview appeared?",["Unknown","Yes","No"])
            competitors=st.text_input("Competitor brands")
            urls=st.text_area("Relevant source URLs (one per line)")
            answer=st.text_area("Raw answer or result notes")
            evidence=st.text_input("Evidence file path")
            limitations=st.text_area("Limitations / verification notes")
            save_obs=st.form_submit_button("Append observation")
        if save_obs:
            if not oid.strip() or not qid: st.error("Observation ID and a saved question are required.")
            elif oid in set(observations.observation_id): st.error("That observation ID already exists.")
            else:
                yn={"Unknown":pd.NA,"Yes":True,"No":False}
                pos=pd.to_numeric(position,errors="coerce") if position.strip() else pd.NA
                evidence_path=(ROOT/evidence).resolve() if evidence.strip() else None
                evidence_exists=bool(evidence_path and evidence_path.is_file() and ROOT.resolve() in evidence_path.parents)
                status="verified" if evidence_exists and answer.strip() and mentioned!="Unknown" and cited!="Unknown" else ("completed" if answer.strip() else "planned")
                row={"observation_id":oid.strip(),"question_id":qid,"question":questions.loc[questions.question_id.eq(qid),"question"].iloc[0],"market":market,"measurement_date":str(measured),"platform":platform,"location_setting":location,"position":pos,"answer_box":yn[answerbox],"ai_overview":yn[overview],"brand_mentioned":yn[mentioned],"brand_cited":yn[cited],"competitors":competitors,"source_urls":urls,"raw_answer":answer,"raw_answer_file":"","evidence_file":str(evidence_path) if evidence_exists else evidence,"verification_status":status,"limitations":limitations}
                updated=pd.concat([observations,pd.DataFrame([row])],ignore_index=True)
                updated.to_csv(ROOT/"data"/"visibility.csv",index=False,encoding="utf-8-sig")
                st.success(f"Appended observation as {status}. {'' if status=='verified' else 'Add a real evidence file and verify the record before counting it as verified.'}")
    st.markdown("**Observation fields:** per-question platform and market, exact date and location setting, organic position or answer features, mention/citation flags, competitors, source URLs, raw-answer/evidence references, verification and limitations. Append repeat runs; do not overwrite history.")

elif nav == "Technical SEO Audit":
    st.subheader("Technical SEO audit")
    report=ROOT/"audit"/"technical_audit.md"
    st.markdown(report.read_text(encoding="utf-8") if report.exists() else "Audit report not prepared.")

elif nav == "Prioritisation Engine":
    st.subheader("Prioritisation engine")
    st.caption("Project heuristic: 25% relevance + 25% visibility gap + 20% impact + 15% ease + 15% evidence confidence. Each input is 0–100. This is not a Google or AI ranking formula.")
    file=ROOT/"data"/"opportunities.csv"
    if file.exists():
        try: st.dataframe(rank_opportunities(pd.read_csv(file)),use_container_width=True)
        except Exception as exc: st.error(f"Could not score opportunities: {exc}")
    else: st.info("No research-backed opportunity scores exist yet. Add evidence and component scores to data/opportunities.csv.")

elif nav == "Content Studio":
    st.subheader("Content studio")
    pages=sorted((ROOT/"content").glob("*.md"))
    if not pages: st.info("No content briefs are published. Drafts must be grounded in verified research and product claims.")
    for page in pages:
        with st.expander(page.stem.replace("_"," ").title()): st.markdown(page.read_text(encoding="utf-8"))

elif nav == "Citation Opportunity Planner":
    st.subheader("Citation opportunity planner")
    st.caption("Only verified third-party result/citation evidence qualifies as an opportunity. Templates and unverified prospects are not counted.")
    st.dataframe(citations,use_container_width=True)
    st.metric("Observed web search result pages",int(citations.observed_evidence.astype(str).str.strip().ne("").sum()) if len(citations) else 0)
    st.caption("Result appearance was recorded through accessible web research; Google-specific ranking and AI-answer citation checks remain pending.")
    download("Export citation targets",citations,"citation_targets.csv")
    upload("Import citation opportunity CSV",CITATION_COLUMNS,"c_upload")

elif nav == "Change Alerts":
    st.subheader("Change alerts")
    alerts=generate_alerts(observations)
    if alerts.empty: st.info("No recorded changes. Two comparable dated observation runs are needed.")
    else: st.dataframe(alerts,use_container_width=True)
    st.caption("Differences are descriptive; sampling changes can explain them. Two dates do not establish statistical significance.")

elif nav == "Reports and Exports":
    st.subheader("Reports and exports")
    download("Visibility observations",observations,"visibility.csv"); download("Questions",questions,"questions.csv"); download("Citation targets",citations,"citation_targets.csv")
    for name in ["weekly_summary.md","90_day_launch_plan.md","assessment_report.md"]:
        p=ROOT/"reports"/name
        if p.exists():
            with st.expander(name): st.markdown(p.read_text(encoding="utf-8")); st.download_button(f"Download {name}",p.read_bytes(),file_name=name)
    audit_file=ROOT/"audit"/"technical_audit.md"
    if audit_file.exists(): st.download_button("Download technical audit",audit_file.read_bytes(),file_name="technical_audit.md")
    opp_file=ROOT/"data"/"opportunities.csv"
    if opp_file.exists(): st.download_button("Download prioritisation inputs",opp_file.read_bytes(),file_name="opportunities.csv")
    if not questions.empty:
        selected=st.selectbox("Question for content brief",questions.question_id.tolist())
        row=questions[questions.question_id.eq(selected)].iloc[0]
        st.text_area("Brief",f"Question: {row.question}\nTopic: {row.topic}\nEvidence status: {row.research_status}\nSource: {row.source_url}\n\nResearch the exact intent and verify all product claims before drafting.")

elif nav == "Assessment Progress":
    st.subheader("Assessment progress")
    checks=[("Question bank (100 sourced questions)","Partial",f"{len(questions)}/100 source-backed question texts logged; market, demand and platform research remains incomplete."),
            ("Visibility research (Google + 4 AI, 3 markets, 2 dates)","Incomplete","Must be completed with actual observations; no automatic scraping."),
            ("Technical fixes (20 with evidence and validation)","Partial","20 audit items documented; production implementation and validation remain pending."),
            ("Content pages (10 fact-checked pages)","Drafts","10 evidence-limited drafts created; product-owner review required."),
            ("Citation opportunities (30 observed pages)","Partial","30 pages observed in accessible web search; Google-specific and AI-answer citation evidence remains unverified."),
            ("Run comparisons and alerts","Ready; no data","At least two comparable measurement dates required."),
            ("Automated tests","Implemented","Run the commands in README.md; current environment uses unittest.")]
    st.dataframe(pd.DataFrame([{"Deliverable":n,"Status":status,"Note":note} for n,status,note in checks]),use_container_width=True)
