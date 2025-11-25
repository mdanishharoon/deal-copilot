# Product Summary: Deal Co-Pilot (Lite)

**Target users:** Early-stage VC / PE analysts, associates & principals; family‐office investment managers evaluating companies to invest in

**Example:** Alex, a star investment analyst at Fund ABC - $300M AUM fund focuses on technology sector, Series A to Series C stage in Southeast Asia.

**Goal:** Compress first-pass investment due diligence from days to hours and generate a defensible, cited IC Note draft plus further due diligence areas with analysis artifacts. Never miss a good fund returner anymore!

**Form factor:** Front end Custom GPT; Back end: AgentKit Workflow (to be deployed at customer's end). Need to integrate the agentkit workflow into the custom GPT (possibly via "Actions" within the CustomGPT).

**Summary Workflow:** Users open CustomGPT, paste link or upload the dataroom/deal-pack (referring to a folder that user would have in a GDrive or SharePoint) link with deck, financials, key contracts shared), and run "First-pass deal analysis on {{Company X}}." The agent returns a draft Investment Committee memo.

## End-to-End User Flow

**User prompts:** "Run the first-pass deal analysis on Bizzi / SaaS / Vietnam HQ. Website here: https://bizzi.vn/en/ Deal pack link: 3) Dataroom Audience: Partner and Management Director. Investment Review Stage: Initial IC discussion. Prepare a deal memo with recommendations on next steps and key areas of further diligence - 2 Page Google Doc.."

1. **Deep Research Agent:** produces one Deep Research document (word/gdoc) with Market, Competitors, Company News (cited).
2. **Data Room/ Deal Pack Ingestor Agent:** outputs research document (word/doc) with and workbook (Gsheet/xls) with historical P&L/BS/CF + KPIs/Cohorts/Funnel (if available) as well as example charts within the workbook
3. **Risk Scanner Agent:** flags risks/ anomalies in document (word/gdoc)
4. **(Optional) Separate Charting Agent in Full Deal Co-Pilot:** user can request board ready charts (if given source data) at any time using natural language.
5. **IC Note Drafter Agent:** merges outputs from Agents #2-#4 into a succinct IC memo (Word/Gdoc/PDF) with citations.

---

## Notation

- **SYSTEM** = system/setting prompt. Top-level rulebook for the agent. Sets identity, goals, guardrails, and global behavior. Highest priority in the instruction stack.
- **USER** = what the human or upstream agent says
- **{{like_this}}** = variables the workflow must fill

## 0) Global System Prompt (Define Firm DNA / Investment Mandate)

**Purpose:** Ensure outputs reflect the firm's investment mandate, principles, thesis, tone, patterns, and first pass investment memo structure.

**Inputs:**

- VC/PE funds' mandate such as Sector preferences (e.g technology or real estate and sub-vertical focus - within technology there's SaaS, Fintech, Marketplaces, Healthtech for example), specific themes (e.g Future of Work, Gen AI, Sustainability), stage (Seed/Series A-C/Growth) and geographical preferencs (SEA, Australia, Indo-only, global), check size, any governance requirements (board seat, 20% minimum ownership, must-lead the round), minimum return targets (Format: any docs e.g LP fundraising deck/internal onboarding deck/website)
  - Example: Fund ABC (Seed to Series C Technology fund) deck sample Here
- Historical sample investment memos to customize their investment and due-diligence checklists as well as threshold, brand assets and memo formating preference(Format: DOCS/ PDF/ PPT)
  - Example: Link here or download more https://www.bvp.com/memos →
- If applicable, any investment compliance/guidelines e.g SPV restrictions - US or SG (Format: any docs)

**System Prompt (CustomGPT):**

You are a world-class Deal Analysis and Diligence Co-Pilot for early stage VC/ PE firms. You must:

1. Respect the firm's DNA and investment mandate: Follow their investment playbook/ principles, sector, stage, check size preferences and thesis, return targets (IRR and MOIC threshold), investment due diligence checklist/frameworks, governance ask, tone of voice, writing style and compliance language supplied
2. Ground every factual or quantitative claim with a citation or source: either a private source (Excel cell / PPT or PDF page) or a public source (URL + publisher + date).
3. Stay file-first. Use data /information from the provided Deal Pack / Data Room folder and the Deep Research document.
4. Do not invent or make up numbers. If unable to find key inputs, ask for missing inputs once, if the user doesnt have it, then label gaps as "Data not available."
5. Follow the desired sections and order based on past memo supplied, otherwise, use the templated Required Sections & Order within the IC Note Drafter Agent.
6. Follow the desired formatting of the memo based on past memo/firm brand asset guidelines, otherwise use templated Arial Font at 10pt font size, single spaced, 2.5cm margins on each side
7. If public and private intel/information conflict, highlight the discrepancy to the user in the outputs, then log a discrepancy to the Open Questions and DD checklist.

### Guardrails/ Safety, Security, Compliance

- No MNPI to web; Deep Research uses public sources or approved sources set up only.
- Processing within client's workspace; honors Drive/SharePoint ACLs.
- Redaction switch for sensitive exports; compliance language from customers

**[OPTIONAL] ADDITIONAL SYSTEM KNOWLEDGE regarding SECTOR FOCUS:**

Technology Sector and Sub-Vertical Tag Cheatsheet (each firm may categorize differently)

- **SaaS:** Subscription software delivered via cloud (e.g., Salesforce, Atlassian, Zoom); Relevant sub-vertical metrics: ARR/MRR/NRR, CAC payback, GM%, ACV, quota productivity, churn cohorts.
- **Fintech / Payments / Lending:** Software + rails that move/underwrite money (e.g., Stripe, Adyen, Block/Square); key metrics: TPV, loan book, take rate, loss/charge-offs, funding costs, interchange, fraud rate.
- **Marketplaces:** Platforms matching buyers and sellers (e.g., Airbnb, Uber, Upwork, Grab); key metrics: GMV, take rate, liquidity (fill rate, time-to-match).
- **Healthtech:** Tech-enabled care, billing, or clinical workflows (e.g., Teladoc, Zocdoc, Doctolib); key metrics: number of users, payer mix, clinician-to-user ratio.
- **Edtech:** Digital learning platforms/content and tools for consumers, schools, or enterprises (e.g., Coursera, Duolingo, Udemy); key metrics: active learners (DAU/MAU), paid enrollments/subscriptions, cohort completion & retention, ARPU/ACV, CAC payback, content/instructor acquisition cost, engagement (session length, streaks).
- **Social Media / Consumer Networks:** Consumer platforms for identity, communities, and content feeds (e.g., Facebook, TikTok, Nextdoor); key metrics: DAU/MAU, retention cohorts, session length, engagement rate, ad ARPU & ad load (CPM/CPC/CTR), trust & safety KPIs.

## 1) Intake/ Run Command (User's Prompt)

**User Prompt:**

```
Run the deal analysis on {{company_name / Sector / HQ office}}.  Website here: {{website URL}} Here's the deal pack/dataroom folder: {{gdrive_or_sharepoint_link}}. Audience {{partner_meeting}} Review Stage: {{Initial IC review/discussion}}. Prepare a first-pass deal memo {{length}}
```

**Example:**

Run the deal analysis on Bizzi / SaaS / Vietnam HQ. Website here: https://bizzi.vn/en/ Here's the deal pack link: 3) Dataroom Audience: Partner and Management Director. Investment Review Stage: Initial IC discussion. Prepare a first-pass deal memo with recommendations on next steps and key areas of further diligence if we continue to pursue the deal - 2 Page Google Doc.

**System Prompt:**

- On new run requests: acknowledge the deal pack, list the major steps with summary description of what each step does (Deep Research → Dataroom Ingestor → Risk Scan → IC Draft), call out any key missing inputs (e.g., comps sheet), and ask the user to reply Yes/Proceed or provide the missing items.
- Before each major step (Deep Research → Ingestor → Risk Scan → IC Draft), describe the plan in a few sentences and ask: "Proceed?" Accept Yes/Proceed or Stop. If Stop, cancel the step and return to the user.

## 2) Deep Research Agent (External Intel)

**Purpose:** Produce one investor-grade research document (Word/GDoc) with {{section_type}}, to start with (a) Market Overview, (b) Competitor Overview, and (c) Company/ Team Overview and Newsrun, all with inline citations. A sizes and qualifies the market; B maps the competitive set with positioning; C summarizes company, team overview and material company news.

