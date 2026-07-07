# Indian Army Supply Chain Risk Monitor

An AI-powered risk intelligence dashboard that analyzes geopolitical crisis scenarios and their impact on the multi-tier supplier network behind six armored vehicle programs — flagging state-owned-enterprise (SOE) exposure, identifying at-risk suppliers, and recommending Indian alternate suppliers for crisis resilience.

Built and run entirely in **Google Colab** on T4 GPU.

---

## 1. Purpose

Modern defense platforms depend on globally distributed, multi-tier supplier networks. A geopolitical shock — sanctions, a border conflict, an export ban, a shipping-lane closure — can silently propagate through Tier-1 and Tier-2 suppliers and through hidden ownership chains (a supplier that looks "safe" on paper but is majority-owned by a state-linked entity in an adversarial country).

This project simulates that analysis for an Indian Army armored-vehicle supply chain: given a crisis scenario, it identifies which suppliers are exposed, why, how severely, and what Indian alternates could replace them.

---

## 2. Data Model

All data lives in three CSV files uploaded at runtime (no data is hardcoded into the script):

| File | Rows | Description |
|---|---|---|
| `supply_chain.csv` | Vehicle → Category → Component → Tier-1 Supplier (+country) → Tier-2 Supplier (+country) | The physical bill-of-materials / supplier graph for armored vehicle programs |
| `ownership.csv` | Tier-1 Supplier → Owner → Owner Type → Owner Country → Stake % → Board Role → Financial Distress Score | Beneficial ownership chains, used to detect SOE and foreign-state exposure |
| `indian_alternates.csv` | Company → Component Category → Components Supplied → Country → Lead Time in Weeks | Candidate Indian suppliers that could substitute for an at-risk foreign supplier |

These three files together are the relational equivalent of a graph: `supply_chain.csv` encodes `Product –CONTAINS→ Component –SUPPLIED_BY→ Supplier –LOCATED_IN→ Country`, and `ownership.csv` encodes `Supplier –OWNED_BY→ Owner –LOCATED_IN→ Country`. The system reasons over these relationships in pandas rather than a graph database 

**Robust ingestion:** all three loaders try `utf-8 → utf-8-sig → cp1252 → latin-1` in sequence (Excel-saved CSVs default to Windows-1252), and apply name normalization (`normalize_country()` / `COUNTRY_ALIASES` for countries, `ALIAS_MAP` for supplier names) so that inconsistent spellings (e.g. "USA" vs "United States", "Ford Motor Co." vs "Ford Motor Company") don't silently break filtering.

---

## 3. AI Pipeline

### 3.1 Why an LLM, not a trained graph model
The project deliberately uses a **local, open-weight LLM (Qwen2.5-3B-Instruct)** running inside Colab for reasoning and scoring — not just prompting a hosted API — to demonstrate a self-contained AI system. The LLM's role is narrow and grounded:
- Interpret the user-selected crisis scenario (region/country in conflict).
- Enrich each exposed supplier with contextual risk commentary.
- Propose candidate alternate suppliers when the deterministic data doesn't already cover a gap.

### 3.2 Deterministic-first architecture
Small LLMs are not reliable enough to be the sole source of a defense risk score, so the pipeline is **deterministic-first, LLM-assisted**:
1. A deterministic formula (below) computes a baseline score for every supplier from the CSV data.
2. The LLM independently proposes a score and commentary for crisis-exposed suppliers.
3. The **higher** of the two scores is kept (never let the LLM silently lower a data-backed risk score).
4. Per-supplier scores are then used to deterministically recompute portfolio-level KPIs — the LLM's own self-reported top-line numbers are discarded, since a 3B model has no guaranteed cross-field consistency between the portfolio score it states and the per-supplier scores it generates.
5. Three-attempt retry with a full deterministic fallback: **the dashboard always renders**, even if the LLM fails or produces malformed JSON every time.

### 3.3 Crisis exposure detection (three paths)
A supplier is flagged as crisis-exposed if **any** of the following hold for the user-selected crisis country/region:
- **Direct** — the Tier-1 supplier itself is located in the crisis country.
- **Tier-2 Dependency** — the supplier's upstream Tier-2 supplier is located in the crisis country (risk propagates upward to the Tier-1 supplier).
- **Ownership-Linked** — the supplier is owned (in whole or part) by an entity headquartered in the crisis country, even if the supplier's own operations are elsewhere.

