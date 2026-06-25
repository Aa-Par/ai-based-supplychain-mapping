
"""
Indian Army Supply Chain Risk Monitor 
====================================================
• HuggingFace LLM (Phi-3-mini) for all analysis — no live web search, no cloud APIs
• Deterministic baseline scoring with LLM overlay (graceful fallback if LLM fails)
• Plotly interactive dashboard (multi-panel: risk scores, tables, ownership, alternates)
• Full ownership CSV integration with SOE-keyword detection and stake-depth filtering
• Supplier rollup (multi-vehicle / multi-component aggregation)
• Dynamic country-crisis filter via interactive prompt
"""

# ── CELL 1: Install ───────────────────────────────────────────
# !pip install -q transformers accelerate torch plotly pandas pyyaml

# ── CELL 2: Backend Config ────────────────────────────────────
import os

LLM_BACKEND  = "huggingface"                        # only supported backend
HF_MODEL_ID  = "microsoft/Phi-3-mini-4k-instruct"   # FREE, runs on CPU or GPU
HF_TOKEN     = os.environ.get("HF_TOKEN", "")

OWNERSHIP_DEPTH_PCT = 1   # show ownership stakes ≥ this %

# ── CELL 3: CSV Loaders ────────────────────────────────────────────────────────
import pandas as pd

def _get_local_or_upload(path_hint: str, label: str) -> str:
    if os.path.exists(path_hint):
        print(f"✅ Found {label} at {path_hint}")
        return path_hint
    try:
        from google.colab import files
        print(f"⬆️  Please upload {label} (.csv) in the dialog that appears below...")
        uploaded = files.upload()
        if not uploaded:
            raise FileNotFoundError(f"No file uploaded for {label}")
        return list(uploaded.keys())[0]
    except ImportError:
        raise FileNotFoundError(f"{label} not found at {path_hint}.")


def load_supply_chain_csv(path_hint="/content/supply_chain.csv") -> list:
    """
    Load the supply chain Neo4j export.
    Expected columns: vehicle, component (or category+component_name),
    tier1_supplier, tier1_country, tier2_supplier, tier2_country
    """
    fp = _get_local_or_upload(path_hint, "supply_chain.csv")
    df = pd.read_csv(fp)
    graph = []
    for _, row in df.iterrows():
        tier2_supplier = row.get("tier2_supplier")
        tier1_supplier = row.get("tier1_supplier")
        if pd.isna(tier2_supplier) or str(tier2_supplier).strip() == "":
            tier2_supplier = tier1_supplier
            tier2_country  = row.get("tier1_country")
        else:
            tier2_country = row.get("tier2_country")

        component_label = row.get("tier2_component")
        if pd.isna(component_label) or str(component_label).strip() == "":
            component_label = row.get("component", row.get("component_name", row.get("function", "")))

        graph.append({
            "vehicle":    str(row.get("vehicle", "")),
            "component":  str(component_label),
            "tier2":      str(tier2_supplier),
            "tier1":      str(tier1_supplier),
            "t2_country": str(tier2_country)  if not pd.isna(tier2_country)  else "Unknown",
            "t1_country": str(row.get("tier1_country", "Unknown")),
        })
    print(f"✅ Loaded {len(graph)} supply chain edges from {fp}")
    return graph, df          # return raw df too for rollup


def load_ownership_csv(path_hint="/content/ownership.csv") -> dict:
    """
    Load the ownership Neo4j export.
    Key column can be named 'supplier' OR 'tier1_supplier' (both handled).
    Other columns: owner, owner_type / owner_node_type, owner_country, stake_pct, note / board_role
    """
    fp = _get_local_or_upload(path_hint, "ownership.csv")
    df = pd.read_csv(fp)
    registry: dict = {}
    for _, row in df.iterrows():
        # Accept either column name for the supplier key
        supplier = row.get("supplier") if not pd.isna(row.get("supplier", float("nan"))) \
                   else row.get("tier1_supplier")
        if supplier is None or (isinstance(supplier, float) and pd.isna(supplier)):
            continue
        supplier = str(supplier).strip()

        stake = row.get("stake_pct")
        try:
            stake = float(stake) if not pd.isna(stake) else 0.0
        except (TypeError, ValueError):
            stake = 0.0

        owner_type = row.get("owner_type")
        if pd.isna(owner_type):
            owner_type = row.get("owner_node_type", "Unknown")

        board_role = row.get("board_role", row.get("note", ""))
        if pd.isna(board_role):
            board_role = ""

        entry = {
            "owner":      str(row.get("owner", "Unknown")),
            "type":       str(owner_type),
            "country":    str(row.get("owner_country", "Unknown")),
            "stake_pct":  stake,
            "board_role": str(board_role),
        }
        registry.setdefault(supplier, []).append(entry)

    print(f"✅ Loaded ownership records for {len(registry)} suppliers from {fp}")
    return registry, df       # return raw df too for SOE rollup


# ── CELL 4: Load data ─────────────────────────────────────────
NEO4J_GRAPH,        SUPPLY_DF  = load_supply_chain_csv()
OWNERSHIP_REGISTRY, OWNER_DF   = load_ownership_csv()

print(f"\nGraph edges       : {len(NEO4J_GRAPH)}")
print(f"Ownership suppliers: {len(OWNERSHIP_REGISTRY)}")


# ── CELL 5: Build supplier rollup (from Code 2) ───────────────────────────────
import re