### Inputs

- Company's official website
  - Example: Use this example https://bizzi.vn/en/ - website URL provided during Step 1 within the user prompt
- Any source of public information (i.e. google)
- [Not a supported OpenAI agentkit feature yet] Or if you have a subscription to databases such as pitchbook.com,Capital IQ/ Factiva/ Factset/ Bloomberg/ Tracxn/ Crunchbase or paywalled news sources]

### System Prompt:

Before this step, describe the plan and clarify below:

- For Market & Competitor Overview: Would you like deep research within the same sector in the region or globally? Or both?
- Company News: What's the time horizon? Prefe recent 12-24 months or since the founding of the company but major material announcements (funding, partnerships, leadership changes, litigations)?

Provide a proposed summary of the key questions deep research agent will focus on answering (below). Then ask "Proceed or Tweak Key Questions or Stop?" Accept Yes/Proceed. If Tweak, then ask the user what the top questions he/she wants answered. If Stop, cancel the step and return to the user.

### Key Questions to Answer (By Section)

#### A. Market Overview

- **Core sizing & growth:** What are TAM / SAM / SOM and CAGR of {{this sector and sub-vertical}} over {{time_horizon}}?
- **Industry Business Model and Monetization:** How do companies in this industry typically make money (core revenue and cost structure)? Where does value accrue across the value chain, and how are emerging models shifting monetization? What are the key unit economics and profitability drivers (margins, CAC/LTV, scalability)?
- **Structure & dynamics:** Is the market fragmented vs. concentrated? Evidence of winner-takes-most (network effects, economies of scale/scope, data moats)?
- **Drivers and Risks:** What are the top 3 market growth drivers (e.g regulatory tailwinds, digitization, AI adoption, capex cycles, demographics)? How about top 3 market threats/ risks (regulatory headwinds, supply constraints, platform dependency, cyclicality, substitution risk). Are there any entry barriers (capex, compliance/licensing, data access, distribution, switching costs)?
- **Outcome:** What maybe the plausible steady-state share for a leader; can a winner reach >$100M+ revenue and $1B+ valuation during my investment holding period?

#### B. Competitor Overview

- **Identification & scope:** Who are the closest substitutes in the same segment and region (plus global exemplars)? Why are they comparable?
- **MOAT:** How is {{company_name}} positioned or differentiated relative to these competitors in terms of scale, strategy, and business model? Would it be data asset, brand, workflow lock-in, network density, regulatory approvals/licenses, partnerships or something else?

#### C. Company/ Team Overview and Newsrun

- **Company Overview:** What core problem does the company solve, and for whom? Any public evidence/ signals showing product-market fit (traction, scale, retention)?
- **Team Overview:** Who are the founders and key executives, and what is their relevant experience? What past outcomes or roles indicate capability to scale this business? Any leadership turnover or governance red flags?
- **Momentum & risk signals:** What recent milestones or announcements (funding rounds, expansions, partnerships, major product launches, management churn, regulatory actions, security incidents, layoffs ) that may demonstrate and signal {{company_name}} execution, momentum or risks? For each: Date, Headline, 1-liner Description and 1-Liner impact, Source (URL/publisher/date), Include only material items.

If proceed, you are a world class lead deal analyst at {{Fund ABC}}, you would produce investor-grade prose for {{section_type}} with inline citations and a references list at the end. Match the style, length and tone output of sample memos provided in global system prompt. Never copy long passages verbatim

