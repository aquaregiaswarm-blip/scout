# Project Scout

## Agentic Sales Intelligence Platform for VAR/SI Sales Teams

---

# Part 1: Product Description

---

## What Is It?

Scout is an agentic deep research platform purpose-built for account executives and business development executives at Value Added Resellers (VARs) and Systems Integrators (SIs). Given a company name, industry, and a vague idea about a project or initiative, Scout autonomously crawls the open internet, collects intelligence, reasons about what else to look for, and iteratively builds a living, interactive intelligence profile — giving sellers everything they need to have effective, productive, and differentiated conversations.

Unlike traditional sales intelligence tools that return static data, Scout operates as a **reasoning research loop**: it gathers, analyzes, identifies gaps, formulates new research paths, and goes back out to find more — repeating until it reaches a confidence threshold or the user tells it to stop.

---

## Who Is It For?

The primary users are **Account Executives (AEs)** and **Business Development (BD) executives** who work for a VAR/SI — a company that can sell and resell virtually any technology product while also delivering professional services (systems integration, transformative consulting). These sellers face a unique challenge: they don't pitch a single product. They need to deeply understand the customer's problem in order to assemble the right combination of vendor products, professional services, and consulting engagements. Deep, contextualized research is their competitive advantage.

The tool is designed for **collaborative use by deal teams of 2–4 people** (e.g., an AE, a BD rep, a solutions architect, and a manager) who share and build on the same intelligence profiles.

---

## How Does It Work?

### Inputs

The user provides three starting inputs:

- **Company name** (required)
- **Industry** (required)
- **Project or initiative** (required, but can be vague or exploratory — e.g., "I heard they're doing something with cloud" or "data modernization efforts")

### The Agentic Research Loop

1. **Strategic Planning** — A Prime Agent analyzes the request, breaks it into discrete research topics, and dispatches up to 5 specialized Research Sub-Agents in parallel.

2. **Parallel Research** — Each Research Sub-Agent executes its focused assignment independently — searching, scraping, and extracting information using available tools. Users can see what each sub-agent is researching and can stop any individual research path.

3. **Synthesis** — A Synthesis Agent takes raw findings from all sub-agents, merges them, deduplicates, resolves contradictions, categorizes findings, and assesses confidence across intelligence categories.

4. **Presentation** — A Presentation Agent formats the structured intelligence into dashboard-ready content with summaries, insights, and portfolio mapping.

5. **Dashboard Update** — After every other cycle, the interactive dashboard is updated with new findings. The user sees intelligence accumulating in real-time.

6. **Next Cycle** — The Prime Agent reviews the synthesis, identifies remaining gaps, and dispatches a new round of sub-agents — or signals completion when confidence is sufficient or returns are diminishing.

### Transparency & Control

- The agent **shows the user what topics each sub-agent is currently researching**.
- The user can **stop any individual research path** at any time. If stopped, the sub-agent returns whatever results it has gathered so far if they are deemed important.
- The agent has a **confidence threshold / diminishing returns feedback loop** that tells it when to stop a research path autonomously.

### Follow-Up Questions

From the dashboard, the user can ask follow-up questions at any time, which trigger a **new agentic research loop** that further enriches the profile.

### Initiative Discovery

Scout doesn't just research what the user asks about — it **discovers initiatives the user didn't know existed**. If the user inputs "Acme Corp + data modernization" but the agent finds signals of a SASE/network security overhaul, it surfaces this to the user and asks whether to pursue a deep dive. A single company profile can have **multiple initiatives** being tracked simultaneously.

---

## What Does the Output Look Like?

The primary interface is an **interactive dashboard** where the user can browse categorized intelligence and drill into specific areas. Key intelligence categories include:

### People Intelligence
- **Org chart mapping** — who reports to whom, who owns the initiative, who controls budget
- **Influence mapping** — decision makers, technical evaluators, champions, and potential blockers
- **Relationship proximity** — connections between the user's own company and the target (future: CRM/LinkedIn integration)
- **Communication style signals** — inferred from public content (data-driven, risk-averse, innovation-focused, etc.)
- **Recent activity** — what key people are posting, speaking about, or publishing

### Initiative Intelligence
- What is the initiative and what problem does it solve?
- Current status and timeline
- Technology or approach they appear to be using
- Budget signals and procurement indicators

### Competitive & Market Context
- What the target company's **competitors** are doing to solve similar problems
- What **vendors and solutions** are commonly used for this type of initiative
- What **vendors or partners the target company is already working with** (displacement or complement opportunities)

### Portfolio Mapping
- Based on findings, Scout **maps intelligence back to the user's own company's portfolio** of vendor partnerships and service offerings
- Surfaces relevant capabilities: "Based on this initiative, here are the solutions your company is positioned to offer"

---

## Data Sources

Scout starts with open, freely accessible sources and expands over time:

### Phase 1 (v0.1 — No Licenses Required)
- Company websites, about pages, leadership pages
- Press releases and news articles
- SEC filings, earnings calls, investor presentations, annual reports
- Job postings (signals for tech stack, priorities, and growth areas)
- Government contracts and procurement portals (RFPs, awards)
- Publicly available technographic signals
- Conference talks, webinars, and public presentations
- Social media posts and public content from key individuals

### Future Phases (Licensed/Authenticated Sources)
- LinkedIn (org charts, profiles, activity, connections)
- Technographic platforms (BuiltWith, Wappalyzer, etc.)
- Industry analyst reports (Gartner, Forrester, IDC)
- CRM integration (Salesforce, HubSpot, etc.)
- Internal knowledge bases

---

## Persistence & Collaboration

- **Living Profiles** — Each company + initiative profile is persistent. Intelligence compounds over time as users trigger new research loops and ask follow-up questions.
- **Manual Refresh** — Profile updates are triggered manually by the user (proactive alerts are a future enhancement).
- **Team Collaboration** — Profiles are shared between 2–4 team members working the same account. All team members see the same intelligence and can trigger research or ask questions.
- **Multi-Initiative Tracking** — A single company can have multiple initiative profiles being tracked simultaneously.

---

## User's Own Company Portfolio

To enable portfolio mapping (matching findings to what the user's company can offer), Scout requires knowledge of the user's own capabilities:

- **Initial Setup** — A curated, manually maintained list of vendor partnerships, service capabilities, and key differentiators (e.g., "Cisco Gold Partner, AWS Advanced Partner, Salesforce implementation practice, managed security practice")
- **Bootstrap Approach** — The initial portfolio can be assembled using internal tools like Microsoft Copilot and Glean to search existing company documents and compile a starting point
- **Agent-Assisted Discovery (Future)** — Scout could eventually research the user's own company the same way it researches targets, auto-discovering capabilities from public information
- **Maintenance** — Manually updated as partnerships and capabilities evolve

---

## The Core Insight

In VAR/SI sales, the sellers who win are the ones who understand the customer's problem more deeply than anyone else — because that understanding is what allows them to assemble the right solution from a vast portfolio. Scout turns a vague hunch into a comprehensive, actionable intelligence profile, discovers opportunities the seller didn't even know about, and maps it all back to what they can actually sell. It doesn't just help sellers prepare — it helps them see what others miss.

---

# Part 2: Architecture

---

## Guiding Principles

1. **Ship fast, learn fast.** v0.1 exists to get in front of 2–3 sellers. Every decision optimizes for speed-to-feedback over long-term scalability.
2. **Simple until proven insufficient.** No framework, abstraction, or infrastructure unless it solves a real problem today.
3. **The agentic loop is the product.** Everything else (dashboard, persistence, auth) is scaffolding around the core research engine. That engine gets the most investment.
4. **Expand data sources over time.** Start with what's free and easy to wire up. The architecture should make adding new sources trivial.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND                             │
│              Next.js (React) Dashboard                   │
│         SSE connection for real-time updates              │
├─────────────────────────────────────────────────────────┤
│                     BACKEND API                          │
│                 Python / FastAPI                          │
│            REST endpoints + SSE streams                   │
├──────────┬──────────────────────┬───────────────────────┤
│ RESEARCH │   MULTI-AGENT        │   DATA LAYER          │
│ TOOLS    │   ORCHESTRATION      │   PostgreSQL          │
│          │                      │   + JSONB for          │
│ - Search │  Prime Agent         │     flexible           │
│ - Scrape │    ↓                 │     findings           │
│ - SEC    │  Research Sub-Agents │                        │
│ - Jobs   │    ↓                 │                        │
│ - News   │  Synthesis Agent     │                        │
│ - Gov    │    ↓                 │                        │
│          │  Presentation Agent  │                        │
└──────────┴──────────────────────┴───────────────────────┘
```

---

## Decision 1: Multi-Agent Design (Custom with Anthropic SDK)

### Options Considered
| Option | Pros | Cons |
|--------|------|------|
| **LangGraph** | Built for stateful loops, checkpointing, visualization | Added dependency, learning curve, abstractions you may not need yet |
| **CrewAI** | Multi-agent collaboration built-in | Opinionated, heavier than needed, more about role-based agents |
| **Autogen** | Microsoft-backed, multi-agent | Complex setup, overkill for this pattern |
| **Custom (Anthropic SDK + tool use)** | Maximum control, no abstractions, simple to debug, fastest to build | You write your own loop management and state tracking |

### Recommendation: Custom with Anthropic SDK

Scout's multi-agent system is conceptually clean: a Prime Agent plans and delegates, Research Sub-Agents execute in parallel, a Synthesis Agent merges findings, and a Presentation Agent formats output. This maps directly to Python async functions calling the Anthropic API with different system prompts and tool configurations. No framework needed.

A framework like LangGraph adds value when your state machine gets complex (branching, checkpointing, recovery). You may want it later. But for v0.1, the overhead of learning and debugging through an abstraction layer will slow you down more than writing the orchestration yourself.

---

## Decision 2: AI Model Selection

### Recommendation: Claude Sonnet 4 (claude-sonnet-4-5-20250514)

**Why Sonnet, not Opus for v0.1:** Fast, capable enough for research reasoning, and significantly cheaper. With a multi-agent design dispatching up to 5 sub-agents per cycle across multiple cycles, API costs add up. Sonnet keeps costs controlled during iteration.

**Model allocation by agent role:**

| Agent | Model | Extended Thinking | Why |
|-------|-------|-------------------|-----|
| Prime Agent | Sonnet 4 | Yes | Needs deep strategic reasoning about what to research and when to stop |
| Research Sub-Agents (up to 5) | Sonnet 4 | No | Focused task execution — search, scrape, extract. Speed matters more than depth. |
| Synthesis Agent | Sonnet 4 | Yes | Needs to reason through contradictions, merge findings, assess confidence |
| Presentation Agent | Sonnet 4 | No | Formatting and writing — doesn't need deep reasoning |

Extended thinking (which uses more tokens) is only enabled where reasoning depth genuinely matters. Research and presentation agents prioritize speed.

Upgrade path: If reasoning quality isn't sufficient during testing, upgrade specific agent roles to Opus. Start with Sonnet everywhere.

---

## Decision 3: Backend — Python + FastAPI

**Why:**
- Python is the natural home for AI/ML work. Every SDK, scraping library, and data processing tool has first-class Python support.
- FastAPI gives you async out of the box (critical — research sub-agents run in parallel with lots of I/O waiting), automatic OpenAPI docs, type hints, and SSE support.
- The scraping ecosystem in Python (httpx, BeautifulSoup, Playwright) is more mature than Node alternatives.

---

## Decision 4: Frontend — Next.js + React + Tailwind CSS

**Why:**
- React's component model maps well to the dashboard panels (people, initiatives, competitive intel, etc.).
- Next.js gives you file-based routing, server-side rendering if needed later, and a clean project structure.
- Tailwind CSS means fast UI development without design system overhead. The dashboard doesn't need to be beautiful for v0.1; it needs to be functional and readable.

**Key frontend components:**
- Company/initiative input form
- Research status panel (what each sub-agent is currently investigating, with stop buttons)
- Findings dashboard (categorized intelligence cards)
- Active research paths (with individual stop controls)
- Follow-up question input
- Team member indicators (who else is viewing)

**Real-time updates via SSE (Server-Sent Events):**
- Simpler than WebSockets — one-directional (server → client), which is exactly what you need for "agents are updating the dashboard."
- Native browser support via `EventSource` API.
- Event types: `subagent_started`, `subagent_completed`, `synthesis_complete`, `findings_updated`, `cycle_complete`, `research_done`, `initiative_discovered`.
- Follow-up questions are regular POST requests that trigger new research loops.

---

## Decision 5: Database — PostgreSQL with JSONB

**Why:**
- PostgreSQL gives you relational structure where you need it (users, teams, companies, initiatives — these have clear schemas) and JSONB flexibility where you need it (research findings, which will evolve in structure as you learn what data matters).
- You avoid the "everything is a document" trap of MongoDB while still getting schema flexibility.
- PostgreSQL is rock-solid, free, and available as a managed service on GCP (Cloud SQL).

**Core data model:**

```
teams
├── id, name, created_at

users
├── id, team_id, name, email, created_at

company_profiles
├── id, team_id, company_name, industry, created_at, updated_at

initiatives
├── id, company_profile_id, name, description, status, discovered_by_agent (bool)
├── created_at, updated_at

research_sessions
├── id, initiative_id, triggered_by (user_id), status, started_at, completed_at

research_cycles
├── id, research_session_id, cycle_number, prime_agent_plan (JSONB)
├── confidence_assessment (JSONB), started_at, completed_at

research_paths
├── id, research_cycle_id, assignment_id, topic, status (active/stopped/completed/exhausted)
├── reasoning (why the prime agent chose this path)

research_findings
├── id, research_path_id, initiative_id
├── category (enum: people, technology, competitive, market, financial, initiative_status)
├── content (JSONB — flexible structure per category)
├── source_url, source_type, confidence_score
├── created_at

synthesized_intelligence
├── id, initiative_id, category, structured_content (JSONB)
├── confidence_score, last_updated_cycle_id, created_at, updated_at

dashboard_content
├── id, initiative_id, content (JSONB — presentation-ready)
├── portfolio_recommendations (JSONB)
├── created_at, updated_at

portfolio
├── id, team_id, vendor_name, partnership_level, capabilities (JSONB)
├── created_at, updated_at
```

The JSONB columns are key — a "people" finding has different fields than a "technology" finding, and you'll be adding new fields constantly as you learn. JSONB lets you evolve without migrations.

---

## Decision 6: Web Scraping & Data Collection

### Recommendation: Layered approach — API-first, scrape as fallback

| Source | Approach | Why |
|--------|----------|-----|
| **Web search** | Brave Search API | Generous free tier (2,000 queries/month), simple REST API. Upgrade to paid ($5/mo for 20k queries) when needed. |
| **Page scraping** | httpx + BeautifulSoup | Fast, lightweight, handles 90% of pages. No browser overhead. |
| **JS-heavy pages** | Playwright (async) | For pages that require JavaScript rendering. Use sparingly — it's slow. |
| **SEC filings** | SEC EDGAR API (free) | Direct access to 10-K, 10-Q, 8-K, earnings transcripts. No API key needed. |
| **Job postings** | Scrape from public boards | Company career pages first (easiest), then public job boards. |
| **News** | Brave Search API (news mode) | Same API, news-specific search. |
| **Government/procurement** | SAM.gov API (free) | Federal contracts and opportunities. Free API key registration. |

**Adding new sources is trivial:** Each data source is a tool function that Research Sub-Agents can call. Adding a new source = writing a Python function + adding it to the tool schema. The Prime Agent automatically incorporates new tools into its planning.

---

## Decision 7: Task Orchestration

### Recommendation: FastAPI Background Tasks with asyncio

**Why:** A research session is a single long-running async task that internally dispatches parallel sub-agents via `asyncio.gather`. For v0.1 with 2–3 users, you don't need a distributed task queue.

**Flow:**
1. User hits `POST /api/research/start` with company, industry, initiative
2. Backend creates a `research_session` record, returns session ID
3. Backend spawns an async task running the orchestrator
4. Frontend connects to `GET /api/research/{session_id}/stream` (SSE)
5. Orchestrator runs the Prime Agent, dispatches up to 5 Research Sub-Agents in parallel, runs Synthesis and Presentation agents
6. Events stream to the dashboard throughout
7. User can `POST /api/research/{session_id}/paths/{path_id}/stop` to halt a sub-agent
8. Orchestrator checks for stop signals between cycles

**Upgrade path:** If you need parallel research sessions for multiple users, add Celery + Redis. Don't pay that complexity cost on day one.

---

## Decision 8: Authentication & Collaboration

### Recommendation: Simple email + password auth with JWT tokens (v0.1)

**Why:** You need just enough auth to support 2–4 people on a team sharing profiles. Email + hashed password + JWT is a few hours of work. Team membership is a simple `users.team_id` foreign key. All company profiles and research findings are scoped to a team.

**Future:** Add SSO/OAuth when you move beyond the pilot group.

---

## Decision 9: Cloud Platform & Deployment (GCP)

**Deployment for v0.1:**
- **Docker Compose locally** for development
- **GCP Cloud Run** for the backend (fully managed, scales to zero, HTTPS automatic)
- **Vercel** for the Next.js frontend (free tier, zero-config deployment)
- **Cloud SQL for PostgreSQL** (or a free-tier Neon/Supabase instance to start even faster)
- **Google Cloud Storage (GCS)** for storing raw scraped content and downloaded documents
- **GCP Secret Manager** for API keys and credentials
- **Google Cloud Logging** for observability (automatic with Cloud Run)
- **Google Artifact Registry** for container images

**Even simpler start:** Run everything locally with Docker Compose. Don't deploy to cloud until you're ready for the 2–3 seller test. This could save you a week.

---

# Part 3: Multi-Agent Architecture — Detailed Design

---

## Agent System Overview

```
                        ┌─────────────────────┐
                        │    PRIME AGENT       │
                        │   (Orchestrator)     │
                        │                      │
                        │  - Analyzes request   │
                        │  - Plans research     │
                        │  - Dispatches workers │
                        │  - Reviews results    │
                        │  - Decides next cycle │
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
           Dispatches up to 5 sub-agents in parallel
                    │              │               │
              ┌─────▼─────┐ ┌─────▼─────┐ ┌──────▼─────┐
              │ RESEARCH   │ │ RESEARCH   │ │ RESEARCH    │
              │ SUB-AGENT  │ │ SUB-AGENT  │ │ SUB-AGENT   │
              │            │ │            │ │             │
              │ Topic:     │ │ Topic:     │ │ Topic:      │
              │ "CTO and   │ │ "Cloud     │ │ "SEC filings│
              │ leadership"│ │ migration  │ │ and recent  │
              │            │ │ tech stack"│ │ earnings"   │
              └─────┬──────┘ └─────┬──────┘ └──────┬─────┘
                    │              │               │
                    └──────────────┼───────────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │  SYNTHESIS AGENT     │
                        │                      │
                        │  - Merges raw findings│
                        │  - Deduplicates       │
                        │  - Categorizes        │
                        │  - Assesses confidence│
                        │  - Flags gaps         │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │ PRESENTATION AGENT   │
                        │                      │
                        │  - Structures for UI  │
                        │  - Writes summaries   │
                        │  - Generates insights │
                        │  - Maps to portfolio  │
                        └──────────┬───────────┘
                                   │
                                   ▼
                          Dashboard Update
                          (via SSE stream)
                                   │
                                   ▼
                        ┌─────────────────────┐
                        │    PRIME AGENT       │
                        │   (Next Cycle)       │
                        │                      │
                        │  Reviews synthesis    │
                        │  Plans next research  │
                        │  Dispatches again     │
                        │  OR signals done      │
                        └──────────────────────┘
```

---

## Agent Roles — Detailed

### 1. Prime Agent (Orchestrator)

**Model:** Claude Sonnet 4 with extended thinking enabled

**Role:** The strategist. It never touches a tool directly. It thinks, plans, delegates, and evaluates.

**System prompt responsibilities:**
- Receive the initial request (company, industry, initiative)
- Break the research problem into discrete, parallelizable topics
- Dispatch up to 5 research sub-agents with specific, focused assignments
- Review synthesized results after each cycle
- Identify gaps, contradictions, and new threads to pull
- Decide whether to launch another cycle, surface a discovered initiative, or stop
- Maintain a mental model of confidence per intelligence category

**Input:** User request + accumulated intelligence from prior cycles
**Output:** A research plan — a list of focused assignments for sub-agents

**Example output from Prime Agent:**

```json
{
  "cycle": 2,
  "reasoning": "Cycle 1 confirmed Acme Corp is pursuing a cloud migration. We identified the CTO (Jane Smith) as the likely executive sponsor but don't know the project lead. Job postings suggest Azure, but their earnings call mentioned 'multi-cloud.' Need to resolve this contradiction. No competitive intelligence yet.",
  "assignments": [
    {
      "id": "research-2a",
      "topic": "Acme Corp cloud migration project leadership and team structure",
      "instructions": "Search for the specific team or division leading the cloud migration. Look for VP/Director level names associated with infrastructure, cloud, or digital transformation. Check LinkedIn posts, conference speaker lists, and press releases.",
      "tools_suggested": ["web_search", "web_scrape"],
      "priority": "high"
    },
    {
      "id": "research-2b",
      "topic": "Acme Corp multi-cloud vs Azure — resolve technology direction",
      "instructions": "The Q3 earnings call mentioned multi-cloud strategy but job postings are Azure-heavy. Search for more specific signals: blog posts, case studies, partnership announcements with cloud vendors, or technical conference talks by Acme engineers.",
      "tools_suggested": ["web_search", "web_scrape"],
      "priority": "high"
    },
    {
      "id": "research-2c",
      "topic": "Competitive landscape — how peers in [industry] are handling cloud migration",
      "instructions": "Search for cloud migration case studies and announcements from Acme's top 3 competitors. What vendors and SIs are they using? What approaches are they taking?",
      "tools_suggested": ["web_search", "web_scrape"],
      "priority": "medium"
    }
  ],
  "discovered_initiatives": [],
  "confidence_assessment": {
    "people": "low — know CTO, need project-level contacts",
    "initiative_status": "medium — confirmed it exists, unclear on timeline",
    "technology": "low — contradictory signals",
    "competitive": "none — not yet researched",
    "financial_signals": "medium — earnings call provided some context"
  }
}
```

---

### 2. Research Sub-Agents (Workers)

**Model:** Claude Sonnet 4 (standard — no extended thinking)

**Role:** Focused researchers. Each one gets a single, specific assignment and goes deep on it. They execute tool calls (search, scrape, etc.) and return raw, structured findings.

**Concurrency cap:** Maximum 5 sub-agents per cycle.

**System prompt responsibilities:**
- You are a research specialist with a specific assignment
- Use the provided tools to gather information on your assigned topic
- Be thorough — follow promising leads, click into relevant pages
- Return structured findings: what you found, where you found it, how confident you are
- Flag anything surprising or tangentially related that the prime agent should know about
- You have a budget of 8–10 tool calls — use them wisely

**Key design property:** Each sub-agent is **stateless and independent**. It gets an assignment, does its work, returns results. It doesn't know about or coordinate with other sub-agents. The Prime Agent handles coordination.

**Input:** A focused research assignment from the Prime Agent
**Output:** Raw findings in a structured format

**Example output from Research Sub-Agent:**

```json
{
  "assignment_id": "research-2a",
  "topic": "Acme Corp cloud migration project leadership and team structure",
  "findings": [
    {
      "content": "Found VP of Cloud Engineering: Michael Torres. His LinkedIn shows he joined Acme 8 months ago from AWS.",
      "source_url": "https://example.com/article-about-acme-hires",
      "source_type": "news_article",
      "confidence": "high",
      "category_hint": "people"
    },
    {
      "content": "Acme posted 12 cloud-related positions in the last 60 days, all reporting to the 'Cloud Center of Excellence' team.",
      "source_url": "https://acme.com/careers",
      "source_type": "job_posting",
      "confidence": "high",
      "category_hint": "initiative_status"
    }
  ],
  "tangential_signals": [
    "Multiple job postings mention 'data sovereignty' requirements — may indicate a compliance/regulatory dimension to the migration."
  ],
  "tools_used": 6,
  "exhausted": false
}
```

---

### 3. Synthesis Agent

**Model:** Claude Sonnet 4 with extended thinking enabled

**Role:** The analyst. Takes raw findings from all sub-agents in a cycle, merges them, deduplicates, resolves contradictions, categorizes into intelligence categories, and assesses overall confidence.

**System prompt responsibilities:**
- Receive raw findings from multiple research sub-agents
- Merge with existing intelligence from prior cycles (avoid duplication)
- Categorize each finding: People, Initiative Status, Technology, Competitive, Financial, Market
- Resolve contradictions (e.g., "earnings call says multi-cloud but hiring is Azure-heavy" → "Likely Azure-first multi-cloud strategy")
- Assess confidence per category
- Flag gaps that need more research
- Identify any newly discovered initiatives

**Input:** Raw findings from all sub-agents in the current cycle + accumulated intelligence from prior cycles
**Output:** Updated, structured intelligence profile

---

### 4. Presentation Agent

**Model:** Claude Sonnet 4 (standard — no extended thinking)

**Role:** The storyteller. Takes the structured intelligence profile and formats it for the dashboard. Writes human-readable summaries, generates insights, and maps findings to the user's portfolio.

**System prompt responsibilities:**
- Take structured intelligence and produce dashboard-ready content
- Write concise, actionable summaries for each category
- Generate "so what?" insights (e.g., "The CTO came from AWS, which may indicate a bias toward AWS solutions — consider leading with your AWS partnership")
- Map findings to the user's portfolio where relevant
- Highlight the strongest conversation starters for a seller
- Write in the language of a sales briefing, not an academic report

**Input:** Structured intelligence profile from the Synthesis Agent + user's portfolio data
**Output:** Dashboard-ready content with summaries, insights, and portfolio recommendations

---

## How the Cycle Runs — End to End

```
1. USER inputs: Company = "Acme Corp", Industry = "Manufacturing", Initiative = "Cloud migration"

2. PRIME AGENT (thinks with extended thinking):
   "Manufacturing company doing cloud migration. I need to understand:
    - Who they are and their scale
    - Who leads IT/digital transformation
    - What the migration involves
    - What they're currently running
    - What their competitors are doing
    Let me create 4 focused research assignments."
   → Outputs: 4 research assignments

3. ORCHESTRATOR dispatches 4 RESEARCH SUB-AGENTS in parallel (asyncio.gather)
   → Each sub-agent makes 5–10 tool calls independently
   → Each returns structured raw findings
   → SSE events stream: "Researching: company overview", "Researching: leadership team", etc.
   → User can stop any sub-agent via the dashboard

4. SYNTHESIS AGENT receives all raw findings:
   "I have 23 raw findings across 4 topics. Let me merge, deduplicate,
    categorize, and assess confidence..."
   → Outputs: Structured intelligence profile with confidence scores

5. PRESENTATION AGENT receives structured intelligence:
   "Let me format this for the dashboard and generate insights..."
   → Outputs: Dashboard-ready content
   → SSE event: "findings_updated" with new dashboard content

6. PRIME AGENT reviews the synthesis (NOT the presentation — it works from structured data):
   "Good progress on people and initiative status. Technology is contradictory.
    No competitive intelligence yet. Let me plan cycle 2 with 3 more assignments..."
   → Go to step 3

7. REPEAT until:
   - Prime Agent signals sufficient confidence across all categories
   - Two consecutive cycles produce minimal new information (diminishing returns)
   - User is satisfied and doesn't ask follow-up questions
```

---

## Parallelism Implementation

Using Python's `asyncio` for concurrent sub-agent execution:

```python
async def execute_cycle(assignments: list[Assignment]) -> list[SubAgentResult]:
    """Run up to 5 research sub-agents in parallel."""
    tasks = []
    for assignment in assignments[:5]:  # Hard cap at 5
        task = asyncio.create_task(
            run_research_subagent(assignment)
        )
        tasks.append(task)

    # Wait for all sub-agents, but handle individual failures gracefully
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out failures, log them, return successful results
    successful = [r for r in results if not isinstance(r, Exception)]
    return successful
```

This is simple, native Python, and gives you true parallelism since the sub-agents are I/O-bound (waiting on API calls and web requests).

---

## Confidence & Diminishing Returns

The Prime Agent's system prompt instructs it to maintain a confidence model per category:

- **People**: Do I know the key decision makers and their roles?
- **Initiative**: Do I understand what it is, why, and current status?
- **Technology**: Do I know what they're using or evaluating?
- **Competitive**: Do I know what alternatives exist?
- **Timeline/Budget**: Do I have any signals on timing or spend?

The Prime Agent reports confidence levels after reviewing each synthesis. When all categories are at "sufficient" or when two consecutive cycles don't produce meaningful new information, the agent stops.

---

## User Control Between Cycles

Between each cycle, the orchestrator:
1. Checks for stop signals on individual research paths (sub-agents)
2. Checks if the user has asked a follow-up question (which creates a new focused loop)
3. Streams current research path topics so the UI can display them with stop buttons

---

# Part 4: Project Structure & Build Plan

---

## Project Structure

```
scout/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, routes
│   │   ├── config.py                  # Settings, API keys, env vars
│   │   ├── models/                    # Pydantic models (request/response schemas)
│   │   │   ├── company.py
│   │   │   ├── initiative.py
│   │   │   ├── research.py
│   │   │   └── user.py
│   │   ├── db/                        # Database layer
│   │   │   ├── database.py            # Connection, session management
│   │   │   ├── tables.py              # SQLAlchemy table definitions
│   │   │   └── queries.py             # Common queries
│   │   ├── agents/                    # THE CORE — multi-agent research engine
│   │   │   ├── orchestrator.py        # Manages the full cycle loop
│   │   │   ├── prime_agent.py         # Strategic planning and delegation
│   │   │   ├── research_agent.py      # Focused research worker (one per assignment)
│   │   │   ├── synthesis_agent.py     # Merges and analyzes raw findings
│   │   │   ├── presentation_agent.py  # Formats intelligence for dashboard
│   │   │   ├── prompts/               # System prompts for each agent role
│   │   │   │   ├── prime.py
│   │   │   │   ├── research.py
│   │   │   │   ├── synthesis.py
│   │   │   │   └── presentation.py
│   │   │   └── tools/                 # Shared tools for research sub-agents
│   │   │       ├── web_search.py      # Brave Search API
│   │   │       ├── web_scrape.py      # httpx + BeautifulSoup
│   │   │       ├── sec_filings.py     # SEC EDGAR API
│   │   │       ├── job_postings.py    # Career page scraper
│   │   │       └── news_search.py     # Brave News API
│   │   ├── services/                  # Business logic
│   │   │   ├── research_service.py
│   │   │   ├── company_service.py
│   │   │   └── portfolio_service.py
│   │   └── streams/                   # SSE event streaming
│   │       └── events.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── app/                       # Next.js app router
│   │   ├── components/
│   │   │   ├── ResearchInput.tsx       # Company/initiative form
│   │   │   ├── ResearchStatus.tsx      # Active sub-agents with stop buttons
│   │   │   ├── Dashboard.tsx           # Main intelligence dashboard
│   │   │   ├── FindingsCard.tsx        # Individual finding display
│   │   │   ├── PeoplePanel.tsx         # People intelligence panel
│   │   │   ├── InitiativePanel.tsx     # Initiative status panel
│   │   │   ├── TechPanel.tsx           # Technology intelligence panel
│   │   │   ├── CompetitivePanel.tsx    # Competitive landscape panel
│   │   │   ├── PortfolioPanel.tsx      # Portfolio mapping panel
│   │   │   ├── FollowUpInput.tsx       # Ask follow-up questions
│   │   │   └── DiscoveredInitiatives.tsx # Newly discovered initiatives
│   │   ├── hooks/
│   │   │   └── useResearchStream.ts    # SSE connection hook
│   │   └── lib/
│   │       └── api.ts                  # API client
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

---

## v0.1 Build Plan

### Sprint 1 (Week 1): The Multi-Agent Engine

**Goal:** The core agent loop works end-to-end in a terminal. No UI, no database.

**Tasks:**
- Set up Python project with FastAPI skeleton and Anthropic SDK
- Write system prompts for all 4 agent roles (prime, research, synthesis, presentation)
- Implement Prime Agent — takes company + initiative, outputs research plan
- Implement Research Sub-Agent — takes assignment, executes tools, returns findings
- Implement parallel dispatch via `asyncio.gather` (cap at 5)
- Build 2 tools: web search (Brave API) and web scrape (httpx + BeautifulSoup)
- Implement Synthesis Agent — merges findings, categorizes, assesses confidence
- Skip Presentation Agent for Sprint 1 — Synthesis output is good enough to evaluate
- Test end-to-end: input company + initiative → watch agents plan, research in parallel, synthesize
- Iterate on system prompts based on output quality

**Exit criteria:** You can run `python -m app.agents.orchestrator "Acme Corp" "Manufacturing" "cloud migration"` and get back categorized, useful intelligence after 2–3 cycles.

### Sprint 2 (Week 2): Persistence + API

**Goal:** Research sessions are saved and accessible via API. SSE streaming works.

**Tasks:**
- Set up PostgreSQL (local Docker or free Neon/Supabase instance)
- Implement the data model (companies, initiatives, findings, sessions, cycles, paths)
- Create FastAPI endpoints:
  - `POST /api/research/start` — kick off a session
  - `GET /api/research/{session_id}/stream` — SSE stream
  - `GET /api/research/{session_id}` — get current state
  - `POST /api/research/{session_id}/paths/{path_id}/stop` — stop a sub-agent
  - `POST /api/research/{session_id}/follow-up` — ask a follow-up question
  - `GET /api/companies/{id}` — get company profile with all initiatives
- Implement SSE streaming from the orchestrator
- Add 1–2 more tools: SEC EDGAR, job posting scraper
- Implement the Presentation Agent

**Exit criteria:** You can start research via API, watch events stream, stop a path, and retrieve persisted results.

### Sprint 3 (Week 3): Dashboard MVP

**Goal:** A functional web dashboard that a seller can actually use.

**Tasks:**
- Set up Next.js project with Tailwind
- Build the input form (company, industry, initiative)
- Build the research status panel (active sub-agents with stop buttons)
- Build the findings dashboard with categorized panels (People, Initiative, Tech, Competitive, Financial)
- Connect SSE for real-time updates (useResearchStream hook)
- Build the follow-up question input
- Build the discovered initiatives component (surface + confirm for deep dive)
- Basic company profile page (list of initiatives, research history)

**Exit criteria:** A seller can open the app, type in a company and initiative, watch research happen in real-time, browse categorized findings, and ask follow-up questions.

### Sprint 4 (Week 4): Polish for User Testing

**Goal:** Ready to put in front of 2–3 sellers for feedback.

**Tasks:**
- Add simple auth (email/password + JWT)
- Add team/collaboration (shared profiles, team scoping)
- Add portfolio configuration (static form/JSON upload for vendor partnerships and capabilities)
- Wire portfolio data into the Presentation Agent for mapping recommendations
- Error handling and resilience (what happens when a sub-agent fails? When a tool times out?)
- UX polish: loading states, error states, empty states
- Deploy: Vercel (frontend) + GCP Cloud Run (backend) + Cloud SQL (database)
- OR keep it simpler: deploy everything on a single GCE instance with Docker Compose

**Exit criteria:** 2–3 sellers can log in, run research, collaborate on profiles, see portfolio recommendations, and provide feedback.

---

## What This Architecture Does NOT Include (Intentionally)

These are explicitly deferred to keep v0.1 fast:

- **No caching layer** (Redis) — add when performance requires it
- **No distributed task queue** (Celery) — add when you need parallel sessions for many users
- **No OAuth/SSO** — add when you move beyond the pilot
- **No LinkedIn integration** — requires API access and compliance
- **No proactive alerts** — manual refresh only for now
- **No agent-assisted portfolio discovery** — static portfolio config for v0.1
- **No mobile** — desktop dashboard only

---

## Technology Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| AI Model | Claude Sonnet 4 (claude-sonnet-4-5-20250514) | Fast, capable, cost-effective for multi-agent loops |
| Agent Architecture | Custom multi-agent (Anthropic SDK + tool use) | 4 specialized agents, parallel sub-agents, maximum control |
| Sub-Agent Cap | 5 per cycle | Cost and complexity control |
| Backend | Python + FastAPI | Best ecosystem for AI + scraping, async native |
| Frontend | Next.js + React + Tailwind | Interactive dashboard, SSE support, fast to build |
| Database | PostgreSQL + JSONB | Structured where needed, flexible where needed |
| Web Search | Brave Search API | Free tier, simple API, good results |
| Web Scraping | httpx + BeautifulSoup (+ Playwright fallback) | Lightweight, covers most cases |
| SEC Data | EDGAR API | Free, no key needed |
| Real-time | Server-Sent Events (SSE) | Simpler than WebSockets, sufficient for one-way updates |
| Auth | Email/password + JWT | Minimum viable auth for team access |
| Deployment | Docker + Vercel (FE) + GCP Cloud Run (BE) + Cloud SQL | Simple, scalable, cost-effective |
| Dev Environment | Docker Compose | Everything runs locally with one command |
