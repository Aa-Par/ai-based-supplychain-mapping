// ============================================================
// SUPPLY CHAIN KNOWLEDGE GRAPH — Cypher build script
// Schema: Product, Component, Supplier, Person, Country
// Relationships: CONTAINS, SUPPLIED_BY, OWNED_BY, LOCATED_IN
// ============================================================

// ------------------------------------------------------------
// 1. CONSTRAINTS (uniqueness — also creates backing indexes)
// ------------------------------------------------------------
CREATE CONSTRAINT product_name   IF NOT EXISTS FOR (n:Product)   REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT component_name IF NOT EXISTS FOR (n:Component) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT supplier_name  IF NOT EXISTS FOR (n:Supplier)  REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT person_name    IF NOT EXISTS FOR (n:Person)    REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT country_name   IF NOT EXISTS FOR (n:Country)   REQUIRE n.name IS UNIQUE;

// ------------------------------------------------------------
// 2. COUNTRIES + risk_score (extends the minimal schema slightly,
//    matching the project's note that properties may grow over time)
// ------------------------------------------------------------
UNWIND [
  {name:'Russia',risk_score:55},{name:'China',risk_score:45},{name:'North Korea',risk_score:60},
  {name:'Iran',risk_score:50},{name:'Syria',risk_score:58},{name:'Myanmar',risk_score:48},
  {name:'France',risk_score:28},{name:'Germany',risk_score:8},{name:'UK',risk_score:7},
  {name:'Israel',risk_score:20},{name:'Pakistan',risk_score:35},{name:'Afghanistan',risk_score:55},
  {name:'Ukraine',risk_score:52},{name:'Belarus',risk_score:42},{name:'Venezuela',risk_score:38},
  {name:'Sudan',risk_score:45},{name:'Libya',risk_score:50},{name:'Yemen',risk_score:55},
  {name:'South Africa',risk_score:14},{name:'Austria',risk_score:10},{name:'Spain',risk_score:9},
  {name:'Singapore',risk_score:5},{name:'India',risk_score:6},{name:'USA',risk_score:4},
  {name:'Canada',risk_score:4},{name:'Australia',risk_score:4},{name:'Japan',risk_score:7},
  {name:'South Korea',risk_score:9},{name:'Taiwan',risk_score:25},{name:'Poland',risk_score:12},
  {name:'Romania',risk_score:12},{name:'Bulgaria',risk_score:13},{name:'Belgium',risk_score:9},
  {name:'Sweden',risk_score:6},{name:'Norway',risk_score:5}
] AS row
MERGE (c:Country {name: row.name})
  ON CREATE SET c.risk_score = row.risk_score
  ON MATCH  SET c.risk_score = row.risk_score;

// ------------------------------------------------------------
// 3. PRODUCTS, COMPONENTS, TIER-1 / TIER-2 SUPPLIERS
//    Multi-tier logic:
//      Product  -[:CONTAINS]->     Component        (vehicle has a part)
//      Component-[:SUPPLIED_BY]->  Tier-2 Supplier   (who actually makes the part)
//      Product  -[:SUPPLIED_BY]->  Tier-1 Supplier   (prime contractor / integrator)
//      Tier-1   -[:SUPPLIED_BY]->  Tier-2 Supplier   (prime sources the part from tier-2,
//                                                      relationship tagged with which
//                                                      component it relates to)
// ------------------------------------------------------------
UNWIND [
  {vehicle:'Plasan SandCat', component:'Engine',      tier2:'Ford Motor Co.',         t2_country:'USA',           tier1:'Plasan',           t1_country:'Israel'},
  {vehicle:'Plasan SandCat', component:'Tyres',       tier2:'Rodgard',                t2_country:'Israel',        tier1:'Plasan',           t1_country:'Israel'},
  {vehicle:'Mbombe 4',       component:'Engine',      tier2:'Cummins',                t2_country:'USA',           tier1:'Paramount',        t1_country:'South Africa'},
  {vehicle:'Mbombe 4',       component:'Tyres',       tier2:'Paramount',              t2_country:'South Africa',  tier1:'Paramount',        t1_country:'South Africa'},
  {vehicle:'Bronco',         component:'Engine',      tier2:'Ford Motor Company',     t2_country:'USA',           tier1:'ST Engineering',   t1_country:'Singapore'},
  {vehicle:'Bronco',         component:'Tyres',       tier2:'Mickey Thompson',        t2_country:'USA',           tier1:'ST Engineering',   t1_country:'Singapore'},
  {vehicle:'Bronco',         component:'Turret',      tier2:'BFGoodrich',             t2_country:'USA',           tier1:'ST Engineering',   t1_country:'Singapore'},
  {vehicle:'Airawat VMIMS',  component:'Engine',      tier2:'Steyr Motors',           t2_country:'Austria',       tier1:'Mahindra Defense', t1_country:'India'},
  {vehicle:'Airawat VMIMS',  component:'Tyres',       tier2:'Michelin',               t2_country:'France',        tier1:'Mahindra Defense', t1_country:'India'},
  {vehicle:'Airawat VMIMS',  component:'Turret',      tier2:'Milanion NTGS',          t2_country:'Spain',         tier1:'Mahindra Defense', t1_country:'India'},
  {vehicle:'Sherpa Light',   component:'Engine',      tier2:'Renault Trucks',         t2_country:'France',        tier1:'ARQUUS',           t1_country:'France'},
  {vehicle:'Sherpa Light',   component:'Tyres',       tier2:'Michelin',               t2_country:'France',        tier1:'ARQUUS',           t1_country:'France'},
  {vehicle:'Sherpa Light',   component:'Integration', tier2:'ARQUUS',                 t2_country:'France',        tier1:'ARQUUS',           t1_country:'France'},
  {vehicle:'Lenco Bearcat',  component:'Engine',      tier2:'Ford Motor Company',     t2_country:'USA',           tier1:'Lenco',            t1_country:'USA'},
  {vehicle:'Lenco Bearcat',  component:'Tyres',       tier2:'Hutchinson',             t2_country:'France',        tier1:'Lenco',            t1_country:'USA'},
  {vehicle:'Lenco Bearcat',  component:'Turret',      tier2:'Military Systems Group', t2_country:'USA',           tier1:'Lenco',            t1_country:'USA'}
] AS row

MERGE (product:Product {name: row.vehicle})
  ON CREATE SET product.category = 'Armored Vehicle'

MERGE (component:Component {name: row.vehicle + ' - ' + row.component})
  ON CREATE SET component.function = row.component

MERGE (tier1:Supplier {name: row.tier1})
  ON CREATE SET tier1.industry = 'Prime Integrator'

MERGE (tier2:Supplier {name: row.tier2})
  ON CREATE SET tier2.industry = 'Component Manufacturer'

MERGE (c1:Country {name: row.t1_country})
MERGE (c2:Country {name: row.t2_country})

MERGE (product)-[:CONTAINS]->(component)
MERGE (component)-[:SUPPLIED_BY]->(tier2)
MERGE (product)-[:SUPPLIED_BY]->(tier1)
MERGE (tier1)-[r:SUPPLIED_BY {component: row.component}]->(tier2)
MERGE (tier1)-[:LOCATED_IN]->(c1)
MERGE (tier2)-[:LOCATED_IN]->(c2);

// ------------------------------------------------------------
// 4. OWNERSHIP REGISTRY (OWNED_BY, 1%+ stakes)
//    Owner entities are modeled as Supplier nodes (companies, funds,
//    sovereign wealth funds, government bodies) EXCEPT for individual
//    / family ownership, which is modeled as Person, per the
//    Product/Component/Supplier/Person/Country schema.
// ------------------------------------------------------------

// 4a. Corporate / institutional / government owners -> Supplier nodes
UNWIND [
  {supplier:'ARQUUS',         owner:'John Cockerill Group',     owner_type:'Industrial Conglomerate',   country:'Belgium',      stake_pct:100,  note:'Parent — Walloon govt partial stake'},
  {supplier:'ARQUUS',         owner:'Région Wallonne',          owner_type:'Government',                country:'Belgium',      stake_pct:5.2,  note:'Indirect via John Cockerill'},
  {supplier:'ST Engineering',  owner:'Temasek Holdings',          owner_type:'Sovereign Wealth Fund',     country:'Singapore',   stake_pct:50.3, note:'Majority — Singapore MoF controlled'},
  {supplier:'ST Engineering',  owner:'GIC Singapore',             owner_type:'Government Investment',     country:'Singapore',   stake_pct:4.1,  note:'Board observer'},
  {supplier:'Hutchinson',      owner:'TotalEnergies SE',          owner_type:'Public Co/State-Influenced',country:'France',      stake_pct:100,  note:'Full subsidiary'},
  {supplier:'Hutchinson',      owner:'Bpifrance (French Govt)',   owner_type:'Government',                country:'France',      stake_pct:1.8,  note:'Indirect via TotalEnergies'},
  {supplier:'Renault Trucks',  owner:'Volvo Group AB',            owner_type:'Public Listed',             country:'Sweden',      stake_pct:100,  note:'Full subsidiary — no state link'},
  {supplier:'Michelin',        owner:'Groupe Michelin SACA',      owner_type:'Public Listed',             country:'France',      stake_pct:100,  note:'Self-governed'},
  {supplier:'Michelin',        owner:'Norges Bank Inv Mgmt',      owner_type:'Government Pension Fund',   country:'Norway',      stake_pct:1.4,  note:'Passive sovereign investor'},
  {supplier:'Mahindra Defense', owner:'Mahindra & Mahindra',      owner_type:'Public Listed Indian',      country:'India',       stake_pct:100,  note:'Parent — no state stake'},
  {supplier:'Mahindra Defense', owner:'LIC of India',             owner_type:'Government Insurer',        country:'India',       stake_pct:2.1,  note:'Passive — Indian state-owned insurer'},
  {supplier:'Steyr Motors',    owner:'Rheinmetall AG',            owner_type:'Public Listed Defense',     country:'Germany',     stake_pct:100,  note:'Acquired 2021'},
  {supplier:'Cummins',         owner:'Vanguard Group',            owner_type:'Institutional',             country:'USA',         stake_pct:9.1,  note:'Passive'},
  {supplier:'Cummins',         owner:'BlackRock Inc.',            owner_type:'Institutional',             country:'USA',         stake_pct:7.3,  note:'Passive'},
  {supplier:'Ford Motor Co.',  owner:'Vanguard Group',            owner_type:'Institutional',             country:'USA',         stake_pct:8.2,  note:'Passive'},
  {supplier:'Plasan',          owner:'Plasan Group (Private)',    owner_type:'Private Israeli',           country:'Israel',      stake_pct:100,  note:'Family-owned'},
  {supplier:'Paramount',       owner:'Paramount Group (Pvt)',     owner_type:'Private',                   country:'South Africa',stake_pct:100,  note:'Founder-controlled'},
  {supplier:'Lenco',           owner:'Lenco Industries (Pvt)',    owner_type:'Private',                   country:'USA',         stake_pct:100,  note:'Founder-owned'}
] AS row
MERGE (s:Supplier {name: row.supplier})
MERGE (owner:Supplier {name: row.owner})
  ON CREATE SET owner.industry = row.owner_type
MERGE (oc:Country {name: row.country})
MERGE (owner)-[:LOCATED_IN]->(oc)
MERGE (s)-[ob:OWNED_BY {owner_type: row.owner_type}]->(owner)
  SET ob.stake_pct = row.stake_pct,
      ob.note = row.note;

// 4b. Individual / family owners -> Person nodes
UNWIND [
  {supplier:'Ford Motor Co.', owner:'Ford Family (Class B)', country:'USA', stake_pct:40.0, role:'Special voting rights — founding family'}
] AS row
MERGE (s:Supplier {name: row.supplier})
MERGE (p:Person {name: row.owner})
  ON CREATE SET p.role = row.role
MERGE (pc:Country {name: row.country})
MERGE (p)-[:LOCATED_IN]->(pc)
MERGE (s)-[ob:OWNED_BY {owner_type:'Family/Founder'}]->(p)
  SET ob.stake_pct = row.stake_pct,
      ob.note = row.role;

// ============================================================
// 5. EXAMPLE ANALYTICAL QUERIES (validate the loaded graph)
// ============================================================

// 5a. Full multi-tier trace for one vehicle
// MATCH (p:Product {name:'Airawat VMIMS'})-[:CONTAINS]->(comp:Component)-[:SUPPLIED_BY]->(t2:Supplier)
// MATCH (p)-[:SUPPLIED_BY]->(t1:Supplier)
// MATCH (t2)-[:LOCATED_IN]->(t2c:Country)
// RETURN p.name, t1.name, comp.function, t2.name, t2c.name;

// 5b. Any supplier with state-linked ownership >= 1% (SOE / government / SWF)
// MATCH (s:Supplier)-[r:OWNED_BY]->(owner)
// WHERE r.owner_type IN ['Government','Sovereign Wealth Fund','Government Investment','Government Pension Fund','Government Insurer']
//   AND r.stake_pct >= 1
// RETURN s.name AS supplier, owner.name AS owner, r.owner_type, r.stake_pct
// ORDER BY r.stake_pct DESC;

// 5c. Total state-linked ownership % per supplier (cumulative exposure)
// MATCH (s:Supplier)-[r:OWNED_BY]->(owner)
// WHERE r.owner_type CONTAINS 'Government' OR r.owner_type CONTAINS 'Sovereign'
// RETURN s.name AS supplier, sum(r.stake_pct) AS total_state_linked_pct
// ORDER BY total_state_linked_pct DESC;

// 5d. Country risk exposure for a given vehicle (every country touched by its supply chain)
// MATCH (p:Product {name:'Bronco'})-[:CONTAINS]->(:Component)-[:SUPPLIED_BY]->(s:Supplier)-[:LOCATED_IN]->(c:Country)
// RETURN DISTINCT c.name, c.risk_score ORDER BY c.risk_score DESC;

// 5e. Single points of failure: components supplied by only one Tier-2 across the whole portfolio
// MATCH (comp:Component)-[:SUPPLIED_BY]->(s:Supplier)
// WITH comp.function AS componentType, collect(DISTINCT s.name) AS suppliers
// WHERE size(suppliers) = 1
// RETURN componentType, suppliers;

// 5f. Suppliers ultimately rooted in a high base-risk country (>=40) via LOCATED_IN
// MATCH (s:Supplier)-[:LOCATED_IN]->(c:Country)
// WHERE c.risk_score >= 40
// RETURN s.name, c.name, c.risk_score ORDER BY c.risk_score DESC;