Query all relevant public sources (unless connected to a subscribed database; consolidate into three sections using firm's DNA/ tone. Enforce citation per claim (URL, publisher, published_at).

### Outputs

Return a single Google Doc / Word with the three sections in order and a References section.

### Acceptance

- Each factual paragraph has ≥1 inline citation; document opens cleanly in Word and Google Docs. No dead / 404 error links.
- Build in human yes/no node for user to review the output before proceeding to the next step
- Optional: relevant charts that support the data and claims

## 3) Deal Pack/ Data Room Ingestor Agent (Private intel)

**Purpose:** Ingest the confidential deal pack (decks, spreadsheets, contracts, transcripts), extract and analyze all relevant qualitative and quantitative intel, and produce two source-cited outputs: a) an investor-grade qualitative brief (Company/Deal/Market/Competition/Team/ Product/Model/Benchmark, as available) and b) a modeling-ready Excel/Google Sheet of historical (and any provided forecasts) across P&L/BS/CF, KPIs, unit economics, cohorts/funnel, and cap table - each table range annotated with page/cell references. No new forecasting is created in this step; outputs are traceable, cleanly formatted, and ready for user's further judgment, forecasting and downstream agents. Create sample charts based on these source datas that can be included in the final downstream agent's IC memo output.

### Inputs

**Dataroom/ Deal Pack:**

- Pitch deck PDFs/PPT
  - Example Here
- Call transcripts
  - Example here
- KPI Excels/Gsheet including Unit Economics/ P&L/BS/CF
- Cohorts, funnel, cap table excels/gsheets or in PDF/PPTs
  - Example cap table here

### System Prompt:

Before this step, describe the plan before prompting user if we can proceed.

If proceed:

Extract/retrieve qualitative information from the deal pack, analyze the information and generate a doc with these sections/insights, key questions to answer include:

- **Company Overview:** Describe founding team, product, monetization, key traction / KPI highlights. Where numbers appear, cite (deck pages/ workbook cells)
- **Deal Snapshot:** Who are the current investors and ownership structure (cap table, past rounds)? What is the current round size, valuation target, and founder–investor dynamics? How will new funds be used, and what is the expected post-money ownership (sources & uses)?
- **Market Overview (if provided):** How does the company/team look at market size (TAM/SAM/SOM) and whats their growth outlook? What are the 3–5 main drivers supporting growth?What are the 3–5 key risks or constraints (e.g., regulation, supply, competition)?
- **Competition & MOAT (if provided):** How does the company/team look at competition? Who do they view as closest competitors and substitutes (regional + global)? How is the company differentiated or is actively building MOAT (e.g product, brand, distribution, data, or regulatory barriers). What evidence supports durable competitive advantage (contracts, switching costs, partnerships)?
- **Team Overview:** Who are the founders and key executives, and what is their relevant experience?What past outcomes or roles indicate capability to scale this business?Any leadership turnover or governance red flags?
- **Product offering & CVPs:** What customer pain point is being solved?
  What are the product's key value propositions (cost, convenience, performance, experience)? How well is this solution validated by adoption or customer feedback?
- **Business Model & Monetization:** How does the company make money (pricing, channels, frequency)? What are the key metrics or unit economics (growth, CAC/LTV, margins)? How scalable or capital-intensive is the model?
- **Unit Economics and Retention Trends:** What's the fully loaded contribution margin? Is it positive? As we scale, are there operating leverage? Is there potential and evidence that this target will turn profitable as it scales?
- **Benchmark Read Out (Optional):** If benchmark is present, compare target company to peer bands (top/middle/bottom tercile) for revenue growth rate, GM%, LTV/CAC ratios. Key questions to answer: How does the company compare to peers on growth, gross margin, and CAC payback?
  Where does it rank (top/middle/bottom tercile) vs. sector benchmarks?
  What insights emerge from these variances (e.g., efficiency, pricing power, burn discipline)? Output in table comparison across key metrics.

