# IncuBrix Visibility Engine

A local Streamlit dashboard and evidence tracker for an AEO, SEO and GEO visibility assessment. It brings question research, recorded search/AI observations, technical audit findings, prioritisation, draft content, citation prospects, alerts and reports into one reviewable workspace.

The application is an evidence tracker, not a search scraper. It does not automatically query Google or AI assistants, bypass platform controls, access private analytics, or create simulated results. Keep actual findings, assumptions and recommendations distinct.

## Current assessment status

Snapshot: 2026-10-25.

- 100 question texts are in `data/questions.csv`. They are sourced examples, not 100 independently validated search-demand findings; market coverage and volumes remain unverified.
- One observation, `OBS001`, is in `data/visibility.csv`. It records a public web research tool result for Q004. It is marked `completed`, not `verified`, and is not a Google or target-AI measurement. Its capture and limitations are in `evidence/raw_answers/OBS001.md`.
- Because there are no verified Google or target-assistant observations, the dashboard shows a dash for Google coverage, average position, mention rate and citation rate. The dash means unavailable from verified data; it does not mean zero visibility.
- 30 citation-plan entries are research leads returned by accessible web searches. Google-specific ranking and AI-answer citation have not been confirmed.
- 20 technical audit items are documented. Production changes and technical validations are not complete.
- 10 content pages are drafts. Product-specific claims need owner review before publication.
- The 13-week launch plan contains proposed work and goals, not achieved outcomes.

See `WORKBOOK.md` for the evidence index, verified page-text observations and key opportunities. See `reports/assessment_report.md` for the current completion summary.

## What the application does

The Streamlit app is divided into ten work areas, selected from the left sidebar:

1. **Executive Overview** - Displays question count, recorded checks, verified Google coverage and average position, plus verified mention and citation rates. When verified observations exist, it charts mention/citation rates by platform and observation counts by market. It also provides market, platform, topic, verification-status and date filters for the observation table. Empty states explain what evidence is needed; the app does not fill missing values with zero.
2. **Question Research** - Displays and exports the question bank, accepts a reviewed question CSV, and provides a form for adding a question. Form-created questions are saved as `planned`. A question being present in the CSV does not prove search demand or volume.
3. **Search and AI Visibility** - Displays and exports observation records, accepts a reviewed CSV, and provides a manual observation form. Suggested target platforms are Google, ChatGPT, Gemini, Copilot and Perplexity; record the actual interface used because availability can change. The app does not query those platforms for you.
4. **Technical SEO Audit** - Displays `audit/technical_audit.md`, including evidence, recommendations, priorities, effort, status and validation limitations.
5. **Prioritisation Engine** - Loads `data/opportunities.csv` and applies the documented weighted score in `prioritisation.py`. The current file contains only its header, so there are no scored opportunities yet.
6. **Content Studio** - Displays each Markdown draft in `content/`. Drafts are not published by the app and should not be treated as fact-checked until product claims and sources are reviewed.
7. **Citation Opportunity Planner** - Displays, imports and exports `data/citation_targets.csv`. Its observed-result count reflects rows with non-empty `observed_evidence`; it is not a count of confirmed Google rankings or AI citations.
8. **Change Alerts** - Compares observations from the latest two recorded dates and displays descriptive changes or an incomplete-comparison alert. A two-date difference is not a statistically significant trend.
9. **Reports and Exports** - Downloads the question, observation and citation CSVs; displays available weekly, assessment, launch-plan and technical-audit reports; and generates a simple brief from a selected question.
10. **Assessment Progress** - Summarises deliverables and labels partial or incomplete research rather than treating templates as completed evidence.

The interface uses Streamlit components with local CSS styling. The only declared runtime dependencies are Streamlit and Pandas; no external charting service or API key is required.

The dependency versions are pinned to the versions used for local verification (pandas 3.1.0 and streamlit 1.66.1). Update these pins deliberately, then rerun the unit tests and Streamlit smoke check before deploying an upgrade.

## Architecture and files

```text
app.py                         Streamlit entry point and user interface
metrics.py                     CSV schemas, loading, conversions, metrics, exports
prioritisation.py               Weighted opportunity scoring
alerts.py                       Dated observation comparisons and alerts
requirements.txt                Python runtime dependencies

data/questions.csv              Question research records
data/visibility.csv             Append-only observation history
data/citation_targets.csv       Citation research leads
data/opportunities.csv          Scoring inputs (currently header-only)

audit/technical_audit.md        20-item technical/content audit
content/*.md                    10 individual content drafts
evidence/search_results/        Public search research log
evidence/raw_answers/           Captured raw answers and limitations
evidence/screenshots/           Intended location for genuine screenshots
reports/                        Weekly, completion and 90-day reports
WORKBOOK.md                     Assessment summary and evidence index
CITATION_PLAN.md                 Citation planner explanation
LAUNCH_PLAN.md                   13-week launch plan
tests/test_core.py               Automated unit tests
```

The app resolves its data and report paths relative to `app.py`, so launch it from the project folder for predictable behavior. CSV data is stored locally. The `.gitignore` excludes `.venv`, Python cache files, `.env` files and Streamlit secrets.

## Setup and launch on Windows

Open PowerShell in the project folder. Use the environment's Python executable directly; activation is optional.

### Create the virtual environment (first setup only)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Run the tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

### Launch the dashboard

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. Streamlit reruns the app when files change; refresh the browser with Ctrl+R if the screen does not update. If port 8501 is already in use, run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

If `.venv` already exists, skip its creation and install dependencies only when needed. Do not commit `.venv` to the project repository.

## GitHub repository and cloud deployment

GitHub stores the source code and can run the automated checks in `.github/workflows/tests.yml`. GitHub Pages does not run this Python/Streamlit application. To make the dashboard accessible as a web app, deploy the repository through Streamlit Community Cloud (or another Python-capable host).

### Repository layout for deployment

- Keep `app.py` and `requirements.txt` at the repository root. The app uses paths relative to `app.py` and expects the `data/`, `audit/`, `content/`, `evidence/` and `reports/` folders beside it.
- `.streamlit/config.toml` supplies the dashboard theme and disables anonymous usage statistics.
- `.github/workflows/tests.yml` runs unit tests, compiles the modules, and smoke-tests the Streamlit app on pushes and pull requests to `main`.
- `.gitignore` excludes the local virtual environment, Python caches, `.env` files and `.streamlit/secrets.toml`. Do not commit credentials or personal tokens.

### Deploy with Streamlit Community Cloud

1. Push the project to a GitHub repository. Keep it private when it contains assessment work or evidence intended only for the company.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) and connect the GitHub account that can access the repository. Private repositories require granting the requested repository access, and deployment requires repository admin permission.
3. Choose **Create app**, select the repository and `main` branch, and enter `app.py` as the app file path. The root `requirements.txt` is used to install dependencies.
4. Deploy and inspect the app logs. Open each navigation section and confirm the committed datasets and evidence paths load.

See the official [Streamlit deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [private repository connection instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account).

**Cloud storage limitation:** this app writes CSV changes to local files. Streamlit Community Cloud does not guarantee persistence of local filesystem changes across restarts or rebuilds. The committed CSVs will provide the initial data, but question/observation/citation edits made in the deployed app may be lost. Treat a cloud deployment as a review/demo until a persistent database or approved external data store is implemented. Do not collect ongoing team research in the cloud app until persistence and access controls are addressed. See Streamlit's [data connection guidance](https://docs.streamlit.io/develop/concepts/connections/connecting-to-data).

## Research and data workflow

### 1. Review and refine questions

Use **Question Research** to inspect the 100 sourced question texts. For each question, confirm its relevance to the current IncuBrix product, source URL/date, language and market. Add demand evidence only when actually observed (for example, an appropriate search, interview, support-ticket or customer-research source). Do not infer volume from a question being present on a page or in a community thread.

New questions need a unique ID, exact text and topic. The form saves them as `planned`; a source or note should be added as research proceeds. Export a CSV before making bulk changes.

### 2. Run manual platform checks

For the assessment's full target matrix, measure the same 100 questions on Google and four currently accessible AI assistants, across the United States and two additional selected markets, on two distinct measurement dates. That is up to 3,000 question/platform/market/date records (100 x 5 x 3 x 2). If the practical scope is smaller, report the actual cohort and do not imply complete coverage.

Keep settings consistent between dates where possible. For each run:

1. Select a saved question and enter the exact query, platform, market, date and location/language/device settings.
2. For Google, record the observed organic position and whether an answer box or AI Overview appeared. Do not treat a search-result position returned by a different research tool as a Google position.
3. For assistants, save the answer text, whether IncuBrix was mentioned, whether a source link to IncuBrix appeared, competitors and relevant cited URLs.
4. Save genuine screenshots and raw answer records under `evidence/`; use project-relative paths in the observation form.
5. Record limitations such as market setting unavailable, login state, model/interface, personalization or result instability.
6. Repeat the same settings on a second date. Append new observation IDs; do not delete earlier runs.

The current schema stores platform, market/date, a free-text location setting, position, answer-box/AI-Overview and brand flags, competitors, URLs, raw answer/evidence paths, status and limitations. Put language, device and assistant model/version in `location_setting` or `limitations` because there are no separate columns for all of them.

The public research observation `OBS001` is deliberately labelled `Public web research tool`, with unspecified location and status `completed`. It proves only that this tool returned the official site for the recorded query. It is not part of the Google/four-assistant matrix and should not be presented as a ranking or AI visibility result.

**Important: current manual-form status behavior.** On submit, an observation becomes `verified` when the evidence path points to an existing file inside the project, raw answer text is present, and both mention/citation fields are set to Yes or No. If the answer is present but those conditions are not met, it becomes `completed`; with no answer it becomes `planned`. This is a completeness rule in the current UI, not an independent review of the evidence or proof that the result came from the selected platform. Review the saved evidence before relying on a `verified` row for assessment metrics. The form does not offer a `failed` option; use CSV maintenance/import to record a genuinely failed attempt.

### 3. Import and export CSV files

The app's CSV upload controls preview a file before the explicit append action. Required columns must be present. Uploads with blank or duplicate record IDs, or IDs already in the local dataset, are rejected instead of silently overwriting existing rows. Exports use UTF-8 with a BOM for spreadsheet compatibility.

Back up the relevant CSV before manual editing or importing. Maintain unique question, observation and target IDs. Do not paste credentials, personal tokens or private customer information into questions, answers, notes or evidence.

## CSV schemas

The authoritative column lists are declared in `metrics.py`. Extra columns may be retained when loading an existing CSV, but all required columns must exist.

### `data/questions.csv`

| Column | Meaning |
| --- | --- |
| `question_id` | Stable unique question identifier, such as `Q001`. |
| `question` | Exact question text to research. |
| `topic` | Topic or intent grouping. |
| `why_relevant` | Business relevance and evidence context. |
| `source_url` | URL where the question or source evidence was observed. |
| `source_date` | Source publication/observation date, if known. |
| `market` | Intended or researched market; unspecified values are not market validation. |
| `language` | Query language. |
| `research_status` | Question research state, for example sourced or planned. |
| `verification_notes` | Caveats and what remains to confirm. |

### `data/visibility.csv`

| Column | Meaning |
| --- | --- |
| `observation_id` | Unique ID for this single platform/question/market/date record. |
| `question_id`, `question` | Link to the saved question and the exact text used. |
| `market`, `measurement_date`, `platform` | Where, when and on which interface it was measured. |
| `location_setting` | Location, language, device, model/interface settings and other context. |
| `position` | Numeric Google organic position when actually observed; blank otherwise. |
| `answer_box`, `ai_overview` | Whether the relevant Google feature appeared; blank means unknown/not captured. |
| `brand_mentioned`, `brand_cited` | Whether the answer/result names IncuBrix and whether it links/cites IncuBrix. |
| `competitors` | Competitor names observed in the same result/answer. |
| `source_urls` | Relevant URLs returned/cited, separated by line or semicolon as appropriate. |
| `raw_answer`, `raw_answer_file` | Captured answer/result text or a path to the full capture. |
| `evidence_file` | Screenshot or other supporting evidence file path, when available. |
| `verification_status` | `planned`, `failed`, `completed` or `verified`, according to actual work. |
| `limitations` | Sampling, access, location, model, evidence and comparability caveats. |

Boolean values accept `true/false`, `yes/no`, `y/n`, and `1/0`; blanks or unrecognized values become unknown. `position` is converted to a number; malformed values become blank. Other schema validation is intentionally lightweight, so reviewers must still check date formats, IDs, URLs and consistency.

### `data/citation_targets.csv`

`target_id`, `url`, `publisher`, `page_type`, `related_question`, `relevance_reason`, `observed_evidence`, `value_reason`, `earning_approach`, `content_angle` and `status` describe a page prospect and why it may matter. A search-result appearance is not proof of a Google rank, an AI citation, an editorial relationship or an earned mention. Validate each prospect on the intended platform before counting it toward a platform-specific assessment requirement.

### `data/opportunities.csv`

This file starts with `opportunity_id`, `question_id`, `title`, five score inputs, `next_action` and `evidence_reference`. The five inputs are listed under the scoring section below. Add an evidence-backed row before expecting a ranked output. Missing score inputs are coerced to zero by the ranking helper; do not use that behavior as a substitute for scoring and evidence.

## Metric definitions and display behavior

All headline visibility rates use rows whose `verification_status` equals `verified`.

- **Research questions**: number of rows in `questions.csv`.
- **Recorded checks**: observations with status `completed` or `verified`. This is a collection count, not a target-platform coverage claim.
- **Google coverage**: unique question IDs with a numeric position in verified Google observations, divided by the number of questions, capped at 100%. The result can include repeated markets/dates; report the cohort when sharing it.
- **Average Google position**: arithmetic mean of numeric positions on verified rows whose platform is Google. Repeated observations are row-weighted.
- **Verified mention rate / citation rate**: percentage of verified observation rows with the corresponding boolean true. Unknown values are treated as false in the current calculation. Rates are row-based, not unique-question-based, and can be distorted by an unbalanced sample.
- **Dashboard charts**: show verified mention/citation percentages grouped by platform and verified observation counts by market. Unknown booleans are treated as false, consistent with the headline rates.
- **Dash in an empty metric card**: no eligible verified evidence is available for that metric. It is not a zero result.

The dashboard does not calculate search demand, total market share, statistically significant trend, organic signup attribution or a private analytics baseline. Organic signup reporting requires authorized, correctly configured analytics and attribution.

## Opportunity prioritisation

`prioritisation.py` computes a weighted average from five manually assigned 0-100 component scores:

| Component | Weight |
| --- | ---: |
| Business relevance | 25% |
| Visibility gap | 25% |
| Potential impact | 20% |
| Implementation ease | 15% |
| Evidence confidence | 15% |

Formula: `score = sum(component_score * component_weight) / sum(weights)`.

Current priority bands are Low below 40, Medium from 40 to below 70, and High from 70 to 100. Scores outside 0-100 are rejected by `score_opportunity`; the table helper clips values and fills missing columns/values with zero, so complete the inputs before interpreting results. This is a project planning heuristic only. It is not an official Google, search engine or AI ranking algorithm. Keep a brief rationale and evidence reference for each component score.

## Change alerts

`alerts.py` compares the latest two distinct measurement dates. It pairs records by `question_id`, `market` and `platform`, then can report changes in mention/citation flags, numeric position, competitor list, repeated gaps and stale measurements. At least two dates are needed; observations older than 30 days can generate a stale alert.

Alerts are descriptive. The comparison code does not establish statistical significance and does not independently ensure that settings or verification status match. Before interpreting a change, confirm the query, market, location, device and platform/model are comparable. With two dates, describe a recorded difference, not a trend.

## Audit, content, citations and reports

- `audit/technical_audit.md` documents 20 proposed/blocked technical and content checks, evidence limits, recommendations, priorities, effort and validation status. No item should be described as fixed or validated unless it was actually changed and rechecked.
- `content/` contains 10 individual draft pages. They are research-led starting points; confirm current features, prices, integrations, examples and other product claims with an owner. Add citations for external factual claims and use a publishing/CMS review before release.
- `data/citation_targets.csv` contains 30 observed search leads. The details and ethical earning approaches are summarized in `CITATION_PLAN.md`; platform-specific evidence is still required.
- `reports/weekly_summary.md` is a current baseline summary and must be refreshed from stored evidence after research runs.
- `reports/90_day_launch_plan.md` and `LAUNCH_PLAN.md` describe a 13-week plan. Targets are proposals, not results; numeric uplifts need a baseline and approval.
- `reports/assessment_report.md` and `WORKBOOK.md` state what is complete, partial or still missing. Update them when evidence changes.

## Testing and validation

The eight unit tests in `tests/test_core.py` cover empty metrics, CSV schema and conversions, invalid uploads, Google/mention metric calculations, opportunity scoring, dated comparisons/alerts and CSV export.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q app.py metrics.py prioritisation.py alerts.py
```

Optional Streamlit UI smoke check:

```powershell
.\.venv\Scripts\python.exe -c "from streamlit.testing.v1 import AppTest; app = AppTest.from_file('app.py').run(); print('Exceptions:', len(app.exception)); [print(item.message) for item in app.exception]"
```

A successful run should report eight passing unit tests; the AppTest check should report zero exceptions. A browser HTTP 200 confirms that the local Streamlit shell responds, but it does not by itself prove every screen or data workflow works. Manually open each sidebar section and test CSV uploads with a disposable copy.

## Limitations and responsible use

- No automated Google or assistant collection is implemented. Collect those results manually or add an authorized, terms-compliant integration only after reviewing platform policies.
- No CAPTCHA/access-control bypass, private Search Console or analytics access, full-site crawler, Lighthouse run, production CMS change or deployment is included.
- Public page text and public search results can change. Keep capture date, source URL and query with every research finding.
- Search result ordering from a general web research tool is not a Google position. `OBS001` is intentionally excluded from verified target-platform metrics.
- Two measurement dates are only two samples. Do not claim statistical significance or generalize beyond the recorded cohort.
- The audit findings, content drafts, citation leads and launch goals are recommendations or templates until verified/approved.
- Do not publish pages, contact publishers, or claim customer outcomes on behalf of IncuBrix from this local app.

## Data safety and backups

The app stores data as local CSV and evidence as local files. Before editing or importing, make a copy of `data/` and any evidence you need to preserve. CSV writes from the app append new records rather than replacing existing rows, but manual edits and external sync tools can still overwrite data. Never commit `.env`, API keys, account credentials, private user data or tokens. The `.gitignore` includes common local-secret and virtual-environment paths.
