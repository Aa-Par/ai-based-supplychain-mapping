# Supply Chain Risk Monitor 

## Goal
Monitor supplier news, financial distress, geopolitical events, ownership structures (to 1% holdings including SOEs and Board of Directors), and port/logistics disruptions. Generate per-supplier risk scores, flag state-controlled suppliers, recommend alternate suppliers for crisis resilience, and deliver a weekly digest report.

## Inputs
- supplier_list (textarea, optional): Newline-delimited supplier list — "Name | Country | Category | Criticality". If blank, run a general sector/region scan.
- industry_sector (select, required): Primary sector (manufacturing, automotive, electronics, aerospace, pharma, energy, food).
- geographic_focus (multiselect, required): Regions to monitor.
- risk_threshold (select, required): Minimum risk level for alerts (critical/high/medium/all).
- ownership_depth (select, required): Minimum stake to include in ownership analysis (one_percent/five_percent/ten_percent/twenty_five_percent).
- alternate_supplier_count (integer, optional, default 3): Number of alternate suppliers to suggest per at-risk supplier.
- email_recipients (string, optional): Comma-separated emails for digest delivery via Gmail.
- report_period (select, optional): weekly/biweekly/monthly/adhoc.

## Procedure

### Step 1 — Check Connector Status
1. Attempt a test call to Gmail connector (listLabels). If it fails, note in the report that email delivery is unavailable and continue.
2. Attempt a test call to Google Sheets connector. If it fails, note that tracking log is unavailable and continue.
3. Do NOT stop if connectors are missing — proceed with intelligence gathering and note limitations in the output.

### Step 2 — Parse Supplier Portfolio
1. If supplier_list is provided, parse each line into: name, country, category, criticality.
2. If blank, construct a representative list based on industry_sector and geographic_focus inputs.
3. Build a working list of suppliers with fields: name, country, category, criticality, risk_score (initialize to 0).

### Step 3 — Scan Risk Signals (run ALL searches in parallel)
Run the following web_search queries simultaneously:
- "[industry_sector] supply chain disruptions geopolitical risks [current year]"
- "port disruptions shipping delays [geographic_focus regions] [current year]"
- "[industry_sector] supplier financial distress bankruptcies [current year]"
- "rare earth export restrictions sanctions [geographic_focus regions] [current year]"
- "tariffs trade war [geographic_focus regions] [current year]"
- "cyber attacks logistics supply chain [current year]"
Synthesize results into a structured list of risk signals with: type, severity (Critical/High/Medium/Low), affected_regions, affected_sectors, source, date.

### Step 4 — Ownership & Control Analysis
For each supplier in the portfolio:
1. Search: "[supplier name] ownership shareholders state owned enterprise board of directors"
2. Search: "[supplier name] annual report major shareholders SEC filing"
3. Identify all owners holding >= the ownership_depth threshold.
4. Flag owners as: SOE (State-Owned Enterprise), Government Investment Vehicle, Government Pension Fund, Private Institutional, Private Individual, or Unknown.
5. Note Board of Directors members and their nationalities/affiliations.
6. Calculate: total_state_linked_pct = sum of all state-connected ownership stakes.
7. Flag supplier as HIGH RISK if: any single SOE stake > 25%, or total_state_linked_pct > 40%, or board has majority from a high-risk jurisdiction.

### Step 5 — Score Each Supplier
Calculate risk_score (0-100) for each supplier using:
- Country risk (0-30 pts): based on geopolitical signals, sanctions, conflict proximity
- Financial health (0-20 pts): based on bankruptcy signals, credit distress news
- Dependency risk (0-20 pts): is this a single-source supplier? Critical category?
- Ownership risk (0-20 pts): SOE control level, high-risk jurisdiction stakes
- Logistics risk (0-10 pts): port disruptions, shipping lane issues for supplier country
Assign overall portfolio risk score = weighted average of supplier scores (weighted by criticality).

### Step 6 — Alternate Supplier Research
For each supplier with risk_score >= 70:
1. Identify the functional role of the component/service supplied.
2. Search: "alternate suppliers [component function] outside [supplier country] [current year]"
3. Search: "who makes [component name] [crisis-resilient countries like USA, Germany, Japan, Australia, Canada]"
4. For each alternate found, assess: country risk, capacity, lead time to switch, crisis readiness.
5. Return top alternate_supplier_count alternates ranked by crisis readiness score.

### Step 7 — Neo4j Graph Guidance
Include in the report a section titled "Neo4j Knowledge Graph Architecture" with:

NODE TYPES:
- Supplier {name, country, category, criticality, risk_score, is_single_source}
- Component {name, function, category, strategic_importance}
- Owner {name, type, country_of_origin, ownership_pct}
- Country {name, risk_level, sanction_status, trade_regime}
- BoardMember {name, nationality, other_affiliations}
- StateOwnedEnterprise {name, country, controlling_ministry, govt_ownership_pct}
- AlternateSupplier {name, country, category, crisis_readiness_score, lead_time_weeks}
- RiskEvent {type, severity, date, description, source}
- LogisticsHub {name, country, type, annual_throughput_teu}
- TradeRoute {origin, destination, risk_level, typical_transit_days}

RELATIONSHIP TYPES:
- (Supplier)-[:SUPPLIES {since_year, contract_value_usd, exclusivity}]->(Component)
- (Owner)-[:OWNS {pct, since_year, voting_rights}]->(Supplier)
- (BoardMember)-[:SITS_ON_BOARD {role, since_year, nationality}]->(Supplier)
- (StateOwnedEnterprise)-[:CONTROLS {pct, mechanism}]->(Supplier)
- (StateOwnedEnterprise)-[:OWNED_BY {pct}]->(Country)
- (Supplier)-[:LOCATED_IN]->(Country)
- (Country)-[:HAS_SANCTION]->(Country)
- (Country)-[:HAS_TRADE_AGREEMENT {agreement_name, signed_year}]->(Country)
- (RiskEvent)-[:DISRUPTS]->(Country)
- (RiskEvent)-[:AFFECTS]->(Supplier)
- (RiskEvent)-[:IMPACTS]->(TradeRoute)
- (AlternateSupplier)-[:CAN_REPLACE {confidence_pct, switch_lead_weeks, cost_premium_pct}]->(Supplier)
- (AlternateSupplier)-[:SUPPLIES]->(Component)
- (Supplier)-[:SHIPS_VIA]->(LogisticsHub)
- (Supplier)-[:DEPENDS_ON {dependency_type, criticality}]->(Supplier)
- (Component)-[:USED_IN]->(Component)

KEY CYPHER QUERIES TO BUILD:
1. Find all suppliers with any state ownership >= 1%:
   MATCH (o:Owner)-[r:OWNS]->(s:Supplier) WHERE o.type IN ["SOE","Government"] AND r.pct >= 1 RETURN s,o,r
2. Find crisis-safe alternate suppliers for a component, excluding high-risk countries:
   MATCH (a:AlternateSupplier)-[:SUPPLIES]->(c:Component)<-[:SUPPLIES]-(s:Supplier)
   MATCH (a)-[:LOCATED_IN]->(ac:Country) WHERE ac.risk_level = "LOW"
   RETURN a, c, s ORDER BY a.crisis_readiness_score DESC
3. Detect cascading risk from a geopolitical event:
   MATCH (e:RiskEvent)-[:DISRUPTS]->(c:Country)<-[:LOCATED_IN]-(s:Supplier)-[:SUPPLIES]->(comp:Component)
   RETURN e, c, s, comp
4. Find board members with dual affiliations to state entities:
   MATCH (b:BoardMember)-[:SITS_ON_BOARD]->(s:Supplier)
   WHERE b.other_affiliations CONTAINS "government" OR b.other_affiliations CONTAINS "ministry"
   RETURN b, s

AI MODEL TRAINING GUIDANCE (Ownership Detection to 1%):
To train a model that identifies beneficial ownership chains down to 1% stakes:
1. DATA SOURCES: SEC EDGAR (13F, 13G, 13D filings), Companies House (UK), Bundesanzeiger (Germany), OpenCorporates, FactSet, Bloomberg ownership data, annual reports, proxy statements.
2. ENTITY TYPES TO EXTRACT: Direct shareholders, beneficial owners, nominee holders, trust beneficiaries, fund managers (look through fund to ultimate beneficial owner), government ministries, sovereign wealth funds, state pension funds.
3. NER MODEL: Fine-tune a BERT/RoBERTa model on ownership disclosure documents. Training labels: OWNER_ENTITY, OWNERSHIP_PCT, ENTITY_TYPE (SOE/Private/Govt), COUNTRY_OF_ORIGIN, BOARD_ROLE.
4. GRAPH COMPLETION: Use link prediction on the Neo4j graph to infer likely ownership chains where direct disclosure is opaque (shell company chains, nominee structures).
5. SOE DETECTION RULES: Flag as SOE if: (a) government entity owns >50%, (b) name matches known SOE registry (GlobalSOETracker, OECD SOE database), (c) board has majority from single government ministry.
6. CRISIS SCENARIO SCORING: During war/sanctions, re-weight alternate supplier scores: penalize suppliers in allied-with-adversary countries, boost suppliers in NATO/Five Eyes/allied nations, factor in port access and airspace restrictions.

### Step 8 — Compose Report & Dashboard
1. Call render_dashboard tool to get schema.
2. Build creaoUI dashboard with:
   - Alert banner (overall risk level)
   - 4 KPI cards: Portfolio Risk Score, Suppliers Monitored, Critical Alerts, State-Linked Flags
   - Bar chart: Risk scores by category (current vs prior week if prior data available)
   - Supplier risk table (all suppliers, sorted by risk score descending)
   - Ownership analysis table (flagged suppliers with owner breakdown)
   - Alternate supplier recommendations table
   - Neo4j status card (node/relationship counts if graph is connected)
3. Wrap full markdown report in creaoArtifact tags (type="text/markdown").

### Step 9 — Deliver & Log
1. If Gmail connected and email_recipients provided: send digest email with report summary.
2. If Google Sheets connected: append a row to the tracking sheet with: date, overall_risk_score, critical_alerts, top_risk_signal, suppliers_monitored.
3. Call record_session with: process_name, frequency, scope, overall_risk_score, critical_alerts, suppliers_monitored, state_linked_flags, signals_detected.

## Output
A visual creaoUI dashboard + downloadable Markdown weekly digest report containing: overall risk score, per-supplier risk scores, top 5–10 risk signals, ownership analysis with SOE/state flags, alternate supplier recommendations for at-risk suppliers, Neo4j architecture guide, and mitigation action plan.