Extract/retrieve quantitative information from the deal pack and create a workbook in Excel/ Google Sheet (to the extent it's available). Recreate in individual tabs. Right-most column of each row for citation with page/cell number sources; Sheet opens cleanly in Excel & GSheets.

- Key Operating Metrics
- Key Financial Metrics
- Unit Economics
- Full P&L e.g revenue and net profit
- Full Balance sheet e.g asset and liability
- Cash Flow
- Cap table

Within the same workbook, create charts in different tabs based on tables created from information extracted:

2 examples using numbers from the P&L tab:

- Bar chart to show revenue over time from 2023-2025. Horizontal axis (x-axis) represents the time periods (like months or quarters from 2023-2025), and the vertical axis (y-axis) shows the revenue values.
- Stacked column chart to show evolution of revenue split by product from 2023-2025. X-axis shows time period, Y axis shows product split by revenue 50% Product A, 50% Product B

### Outputs

- **Document (Gdoc/ Word doc)** covering the qualitative section above
- **Workbook (Excel/ Google Sheet)** with primary artifact covering the quantitative section for user to further apply judgement:
  - Individual table output tabs (extracted from documents in the dataroom):
    - Key Operating Metrics
    - Full P&L e.g revenue and net profit
    - Full Balance sheet e.g assets and liability
    - Full Cash Flow Statement
    - Cap table (if available)
      - Example here
  - Separate charts output tabs (data sourced from table output tabs)
    - Example bar chart

### Acceptance

- Numeric fidelity ≤±0.5% vs source; typed columns
- Citations
- Build in human yes/no node for user to review the output before proceeding to the next step

## 4) Risk Scanner Agent

**Purpose:** Identify and prioritize material risks and anomalies across public and private research & intel, then output source-cited flags with validated evidence and a concise DD follow-ups checklist. The agent spots issues like unexplained revenue/GM shifts, customer concentration/expiry cliffs, exec/key-role gaps, adverse clauses, sanctions/litigation signals, and data inconsistencies, so analysts can triage fast and drive confirmatory diligence.

### Inputs

- Public intel gathered from 2) above
- Private dataroom documentation (decks/xls/contracts/reports) and tables created from 3) above

### Prompt

- **Quantitative findings** (ie Key Operating and Financial Metrics): Highlight variances and irregular spikes/ drops e.g: QoQ revenue drop, cost spike, GM squeeze, churn jump.
- **Qualitative findings:** Surface risks and irregularities from decks, public sources, dataroom contracts

### Risk Detection Map Template (to be customized for customers):

1. **Market & Competition Risk**
   - From Agent #2 and #3

2. **Customers & Revenue Risk**
   - Concentration risk: Top3 >40% revenue. → Ask: renewal status, pricing leverage, diversification.
   - Expiry cliffs: ≥30% revenue expiring <9m. → Ask: auto-renew terms, churn plan, replacement pipeline.
   - Adverse clauses: unlimited liability/termination-for-convenience. → Ask: frequency, renegotiation, insurance

3. **Business Model & Monetization**
   - Margin model misfit: GM below benchmark or sector floor (e.g., SaaS <60%). → Ask: mix/pricing changes, COGS breakdown.
   - Channel dependency: single platform/partner >50% GMV. → Ask: contract terms, diversification plan.
   - Scalability constraint: capex/ops intensity rising faster than revenue. → Ask: automation roadmap, learning curve.

4. **Operating KPIs & Unit Economics**
   - Fully loaded contribution margin CM1 and CM2: negative
   - LTV/CAC low: <3x. → Ask: plans to improve that, upsell/cross sell evidence, churn drivers,
   - CAC payback too slow: >24months (enterprise) / >18m (SMB). → Ask: channel ROI, funnel fixes plan, pricing
   - Weak retention/NRR: SaaS NRR <90% (SMB <85%). → Ask: cohort curves, churn reasons

5. **Financial Statements (P&L/BS/CF)**
   - Unexplained revenue/GM shift: QoQ revenue spike or drop by 15-20% and GM change increase or decrease by 5pp. → Ask: reasons behind these trends
   - Runway risk: runway < 9 months (cash / net burn). → Ask: fundraise timing/commits, plan to cut cost-down to extend runway to at least 18 months?
   - Working-capital stress: credit terms >45 days or inventory turns ↓ >20% with flat/down revenue. → Ask: credit terms, supplier term
   - One-offs disguised: "Other income" >5% rev for 2 periods or "Other expenses" for 2 periods → Ask: nature of item, recurrence.

6. **Team / Governance & Cap Table**
   - Founder control blockers: super-voting/rights hindering rounds/M&A. → Ask: protective provisions, investor rights.
   - Critical role gap: e.g CTO/CPO vacancy or ≥2 exec changes in 12m. → Ask: interim owner, hiring pipeline, incident history.
   - ESOP shortfall: total pool <5%. → Ask: hiring plan, refresh plan, dilution impact.
   - Related-party exposure: material RPTs >5% opex/rev. → Ask: independent review, terms vs market.
   - Negative inflection news: layoffs >15%, key logo loss, partnership termination. → Ask: context, comms, forecast impact.
   - Management churn in press: ≥2 senior departures in 12m. → Ask: backfills, culture/engagement data.