SOE_KEYWORDS = re.compile(
    r"government|sovereign|state|gic|temasek|bpifrance|lic of india|soe|"
    r"public sector|national investment|pension fund|insurer",
    re.I,
)

# Flag state-linked rows in the raw ownership DataFrame
_owner_col = "tier1_supplier" if "tier1_supplier" in OWNER_DF.columns else "supplier"
OWNER_DF["is_state_linked"] = (
    OWNER_DF["owner_type"].astype(str).str.contains(SOE_KEYWORDS) |
    OWNER_DF["owner"].astype(str).str.contains(SOE_KEYWORDS)
)

soe_summary_df = (
    OWNER_DF[OWNER_DF["is_state_linked"]]
    .groupby(_owner_col)
    .agg(
        max_state_stake=("stake_pct", "max"),
        state_owners=("owner", lambda s: ", ".join(sorted(set(s)))),
    )
    .reset_index()
    .rename(columns={_owner_col: "supplier"})
)
soe_summary_df["soe_status"] = soe_summary_df["max_state_stake"].apply(
    lambda p: "Controlled" if p >= 25 else "Linked"
)
print(f"State-linked Tier-1 suppliers (SOE keyword scan): {len(soe_summary_df)}")

# Build unified supplier registry (one row per unique supplier with all vehicles/components)
_records = []
for _, r in SUPPLY_DF.iterrows():
    t1 = str(r.get("tier1_supplier", ""))
    t2 = str(r.get("tier2_supplier", ""))
    t1c = str(r.get("tier1_country", "Unknown"))
    t2c = str(r.get("tier2_country", "Unknown"))
    comp = str(r.get("component", r.get("component_name", "")))
    veh  = str(r.get("vehicle", ""))

    if t1:
        _records.append({"supplier": t1, "tier": "Tier-1", "country": t1c, "vehicle": veh, "component": comp})
    if t2 and t2 != t1 and t2.strip() not in ("", "nan"):
        _records.append({"supplier": t2, "tier": "Tier-2", "country": t2c, "vehicle": veh, "component": comp})

supplier_registry_df = pd.DataFrame(_records).drop_duplicates(subset=["supplier", "vehicle", "component"])

SUPPLIER_ROLLUP = (
    supplier_registry_df.groupby("supplier")
    .agg(
        countries=("country",   lambda s: sorted(set(s))),
        vehicles =("vehicle",   lambda s: sorted(set(s))),
        components=("component",lambda s: sorted(set(s))),
        tiers    =("tier",      lambda s: sorted(set(s))),
    )
    .reset_index()
    .merge(
        soe_summary_df[["supplier", "soe_status", "state_owners", "max_state_stake"]],
        on="supplier", how="left",
    )
)

print(f"Total unique suppliers in portfolio: {len(SUPPLIER_ROLLUP)}")


# ── CELL 6: Optional CREAO config loading ─────────────────────
import yaml, json as _json

def _try_load(path_hint, label, loader):
    if os.path.exists(path_hint):
        try:
            with open(path_hint, "r", encoding="utf-8") as f:
                return loader(f)
        except Exception as e:
            print(f"⚠️ Couldn't parse {label}: {e}")
    return None

CREAO_CONFIG   = _try_load("/content/config.yaml",   "config.yaml",   yaml.safe_load)
CREAO_SKILL_MD = _try_load("/content/SKILL.md",       "SKILL.md",      lambda f: f.read())
CREAO_MANIFEST = _try_load("/content/manifest.json",  "manifest.json", _json.load)

AGENT_TITLE = (CREAO_MANIFEST or {}).get("name", "Indian Army Supply Chain Risk Monitor")

_DEPTH_MAP = {"one_percent": 1, "five_percent": 5, "ten_percent": 10, "twenty_five_percent": 25}
if CREAO_CONFIG:
    for field in CREAO_CONFIG.get("form", {}).get("fields", []):
        if field.get("id") == "ownership_depth":
            OWNERSHIP_DEPTH_PCT = _DEPTH_MAP.get(field.get("default_value"), OWNERSHIP_DEPTH_PCT)
    print(f"✅ CREAO config.yaml — ownership depth set to ≥{OWNERSHIP_DEPTH_PCT}%")

SKILL_RUBRIC_TEXT = ""
if CREAO_SKILL_MD:
    text  = CREAO_SKILL_MD
    start = text.find("### Step 4")
    end   = text.find("### Step 6")
    SKILL_RUBRIC_TEXT = text[start:end].strip() if (start != -1 and end != -1) else text[:3000]
    print("✅ SKILL.md scoring rubric loaded for prompt grounding")


# ── CELL 7: LLM backend (HuggingFace only) ───────────────────
import json as _json, textwrap, warnings, ast
warnings.filterwarnings("ignore")


def _repair_truncated_json(text: str) -> str:
    text = text.rstrip()
    if text.endswith(","):
        text = text[:-1]
    open_braces   = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    text += "]" * max(open_brackets, 0)
    text += "}" * max(open_braces, 0)
    return text


def _extract_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    text = re.sub(r"<\|.*?\|>", "", text).strip()
    start = text.find("{")
    if start == -1:
        return "{}"
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return _repair_truncated_json(text[start:])


def _parse_llm_output(raw: str) -> dict:
    cleaned = _extract_json(raw)
    for candidate in [cleaned, cleaned.replace("True", "true").replace("False", "false").replace("None", "null")]:
        try:
            return _json.loads(candidate)
        except Exception:
            pass
    try:
        return ast.literal_eval(cleaned)
    except Exception:
        pass
    return {}


def build_llm_client():
    print(f"🤗 Loading: {HF_MODEL_ID}")
    print("   ⏳ First load can take 2-8 min on Colab free tier (downloads ~2.4 GB).")
    try:
        from transformers import pipeline
        import torch
        device_label = (
            "GPU ✅" if torch.cuda.is_available()
            else "CPU ⚠️ — Runtime > Change runtime type > T4 GPU for 10x speed"
        )
        print(f"   Device: {device_label}")
        pipe = pipeline(
            "text-generation",
            model=HF_MODEL_ID,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )

        def call_llm(system_msg: str, user_msg: str) -> str:
            try:
                prompt = pipe.tokenizer.apply_chat_template(
                    [{"role": "system", "content": system_msg},
                     {"role": "user",   "content": user_msg}],
                    tokenize=False, add_generation_prompt=True,
                )
            except Exception:
                prompt = (
                    f"<|system|>\n{system_msg}<|end|>\n"
                    f"<|user|>\n{user_msg}<|end|>\n<|assistant|>\n"
                )
            out = pipe(
                prompt,
                max_new_tokens=3500,
                temperature=0.2,
                do_sample=True,
                return_full_text=False,
            )
            raw = out[0]["generated_text"]
            print(f"  🔍 LLM raw (first 400 chars): {raw[:400]}")
            return raw

        print("✅ HuggingFace pipeline ready")
        return call_llm

    except Exception as e:
        print(f"⚠️ Local pipeline failed ({e}) — falling back to HF Inference API...")
        import requests as req

        def call_hf_api(system_msg: str, user_msg: str) -> str:
            prompt = (
                f"<|system|>\n{system_msg}<|end|>\n"
                f"<|user|>\n{user_msg}<|end|>\n<|assistant|>\n"
            )
            headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
            r = req.post(
                f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}",
                headers=headers,
                json={"inputs": prompt, "parameters": {
                    "max_new_tokens": 3500,
                    "temperature": 0.2,
                    "return_full_text": False,
                }},
                timeout=180,
            )
            result = r.json()
            raw = result[0].get("generated_text", "") if isinstance(result, list) else str(result)
            print(f"  🔍 HF API raw (first 400 chars): {raw[:400]}")
            return raw

        return call_hf_api


print("\n🔄 Initializing LLM — first load may take a few minutes...")
LLM_FN = build_llm_client()


# ── CELL 8: LLM Scenario Analysis (no web search) ────────────
def analyze_scenario(llm_fn, scenario: str, neo4j_graph: list, supplier_rollup: pd.DataFrame) -> dict:
    """
    Ask the LLM to assess the full supplier portfolio against the given scenario.
    Uses only the provided supply-chain graph and rollup data — no live web search.
    """
    graph_summary = "\n".join([
        f"  {r['vehicle']} | {r['component']} | "
        f"Tier2: {r['tier2']} ({r['t2_country']}) → Tier1: {r['tier1']} ({r['t1_country']})"
        for r in neo4j_graph
    ])

    rollup_summary = "\n".join([
        f"  Supplier: {row['supplier']} | Countries: {row['countries']} | "
        f"Vehicles: {row['vehicles']} | Components: {row['components']} | "
        f"Tiers: {row['tiers']} | SOE Status: {row.get('soe_status', 'None')} | "
        f"State Owners: {row.get('state_owners', 'None')} | "
        f"Max State Stake: {row.get('max_state_stake', 0)}%"
        for _, row in supplier_rollup.iterrows()
    ])

    rubric_block = (
        f"\n\nFOLLOW THIS EXACT SCORING RUBRIC:\n{SKILL_RUBRIC_TEXT}\n"
        if SKILL_RUBRIC_TEXT else ""
    )

    system_msg = textwrap.dedent(f"""
    You are a defense supply chain risk analyst supporting the Indian Army.
    You will be given a geopolitical scenario, a supply chain graph extracted from Neo4j,
    and a supplier rollup table (with SOE/state-ownership flags).

    Your job:
    1. Identify which suppliers are exposed to the scenario.
    2. Score each unique supplier (0-100) using: country risk, dependency risk,
       ownership risk (SOE flags), logistics risk, and financial exposure.
    3. Recommend alternate suppliers for the highest-risk ones.
    4. Base ALL reasoning on the provided data — do NOT invent facts or use external sources.
    5. Return ONLY a valid JSON object — no markdown fences, no preamble, no commentary.
    {rubric_block}
    """).strip()

    user_msg = textwrap.dedent(f"""
    SCENARIO: {scenario}

    SUPPLY CHAIN GRAPH (from Neo4j):
    {graph_summary}

    SUPPLIER ROLLUP (with SOE flags):
    {rollup_summary}

    Return a JSON object with this EXACT structure (fill every field):
    {{
      "scenario_summary": "<1-2 sentence plain English summary of the crisis>",
      "crisis_countries": ["<country1>", "<country2>"],
      "overall_risk_level": "CRITICAL | HIGH | MEDIUM | LOW",
      "portfolio_risk_score": <integer 0-100>,
      "executive_summary": "<2-3 sentence risk summary for the Indian Army>",
      "suppliers": [
        {{
          "name": "<supplier name>",
          "country": "<country>",
          "component": "<what they supply>",
          "vehicle": "<which vehicle(s)>",
          "risk_score": <integer 0-100>,
          "risk_reason": "<1 sentence why>",
          "is_sole_source": <true|false>,
          "tier": <1 or 2>
        }}
      ],
      "critical_alerts": ["<alert1>", "<alert2>", "<alert3>"],
      "immediate_actions": ["<action1>", "<action2>", "<action3>"],
      "alternate_suppliers": [
        {{
          "replaces": "<at-risk supplier name>",
          "name": "<alternate name>",
          "country": "<country>",
          "readiness_score": <integer 0-100>,
          "lead_time_weeks": <integer>,
          "cost_premium_pct": <integer>,
          "reason": "<why a good alternate>"
        }}
      ],
      "signals_detected": <integer>
    }}
    """).strip()

    for attempt in range(1, 4):
        try:
            raw = llm_fn(
                system_msg,
                user_msg if attempt == 1
                else f"Scenario: {scenario}\nReturn ONLY valid JSON matching the schema exactly. No prose.",
            )
            result = _parse_llm_output(raw)
            if result.get("suppliers") is None:
                raise ValueError("Missing 'suppliers' key in LLM output")
            return result
        except Exception as e:
            print(f"  ⚠️ Attempt {attempt}/3 failed ({e})")

    print("  ❌ All LLM attempts failed. Returning minimal placeholder.")
    return {
        "scenario_summary": scenario,
        "crisis_countries": [],
        "overall_risk_level": "UNKNOWN",
        "portfolio_risk_score": 0,
        "executive_summary": "LLM analysis failed — check model backend.",
        "suppliers": [],
        "critical_alerts": ["LLM returned no valid JSON — analysis incomplete"],
        "immediate_actions": ["Check HuggingFace model availability or increase max_new_tokens"],
        "alternate_suppliers": [],
        "signals_detected": 0,
    }


# ── CELL 9: Ownership Analysis Engine ────────────────────────
STATE_TYPES = {
    "Government", "Sovereign Wealth Fund", "Government Investment",
    "Government Pension Fund", "Government Insurer", "SOE", "Industrial Conglomerate",
    "Public Sector",
}

def run_ownership_analysis(suppliers: list, registry: dict, depth_pct: float = 1.0) -> list:
    results = []
    for s in suppliers:
        name = s.get("name", "")
        owners = registry.get(name, [])
        flagged_owners = [o for o in owners if o["stake_pct"] >= depth_pct]

        # Also flag by SOE keyword even if type string doesn't match the set exactly
        state_owners = [
            o for o in flagged_owners
            if o["type"] in STATE_TYPES or SOE_KEYWORDS.search(o["type"]) or SOE_KEYWORDS.search(o["owner"])
        ]
        total_state_pct = min(sum(o["stake_pct"] for o in state_owners), 100)
        soe_flag = (
            any(o["stake_pct"] > 25 and (o["type"] in STATE_TYPES or SOE_KEYWORDS.search(o["type"])) for o in flagged_owners)
            or total_state_pct > 40
        )
        results.append({
            **s,
            "owners":            flagged_owners,
            "state_owners":      state_owners,
            "total_state_pct":   round(total_state_pct, 1),
            "soe_flag":          soe_flag,
            "ownership_risk_score": min(20, int(total_state_pct / 5)),
        })
    return results


# ── CELL 10: Plotly Dashboard ─────────────────────────────────
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from IPython.display import display, HTML
from collections import defaultdict


def render_dashboard(analysis: dict, ownership_data: list):
    suppliers     = analysis.get("suppliers", [])
    alternates    = analysis.get("alternate_suppliers", [])
    score         = analysis.get("portfolio_risk_score", 0)
    level         = analysis.get("overall_risk_level", "UNKNOWN")
    crisis_countries = ", ".join(analysis.get("crisis_countries", ["Unknown"]))

    def rcol(v):
        return "#ef4444" if v >= 70 else "#f59e0b" if v >= 50 else "#22c55e"

    suppliers_sorted = sorted(suppliers, key=lambda x: x.get("risk_score", 0), reverse=True)
    soe_flagged      = [o for o in ownership_data if o.get("soe_flag")]

    fig = make_subplots(
        rows=5, cols=2,
        subplot_titles=(
            f"📊 Supplier Risk Scores — Crisis: {crisis_countries}",
            "🔄 Alternate Supplier Readiness Scores",
            "🚛 Full Supplier Risk Register (All Vehicles)", "",
            f"🏛️ Ownership Analysis — State Stakes ≥{OWNERSHIP_DEPTH_PCT}%",
            "📈 Avg Risk by Country of Origin",
            "🔄 Alternates — Readiness vs Lead Time", "",
            "🔷 Neo4j Graph — Ownership Chain (SOE Flags)", "",
        ),
        specs=[
            [{"type": "bar"},   {"type": "bar"}],
            [{"type": "table", "colspan": 2}, None],
            [{"type": "table"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "table"}],
            [{"type": "table", "colspan": 2}, None],
        ],
        vertical_spacing=0.06,
        row_heights=[0.18, 0.18, 0.18, 0.18, 0.18],
        column_widths=[0.55, 0.45],
    )

    # Row 1-col-1: Supplier risk bar chart
    fig.add_trace(go.Bar(
        x=[s["name"] for s in suppliers_sorted],
        y=[s.get("risk_score", 0) for s in suppliers_sorted],
        marker_color=[rcol(s.get("risk_score", 0)) for s in suppliers_sorted],
        text=[str(s.get("risk_score", 0)) for s in suppliers_sorted],
        textposition="outside", showlegend=False, name="Risk Score",
    ), row=1, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#f59e0b",
                  annotation_text="Alert Threshold (70)", row=1, col=1)

    # Row 1-col-2: Alternate readiness bar
    top_alts = sorted(alternates, key=lambda x: x.get("readiness_score", 0), reverse=True)[:8]
    fig.add_trace(go.Bar(
        x=[a["name"] for a in top_alts],
        y=[a.get("readiness_score", 0) for a in top_alts],
        marker_color=["#22c55e" if a.get("readiness_score", 0) >= 80 else "#f59e0b" for a in top_alts],
        text=[str(a.get("readiness_score", 0)) for a in top_alts],
        textposition="outside", showlegend=False, name="Readiness",
    ), row=1, col=2)

    # Row 2: Full supplier risk register table
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Supplier</b>", "<b>Country</b>", "<b>Component</b>", "<b>Vehicle</b>",
                    "<b>Tier</b>", "<b>Risk Score</b>", "<b>Reason</b>", "<b>Status</b>"],
            fill_color="#1e293b", font=dict(color="white", size=10), align="left", height=26,
        ),
        cells=dict(values=[
            [s["name"] for s in suppliers_sorted],
            [s.get("country", "?") for s in suppliers_sorted],
            [s.get("component", "?") for s in suppliers_sorted],
            [s.get("vehicle", "?") for s in suppliers_sorted],
            [f"Tier {s.get('tier', 1)}" for s in suppliers_sorted],
            [s.get("risk_score", 0) for s in suppliers_sorted],
            [s.get("risk_reason", "") for s in suppliers_sorted],
            ["🔴 CRITICAL" if s.get("risk_score", 0) >= 70
             else "🟡 MEDIUM" if s.get("risk_score", 0) >= 50 else "🟢 LOW"
             for s in suppliers_sorted],
        ],
        fill_color=[[
            "#fee2e2" if s.get("risk_score", 0) >= 70
            else "#fef9c3" if s.get("risk_score", 0) >= 50 else "#dcfce7"
            for s in suppliers_sorted
        ]] * 8,
        font=dict(size=9), align="left", height=20),
    ), row=2, col=1)

    # Row 3-col-1: Ownership table
    own_rows = []
    for o in ownership_data:
        for owner in o.get("owners", []):
            flag = (
                "🚨 SOE FLAG"
                if o.get("soe_flag") and (
                    owner["type"] in STATE_TYPES or SOE_KEYWORDS.search(owner["type"]) or SOE_KEYWORDS.search(owner["owner"])
                )
                else "✅ OK"
            )
            own_rows.append({
                "supplier": o["name"], "owner": owner["owner"], "type": owner["type"],
                "country": owner["country"], "stake": owner["stake_pct"],
                "board": owner.get("board_role", ""), "flag": flag,
            })
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Supplier</b>", "<b>Owner</b>", "<b>Type</b>", "<b>Country</b>",
                    f"<b>Stake %</b><br><sub>(≥{OWNERSHIP_DEPTH_PCT}% shown)</sub>",
                    "<b>Board Role</b>", "<b>Flag</b>"],
            fill_color="#7c3aed", font=dict(color="white", size=10), align="left", height=26,
        ),
        cells=dict(values=[
            [r["supplier"] for r in own_rows], [r["owner"] for r in own_rows],
            [r["type"] for r in own_rows],     [r["country"] for r in own_rows],
            [f"{r['stake']}%" for r in own_rows],
            [r["board"] for r in own_rows],    [r["flag"] for r in own_rows],
        ],
        fill_color=[["#fde8ff" if "SOE" in r["flag"] else "#f0fdf4" for r in own_rows]] * 7,
        font=dict(size=9), align="left", height=20),
    ), row=3, col=1)

    # Row 3-col-2: Avg risk by country
    ctry: dict = defaultdict(list)
    for s in suppliers:
        ctry[s.get("country", "?")].append(s.get("risk_score", 0))
    avg_c = dict(sorted(
        {c: sum(v) / len(v) for c, v in ctry.items()}.items(),
        key=lambda x: x[1], reverse=True,
    ))
    fig.add_trace(go.Bar(
        x=list(avg_c.keys()), y=list(avg_c.values()),
        marker_color=[rcol(v) for v in avg_c.values()],
        text=[f"{v:.0f}" for v in avg_c.values()],
        textposition="outside", showlegend=False,
    ), row=3, col=2)

    # Row 4-col-1: Scatter — readiness vs lead time
    fig.add_trace(go.Scatter(
        x=[a.get("lead_time_weeks", 0) for a in alternates],
        y=[a.get("readiness_score", 0) for a in alternates],
        mode="markers+text",
        text=[a["name"] for a in alternates],
        textposition="top center", textfont=dict(size=8),
        marker=dict(
            size=[max(8, 22 - a.get("cost_premium_pct", 0) // 3) for a in alternates],
            color=[a.get("readiness_score", 0) for a in alternates],
            colorscale="RdYlGn", showscale=True,
            colorbar=dict(title="Readiness", x=0.44, len=0.18, y=0.22),
        ),
        showlegend=False,
    ), row=4, col=1)
    fig.update_xaxes(title_text="Lead Time (weeks)", row=4, col=1)
    fig.update_yaxes(title_text="Crisis Readiness",  row=4, col=1)

    # Row 4-col-2: Alternates summary table
    top12 = sorted(alternates, key=lambda x: x.get("readiness_score", 0), reverse=True)[:10]
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>Replaces</b>", "<b>Alternate</b>", "<b>Country</b>",
                    "<b>Readiness</b>", "<b>Lead wks</b>", "<b>+Cost%</b>", "<b>Reason</b>"],
            fill_color="#0f766e", font=dict(color="white", size=10), align="left", height=26,
        ),
        cells=dict(values=[
            [a.get("replaces", "")            for a in top12],
            [a.get("name", "")                for a in top12],
            [a.get("country", "")             for a in top12],
            [f"{a.get('readiness_score', 0)}/100" for a in top12],
            [a.get("lead_time_weeks", 0)      for a in top12],
            [f"+{a.get('cost_premium_pct', 0)}%" for a in top12],
            [a.get("reason", "")              for a in top12],
        ],
        fill_color=[["#d1fae5" if a.get("readiness_score", 0) >= 80 else "#fef9c3" for a in top12]] * 7,
        font=dict(size=9), align="left", height=20),
    ), row=4, col=2)

    # Row 5: Neo4j ownership chain table (SOE flags)
    neo4j_rows = []
    for o in ownership_data:
        for st in o.get("state_owners", []):
            if st["stake_pct"] >= OWNERSHIP_DEPTH_PCT:
                neo4j_rows.append({
                    "cypher": (
                        f"(:{st['type']}{{name:'{st['owner']}'}})"
                        f"-[:OWNS{{pct:{st['stake_pct']}}}]->"
                        f"(Supplier{{name:'{o['name']}'}})"
                    ),
                    "supplier": o["name"], "owner": st["owner"],
                    "type": st["type"],   "pct":   st["stake_pct"],
                    "flag": "🚨 SOE" if o["soe_flag"] else "⚠️ Watch",
                })
    if neo4j_rows:
        fig.add_trace(go.Table(
            header=dict(
                values=["<b>Neo4j Cypher Relationship</b>", "<b>Supplier</b>",
                        "<b>State Owner</b>", "<b>Stake %</b>", "<b>SOE Flag</b>"],
                fill_color="#1d4ed8", font=dict(color="white", size=10), align="left", height=26,
            ),
            cells=dict(values=[
                [r["cypher"]   for r in neo4j_rows],
                [r["supplier"] for r in neo4j_rows],
                [r["owner"]    for r in neo4j_rows],
                [f"{r['pct']}%" for r in neo4j_rows],
                [r["flag"]     for r in neo4j_rows],
            ],
            fill_color=[["#eff6ff" if r["flag"] == "⚠️ Watch" else "#fde8d8" for r in neo4j_rows]] * 5,
            font=dict(size=9), align="left", height=20),
        ), row=5, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["<b>No state-linked owners found above threshold</b>"],
                fill_color="#1d4ed8", font=dict(color="white"), height=26,
            ),
            cells=dict(values=[["No SOE flags triggered"]], fill_color="#eff6ff", height=20),
        ), row=5, col=1)

    fig.update_layout(
        title=dict(
            text=(
                f"🇮🇳 {AGENT_TITLE.upper()}<br>"
                f"<sup>Scenario: {analysis.get('scenario_summary', '')[:90]}  |  "
                f"Crisis Countries: {crisis_countries}  |  Risk: {score}/100 — {level}  |  "
                f"LLM: HuggingFace ({HF_MODEL_ID})  |  "
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</sup>"
            ),
            font=dict(size=14), x=0.5, xanchor="center",
        ),
        height=2000, paper_bgcolor="#f8fafc",
        font=dict(family="Inter, sans-serif", size=10),
        margin=dict(t=100, b=40, l=40, r=60),
    )
    fig.update_xaxes(tickangle=-35, row=1, col=1)
    fig.update_xaxes(tickangle=-35, row=1, col=2)
    fig.update_xaxes(tickangle=-30, row=3, col=2)
    fig.show()

    # ── HTML KPI panel ────────────────────────────────────────
    alerts_html = "".join(
        f'<div style="background:#fee2e2;border-left:4px solid #ef4444;padding:6px 10px;'
        f'margin:3px 0;border-radius:4px;font-size:11px;">🚨 {a}</div>'
        for a in analysis.get("critical_alerts", []))
    actions_html = "".join(
        f"<li style='margin:2px 0;font-size:11px;'>{a}</li>"
        for a in analysis.get("immediate_actions", []))
    soe_html = "".join(
        f'<div style="background:#fde8ff;border-left:4px solid #7c3aed;padding:6px 10px;'
        f'margin:3px 0;border-radius:4px;font-size:11px;">⚠️ {o["name"]} — '
        f'State stake: {o["total_state_pct"]}% — '
        f'SOE FLAG: {"YES 🚨" if o["soe_flag"] else "Watch"}</div>'
        for o in ownership_data if o.get("state_owners"))
    kpi_cards = "".join(f"""
    <div style="background:#1e293b;padding:9px 16px;border-radius:8px;min-width:120px;text-align:center;">
      <div style="font-size:9px;color:#94a3b8;text-transform:uppercase;">{label}</div>
      <div style="font-size:22px;font-weight:700;color:{color};">{value}</div>
    </div>""" for label, value, color in [
        ("Portfolio Risk",    f"{score}/100",      "#ef4444" if score >= 70 else "#f59e0b"),
        ("Risk Level",        level,               "#ef4444" if level == "CRITICAL" else "#f59e0b"),
        ("Suppliers",         len(suppliers),      "#60a5fa"),
        ("Critical Alerts",   len(analysis.get("critical_alerts", [])), "#ef4444"),
        ("SOE Flags",         len(soe_flagged),    "#a78bfa"),
        ("Alternates Found",  len(alternates),     "#22c55e"),
        ("Ownership Depth",   f"≥{OWNERSHIP_DEPTH_PCT}%", "#f59e0b"),
        ("LLM",               "HuggingFace",       "#818cf8"),
    ])
    display(HTML(f"""
    <div style="font-family:Inter,sans-serif;padding:14px;background:#0f172a;color:white;border-radius:10px;margin:10px 0;">
      <h2 style="margin:0 0 10px;font-size:15px;">🛡️ {AGENT_TITLE}
        &nbsp;<span style="font-size:11px;color:#64748b;">Crisis: {crisis_countries}</span></h2>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px;">{kpi_cards}</div>
      <p style="font-size:11px;color:#cbd5e1;margin:6px 0 10px;">{analysis.get("executive_summary", "")}</p>
      <div style="display:flex;gap:10px;flex-wrap:wrap;">
        <div style="flex:1;min-width:240px;background:#1e293b;padding:10px;border-radius:8px;">
          <div style="color:#f87171;font-size:10px;font-weight:700;margin-bottom:4px;">🔴 CRITICAL ALERTS</div>
          {alerts_html or '<div style="font-size:11px;color:#94a3b8;">None triggered</div>'}
        </div>
        <div style="flex:1;min-width:240px;background:#1e293b;padding:10px;border-radius:8px;">
          <div style="color:#4ade80;font-size:10px;font-weight:700;margin-bottom:4px;">✅ IMMEDIATE ACTIONS</div>
          <ul style="margin:0;padding-left:14px;">{actions_html}</ul>
        </div>
        <div style="flex:1;min-width:240px;background:#1e293b;padding:10px;border-radius:8px;">
          <div style="color:#c084fc;font-size:10px;font-weight:700;margin-bottom:4px;">🏛️ OWNERSHIP FLAGS (≥{OWNERSHIP_DEPTH_PCT}%)</div>
          {soe_html or '<div style="font-size:11px;color:#94a3b8;">No state-linked owners above threshold</div>'}
        </div>
      </div>
    </div>
    """))
    return fig


# ── CELL 11: Dynamic Country-Crisis Filter ────────────────────
raw_countries = set()

for edge in NEO4J_GRAPH:
    for key in ["t1_country", "t2_country"]:
        val = edge.get(key)
        if val and str(val).strip().lower() not in ("unknown", "nan", ""):
            raw_countries.add(str(val).strip())

for entries in OWNERSHIP_REGISTRY.values():
    for entry in entries:
        val = entry.get("country")
        if val and str(val).strip().lower() not in ("unknown", "nan", ""):
            raw_countries.add(str(val).strip())

available_countries = sorted(raw_countries)

print("\n🌍 Countries found in your data:")
if not available_countries:
    print("  ⚠️ No country columns detected — enter a country name manually below.")
else:
    for idx, ctry in enumerate(available_countries, 1):
        print(f"  [{idx}] {ctry}")
print("──────────────────────────────────────────────────")

selection = input("\nEnter country name or number to set as Crisis Zone: ").strip()
if selection.isdigit() and 1 <= int(selection) <= len(available_countries):
    CRISIS_COUNTRY = available_countries[int(selection) - 1]
else:
    matched = [c for c in available_countries if c.lower() == selection.lower()]
    CRISIS_COUNTRY = matched[0] if matched else selection

print(f"\n🚨 Crisis country set to: {CRISIS_COUNTRY}")


# ── CELL 12: Deterministic baseline agent ─────────────────────
def run_baseline_country_agent(crisis_country: str) -> tuple:
    """
    Rule-based fallback: extract impacted suppliers directly from the graph + ownership,
    then score them deterministically. Used as the base; LLM refines if available.
    """
    impacted: dict = {}
    target_lower = crisis_country.lower()

    for edge in NEO4J_GRAPH:
        t1_name = edge.get("tier1")
        t2_name = edge.get("tier2")
        t1_ctry = str(edge.get("t1_country", "")).lower()
        t2_ctry = str(edge.get("t2_country", "")).lower()

        if t1_name and target_lower in t1_ctry:
            impacted[t1_name] = {
                "name": t1_name, "country": edge.get("t1_country"),
                "component": edge.get("component", "Critical Components"),
                "vehicle":   edge.get("vehicle", "Defense Systems"),
                "risk_score": 95,
                "risk_reason": f"Tier 1 supplier directly in active crisis zone ({edge.get('t1_country')}).",
                "is_sole_source": True, "tier": 1,
            }

        if t2_name and target_lower in t2_ctry and t2_name not in impacted:
            impacted[t2_name] = {
                "name": t2_name, "country": edge.get("t2_country"),
                "component": edge.get("component", "Sub-assemblies / Materials"),
                "vehicle":   edge.get("vehicle", "Defense Systems"),
                "risk_score": 85,
                "risk_reason": f"Upstream Tier 2 bottleneck in crisis country ({edge.get('t2_country')}).",
                "is_sole_source": False, "tier": 2,
            }

    # Cross-reference ownership: flag suppliers owned from crisis country
    for supplier_name, entries in OWNERSHIP_REGISTRY.items():
        if supplier_name in impacted:
            continue
        for entry in entries:
            owner_ctry = str(entry.get("country", "")).lower()
            if target_lower in owner_ctry:
                impacted[supplier_name] = {
                    "name": supplier_name, "country": entry.get("country"),
                    "component": "System Subcomponents", "vehicle": "Defense Systems",
                    "risk_score": 70,
                    "risk_reason": f"Ownership ties to {entry.get('country')} flagged.",
                    "is_sole_source": False, "tier": 1,
                }
                break

    supplier_list = list(impacted.values())
    portfolio_score = min(100, len(supplier_list) * 25) if supplier_list else 0
    risk_level = (
        "CRITICAL" if portfolio_score >= 70
        else "HIGH"   if portfolio_score >= 50
        else "MEDIUM" if portfolio_score > 0
        else "LOW"
    )

    baseline_analysis = {
        "scenario_summary": f"Geopolitical risk evaluation for dependencies in {crisis_country}.",
        "crisis_countries": [crisis_country],
        "overall_risk_level": risk_level,
        "portfolio_risk_score": portfolio_score,
        "executive_summary": (
            f"Identified {len(supplier_list)} defense nodes tied to operational "
            f"vulnerabilities within {crisis_country}."
        ),
        "suppliers": supplier_list,
        "critical_alerts": [f"Vulnerability warning for {s['name']}." for s in supplier_list],
        "immediate_actions": [
            "Engage domestic ordnance alternatives.",
            "Check safety buffer inventory allocations.",
            "Initiate dual-sourcing assessment for critical components.",
        ],
        "alternate_suppliers": [
            {
                "replaces": s["name"], "name": "Domestic Alternative (India)",
                "country": "India", "readiness_score": 75, "lead_time_weeks": 6,
                "cost_premium_pct": 12,
                "reason": "Geographically secure substitute with existing capacity.",
            }
            for s in supplier_list
        ],
        "signals_detected": len(supplier_list),
    }
    ownership = run_ownership_analysis(supplier_list, OWNERSHIP_REGISTRY, OWNERSHIP_DEPTH_PCT)
    return baseline_analysis, ownership


# ── CELL 13: Run pipeline ─────────────────────────────────────
def run_agent(scenario: str, llm_fn=None):
    """
    Full pipeline:
      1. Run deterministic baseline for guaranteed output.
      2. Ask LLM to refine/enrich analysis (graceful fallback to baseline if LLM fails).
      3. Merge results: use LLM suppliers if valid, else baseline.
      4. Run ownership analysis.
      5. Render Plotly dashboard.
    """
    if llm_fn is None:
        llm_fn = LLM_FN

    print("=" * 70)
    print(f"  🇮🇳 {AGENT_TITLE.upper()}")
    print(f"  LLM Backend    : HuggingFace ({HF_MODEL_ID})")
    print(f"  Ownership Depth: ≥{OWNERSHIP_DEPTH_PCT}%")
    print(f"  Graph edges    : {len(NEO4J_GRAPH)}   |   Suppliers: {len(SUPPLIER_ROLLUP)}")
    print(f"  Scenario       : {scenario[:70]}...")
    print("=" * 70)

    print("\n⚙️  Step 1/3 — Deterministic baseline scoring...")
    baseline_analysis, _ = run_baseline_country_agent(crisis_country=scenario.split()[0])

    print("\n🤖 Step 2/3 — LLM enrichment (HuggingFace)...")
    llm_analysis = analyze_scenario(llm_fn, scenario, NEO4J_GRAPH, SUPPLIER_ROLLUP)

    # Merge: prefer LLM output when it produces a valid supplier list
    if llm_analysis.get("suppliers"):
        analysis = llm_analysis
        print(f"  ↳ Using LLM analysis ({len(analysis['suppliers'])} suppliers scored)")
    else:
        analysis = baseline_analysis
        print("  ↳ LLM fallback — using deterministic baseline")

    print(f"\n🏛️  Step 3/3 — Ownership analysis (≥{OWNERSHIP_DEPTH_PCT}%)...")
    ownership_data = run_ownership_analysis(analysis.get("suppliers", []), OWNERSHIP_REGISTRY, OWNERSHIP_DEPTH_PCT)
    print(f"  ↳ SOE flags: {sum(1 for o in ownership_data if o.get('soe_flag'))}")
    print(f"  ↳ State-linked owners: {sum(len(o.get('state_owners', [])) for o in ownership_data)}")

    print("\n📊 Rendering interactive Plotly dashboard...")
    render_dashboard(analysis, ownership_data)
    print("\n✅ Agent run complete.")
    return analysis, ownership_data


# ── CELL 14: Entry point ──────────────────────────────────────
# Build the scenario string from the selected country, then run
SCENARIO = f"{CRISIS_COUNTRY} supply disruption — geopolitical crisis affecting Indian Army supply chain"

analysis, ownership_data = run_agent(SCENARIO)