The crisis country selected by the user (not the LLM's self-reported `crisis_countries` field, which is spelling-inconsistent) is treated as the single source of truth for filtering.

### 3.4 Supplier Risk Scoring Formula

```
Risk Score = Base Weight
           + Geopolitical Signal Score   (0–20)
           + Ownership Risk Score        (0–15)
           + Financial Distress Score    (0–10)
           + Concentration Penalty       (0–5)
→ capped at 100
```

| Component | Range | What It Represents |
|---|---|---|
| Base Weight | fixed | Category/component criticality |
| Geopolitical Signal Score | 0–20 | Whether the supplier's Tier-1/Tier-2 country or ownership chain is tied to the active crisis scenario |
| Ownership Risk Score | 0–15 | SOE / state-linked ownership stake, sourced from `ownership.csv` |
| Financial Distress Score | 0–10 | Placeholder hook (`financial_distress` column in `ownership.csv`) for future financial-health signals.                                      0 = Financially healthy — no distress signals.                                                                                                                              5 = Moderate distress — some financial strain but not existential.                                                                                                          10 = Severe distress — active red flags: heavy losses.  |
| Concentration Penalty | 0–5 | Single-source dependency — no alternate on record for that component |

This deterministic score is blended with the LLM's independent estimate by taking the higher value (Section 3.2), so the LLM can escalate a risk the formula misses but can never quietly suppress one the data supports.


### 3.5 Alternate Supplier Readiness Scoring System

```
Readiness Score = Capability Match      (0–30)
                 + Country Risk Bonus    (0–25)
                 + Capacity Signal       (0–20)
                 + Lead-Time Score       (0–15)
                 + Existing Relationship (0–10)
→ Capped at 100
```

| Component              | Range | What It Represents |
|------------------------|-------|------------------------------------------------|
| **Capabilty Match** | 0–30  | Exact match between *indian_alternates.component_category* and the at-risk supplier’s component/category → 30. Partial keyword match > 15. Category-only match > 5. |
| **Country Risk Bonus**    | 0–25  | Alternate’s country = India → 25. Allied/neutral country → 10–15. Same country as the crisis-hit supplier → 0. |
| **Capacity Signal**    | 0–20  | alternate supplier's production volume and manufacturing capability. |
| **Lead-Time Score**    | 0–15  | Operational delay and efficiency involved in onboarding and receiving parts from an alternate supplier compared to the original one. |
| **Existing Relationship** | 0–10 | If the alternate already supplies a different component in the same vehicle program → 10 (faster onboarding, known vendor). Else 0. |

---

## 4. Dashboard

The output is a Plotly-based interactive dashboard, structured to mirror the CREAO Supply Chain Risk Monitor layout defined in `dashboard.json`:

- **Top Alert Banner** — overall crisis risk level for the selected scenario.
- **4 KPI Cards** — Portfolio Risk Score, Suppliers Monitored, Critical Alerts — all scoped to the crisis-exposed subset, not the full portfolio.
- **Risk Chart** — bar chart of risk scores by category, current vs. prior scan (where prior data exists).
- **Full Supplier Risk Register** — every supplier in the portfolio, sorted by risk score, with a **Crisis Exposure** column (Direct / Tier-2 Dependency / Ownership-Linked / None). This table is intentionally left unfiltered so the analyst can see the whole portfolio at a glance.
- **Ownership Analysis Table** — flagged suppliers with owner name, owner type, owner country, and stake %, highlighting SOE and foreign-state exposure.
- **Alternate Suppliers — Readiness & Cost** — Indian alternates for crisis-exposed suppliers only, pulled from `indian_alternates.csv`.
- **Config/Graph Status Card** — ingestion summary (row counts loaded, any dedup warnings, LLM call success/fallback status).

---

## 5. How to Run

1. Open the notebook in Google Colab.
2. Run the setup cells (model download — Qwen2.5-3B-Instruct — happens once per runtime; optionally point `HF_HOME` at Google Drive to persist the model across sessions).
3. When prompted, upload `supply_chain.csv`, `ownership.csv`, and `indian_alternates.csv` via the Colab file picker (`google.colab.files.upload()`) — no data is baked into the notebook itself.
4. Select the crisis scenario (country/region) when prompted.
5. Run the remaining cells. The notebook will:
   - Ingest and normalize the three CSVs.
   - Run three-path crisis exposure detection.
   - Score every supplier deterministically, then enrich crisis-exposed suppliers via the local LLM (with automatic fallback).
   - Render the full interactive dashboard inline, with a static HTML fallback if the Colab renderer is unavailable.

---

## 7. Scope & Limitations

- This is a demonstration/prototype system built on a small, illustrative dataset — not a production intelligence feed.
- Geopolitical "crisis" input is user-selected, not sourced from live news or threat feeds.
- The system does not currently connect to any external graph database — all relational reasoning is done in-memory over the three CSVs using pandas.