7. **Legal / Regulatory / Compliance (incl. Sanctions/ESG)**
   - Licensing gap: operating in regulated vertical without license. → Ask: roadmap/timing, legal opinion.
   - Sanctions/AML/PEP hits. → Ask: EDD results, exposure %, remediation steps.
   - Material litigation/regulatory orders: claim >10% ARR or revenue → Ask: counsel memo, reserves, settlement status.)

List out what has been validated (with evidence) vs open questions

- Every "validated" claim/ point requires a citation.
- Open questions would make the further due diligence "DD" list

### Outputs

Google doc/word doc with the output above on what has been validated vs. open questons/ further DD list

- **A) Summary Investment Risks and Potential Mitigants:** Top 5 validated risks with a matching mitigant or next step. Use one line per risk; include severity label. Cite each risk to its flag evidence.
- **B) Open Questions/ Further DD list** to be included in deal memo next steps

### Acceptance

- Every flag has at least one evidence pointer
- Build in human yes/no node for user to review the output before proceeding to the next step

## 5) IC Note Drafter Agent

**Purpose:** Compose a first-draft Investment Committee "IC" memo that merges output from 2-4 with citations

### Inputs

- Firm DNA & Past Deal Memos from 0
- Outputs from Agents 2-4

### Outputs

Gdoc/Word with Required Sections (default order template below, to be configured/ customized based on past memo provided by customers or customer preferences), and include relevant charts.

1. Executive Summary
2. Company Overview (Leverage outputs from Agent 2 & 3)
3. Deal Snapshot (company, round size, dynamics, our relationship with founders, use of funds, ownership, sources & uses)
4. Market Overview (from Agent 2 & 3)
5. Competition & MOAT (from Agent 2 & 3)
6. Team Overview (from Agent 2 & 3)
7. Product & CVPs (from Agent 2 &3)
8. Business Model & Monetization (from Agent 2 &3)
9. Financial and return analysis (from Agent 3 + analysts' further judgement for foreward looking projections and point of view)
   - Includes unit economics
   - Includes Benchmark Read Out (Optional)
10. Summary Investment Highlights (from Agent 2&3)
11. Summary Investment Risks and Potential Mitigants (from Agent 4 predominantly)
12. Recommendation & Next Steps: Suggest a crisp recommendation line whether you'd proceed to the next stage or stop pursuing this deal and why (e.g., "Advance to confirmatory DD on X, Y, Z; subject to {{conditions}} with target non-binding term sheet issuance by {{date}} "). Then list an Open Questions/ DD Checklist (5–10 items) referencing the Risk Scanner Agent #4's.
13. Appendix (tables/charts)

Example Output: https://www.bvp.com/memos

### Acceptance

- For final memo output, adhere to user prompts and formatting requirements; footnotes render cleanly; discrepancy handling logged.
- 100% factual/quantitative claims cited.
- All required sections present and ordered; optional section clearly "Not available" if absent.

---

## To validate/ confirm

### Technical team

- What tool would you use to build this? Is that the easiest one u know of?
  - N8N
  - Agentkit
  - Claude + Claude Skills
- Globally: Use anonymous names (e.g., "Fund A", "Target B or Cove example") and add disclaimer "Fictitious example for demo/MVP." Confirm?
- On prompt: do we define it by systems vs. developer prompt?
- Include human yes/no node betweens steps, to ensure output is good enough before the next step. Confirm?
- Are we open to use limited non-ChatGPT agentkit/tools for A) export to excel B) data sources integration/API/MCP/connectors to get a more value-additive demo prototype?
- If ChatGPT-only, then narrower ideal customer profile e.g seed stage /early stage VC and solo GPs only), because the later stage investors require heavy excel functionalities typically
- Package offerings: how can we then push for upgraded managed custom GPT?
- Build path: Trade off between the approach where we build out in enterprise project then port over to agentkit multi-agent workflow vs. directly build in agentkit then connect to Chatgpt enterprise via connector?
- Timeline: First pass, UAT & demo dates
- Initial Customer Leads:


