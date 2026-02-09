# Scout — Epics & Stories

---

# Epic 1: Project Foundation & Infrastructure

**Goal:** Establish the development environment, project scaffolding, and local infrastructure so all subsequent work has a solid base to build on.

**Sprint:** 1 (Week 1)

---

### Story 1.1: Initialize Backend Project

**As a** developer,
**I want** a properly structured Python/FastAPI project with all dependencies configured,
**So that** I can immediately start building agent logic without setup friction.

**Acceptance Criteria:**
- Python 3.12+ project with `pyproject.toml` or `requirements.txt`
- FastAPI app skeleton with health check endpoint (`GET /api/v1/health`)
- Anthropic SDK installed and configured (reads API key from env)
- httpx, beautifulsoup4, structlog, pydantic v2 installed
- Async SQLAlchemy 2.0 + asyncpg installed
- pytest + pytest-asyncio configured with a sample passing test
- `.env.example` with all required environment variables documented
- App runs with `uvicorn app.main:app --reload`

---

### Story 1.2: Initialize Frontend Project

**As a** developer,
**I want** a Next.js project with TypeScript and Tailwind configured,
**So that** I can build the dashboard when the time comes without setup delays.

**Acceptance Criteria:**
- Next.js 14+ with App Router, TypeScript strict mode, Tailwind CSS
- Basic layout with navigation shell (sidebar or top nav placeholder)
- Home page with placeholder text
- `lib/api.ts` with a typed fetch wrapper pointing to `NEXT_PUBLIC_API_URL`
- `lib/types.ts` with initial shared type definitions
- App runs with `npm run dev`

---

### Story 1.3: Docker Compose Local Dev Environment

**As a** developer,
**I want** a single `docker-compose up` command that starts the backend, frontend, and PostgreSQL,
**So that** the full stack runs locally with no manual setup.

**Acceptance Criteria:**
- `docker-compose.yml` at project root with three services: `backend`, `frontend`, `db`
- PostgreSQL 16 with persistent volume, pre-configured database `scout`
- Backend auto-reloads on code changes (volume mount + uvicorn --reload)
- Frontend auto-reloads on code changes (volume mount)
- All services start successfully with `docker-compose up`
- README.md documents how to start and stop the environment

---

### Story 1.4: Database Schema & Migrations

**As a** developer,
**I want** the core database tables created via Alembic migrations,
**So that** agents and API endpoints can persist data from Sprint 2 onward.

**Acceptance Criteria:**
- Alembic configured with async SQLAlchemy
- Initial migration creates all core tables:
  - `teams` (id, name, created_at)
  - `users` (id, team_id FK, name, email, password_hash, created_at)
  - `company_profiles` (id, team_id FK, company_name, industry, created_at, updated_at)
  - `initiatives` (id, company_profile_id FK, name, description, status, discovered_by_agent, created_at, updated_at)
  - `research_sessions` (id, initiative_id FK, triggered_by FK, status, started_at, completed_at)
  - `research_cycles` (id, research_session_id FK, cycle_number, prime_agent_plan JSONB, confidence_assessment JSONB, started_at, completed_at)
  - `research_paths` (id, research_cycle_id FK, assignment_id, topic, status, reasoning, started_at, completed_at)
  - `research_findings` (id, research_path_id FK, initiative_id FK, category enum, content JSONB, source_url, source_type, confidence_score, created_at)
  - `synthesized_intelligence` (id, initiative_id FK, category, structured_content JSONB, confidence_score, last_updated_cycle_id, created_at, updated_at)
  - `dashboard_content` (id, initiative_id FK, content JSONB, portfolio_recommendations JSONB, created_at, updated_at)
  - `portfolio` (id, team_id FK, vendor_name, partnership_level, capabilities JSONB, created_at, updated_at)
- `alembic upgrade head` runs cleanly from empty database
- `db/queries.py` has basic CRUD functions for company_profiles and initiatives

---

# Epic 2: Research Tools

**Goal:** Build the tool functions that Research Sub-Agents use to gather information from the internet. Each tool is a self-contained async function with a defined schema.

**Sprint:** 1 (Week 1)

---

### Story 2.1: Tool Base Interface

**As a** developer,
**I want** a consistent interface for all research tools,
**So that** adding new tools is standardized and the research agent can call any tool uniformly.

**Acceptance Criteria:**
- `agents/tools/base.py` defines:
  - A `Tool` base class or protocol with `name`, `description`, `schema` (Anthropic tool JSON schema), and `async execute(**kwargs) -> dict`
  - A `ToolRegistry` that collects all available tools and returns them as a list of Anthropic tool definitions
  - A `run_tool(tool_name, kwargs)` dispatcher function
- Error handling: if a tool raises an exception, `run_tool` returns `{"error": "...", "tool": "..."}` instead of propagating
- Timeout handling: tools have a configurable timeout (default 15s)
- All tools log their invocation and result summary via structlog

---

### Story 2.2: Web Search Tool (Brave Search API)

**As a** Research Sub-Agent,
**I want** to search the web for information about companies and topics,
**So that** I can discover relevant pages, articles, and resources.

**Acceptance Criteria:**
- `agents/tools/web_search.py` implements the Tool interface
- Calls Brave Search API (`https://api.search.brave.com/res/v1/web/search`)
- Accepts parameters: `query` (string), `count` (int, default 10)
- Returns structured results: list of `{title, url, description, age}` dicts
- Handles API errors gracefully (rate limits, timeouts, invalid responses)
- Strips out irrelevant results (ads, spam) where possible
- Tool schema defined for Anthropic tool use format
- Unit test with mocked API response

---

### Story 2.3: Web Scrape Tool

**As a** Research Sub-Agent,
**I want** to fetch and extract readable content from a specific web page,
**So that** I can get detailed information from pages found via search.

**Acceptance Criteria:**
- `agents/tools/web_scrape.py` implements the Tool interface
- Uses httpx (async) to fetch the page with reasonable headers (User-Agent, Accept)
- Uses BeautifulSoup to extract main content, stripping nav, footer, ads, scripts
- Accepts parameters: `url` (string), `extract_type` (enum: "full_text", "structured") 
- Returns: `{url, title, content (truncated to ~4000 tokens), meta_description, headings[]}`
- Handles common failures: timeouts, 403/404, SSL errors, non-HTML content types
- Respects robots.txt (best effort — check for Disallow on the path)
- Content is truncated intelligently (not mid-sentence) to avoid exceeding context limits
- Unit test with mocked HTTP response

---

### Story 2.4: SEC Filings Tool

**As a** Research Sub-Agent,
**I want** to search and retrieve SEC filing data for public companies,
**So that** I can find financial signals, strategic priorities, and executive commentary.

**Acceptance Criteria:**
- `agents/tools/sec_filings.py` implements the Tool interface
- Uses SEC EDGAR full-text search API (`https://efts.sec.gov/LATEST/search-index?q=...`)
- Accepts parameters: `company_name` (string), `filing_type` (optional: "10-K", "10-Q", "8-K"), `query` (optional keyword within filings)
- Returns: list of `{filing_type, date, company, description, url, relevant_excerpt}` dicts
- Extracts relevant excerpts rather than returning full filing text
- Handles: company name variations, no results found, API rate limits
- Follows SEC EDGAR fair use policy (User-Agent with contact email, reasonable rate)
- Unit test with mocked API response

---

### Story 2.5: News Search Tool

**As a** Research Sub-Agent,
**I want** to search for recent news articles about a company or topic,
**So that** I can find current events, press releases, and announcements.

**Acceptance Criteria:**
- `agents/tools/news_search.py` implements the Tool interface
- Uses Brave Search API with `news` search type
- Accepts parameters: `query` (string), `count` (int, default 10), `freshness` (optional: "past_day", "past_week", "past_month")
- Returns: list of `{title, url, source, published_date, description}` dicts
- Sorted by recency
- Unit test with mocked API response

---

### Story 2.6: Job Postings Tool

**As a** Research Sub-Agent,
**I want** to find job postings from a target company,
**So that** I can infer their technology stack, team structure, priorities, and growth areas.

**Acceptance Criteria:**
- `agents/tools/job_postings.py` implements the Tool interface
- Strategy: Use Brave Search to find "[company name] careers" or "[company name] jobs [topic]", then scrape the results
- Accepts parameters: `company_name` (string), `keywords` (optional list of strings to filter by, e.g., ["cloud", "Azure", "migration"])
- Returns: list of `{title, department, location, description_excerpt, source_url, date_posted}` dicts
- Extracts key signals from descriptions: technologies mentioned, seniority level, team/division
- Handles: no results, career pages that require JS (flag for Playwright fallback)
- Unit test with mocked responses

---

# Epic 3: Multi-Agent Research Engine

**Goal:** Build the core agentic research loop — the Prime Agent, Research Sub-Agents, Synthesis Agent, and the orchestrator that manages the cycle.

**Sprint:** 1 (Week 1) — this is the most critical epic

---

### Story 3.1: Agent Prompt Engineering — Prime Agent

**As a** developer,
**I want** a well-crafted system prompt for the Prime Agent,
**So that** it produces high-quality research plans with focused, parallelizable assignments.

**Acceptance Criteria:**
- `agents/prompts/prime.py` exports a `build_prime_prompt(company, industry, initiative, prior_intelligence, cycle_number)` function
- System prompt instructs the Prime Agent to:
  - Analyze the research target and break it into discrete topics
  - Create up to 5 focused assignments for sub-agents
  - Each assignment has: id, topic, specific instructions, suggested tools, priority
  - Assess confidence per category (people, initiative, technology, competitive, financial)
  - Signal when it believes research is complete (diminishing returns)
  - Surface any discovered initiatives with a recommendation to investigate
  - Output valid JSON matching a defined schema
- Prompt includes the intelligence categories and what "good" looks like for each
- Prompt includes examples of well-formed assignments
- Prompt evolves — mark it clearly as v1 with a version comment

---

### Story 3.2: Agent Prompt Engineering — Research Sub-Agent

**As a** developer,
**I want** a well-crafted system prompt for Research Sub-Agents,
**So that** they execute focused research assignments effectively and return structured findings.

**Acceptance Criteria:**
- `agents/prompts/research.py` exports a `build_research_prompt(assignment)` function
- System prompt instructs the Research Sub-Agent to:
  - Focus exclusively on the assigned topic
  - Use available tools strategically (budget of 8–10 tool calls)
  - Return structured findings: content, source_url, source_type, confidence, category_hint
  - Flag tangential signals that might be relevant to the Prime Agent
  - Report when a topic is exhausted (no more useful information available)
  - Output valid JSON matching a defined schema
- Prompt includes the specific assignment details (topic, instructions, suggested tools)

---

### Story 3.3: Agent Prompt Engineering — Synthesis Agent

**As a** developer,
**I want** a well-crafted system prompt for the Synthesis Agent,
**So that** it merges raw findings into a coherent, categorized intelligence profile.

**Acceptance Criteria:**
- `agents/prompts/synthesis.py` exports a `build_synthesis_prompt(raw_findings, prior_intelligence)` function
- System prompt instructs the Synthesis Agent to:
  - Merge new findings with existing intelligence (avoid duplicates)
  - Categorize each finding into: People, Initiative Status, Technology, Competitive, Financial, Market
  - Resolve contradictions with reasoning (e.g., "Source A says X, Source B says Y — most likely Z because...")
  - Assess confidence per category on a scale (none, low, medium, high, sufficient)
  - Identify remaining gaps that warrant further research
  - Flag any newly discovered initiatives
  - Output valid JSON matching a defined schema

---

### Story 3.4: Agent Prompt Engineering — Presentation Agent

**As a** developer,
**I want** a well-crafted system prompt for the Presentation Agent,
**So that** it produces dashboard-ready content that is actionable for sellers.

**Acceptance Criteria:**
- `agents/prompts/presentation.py` exports a `build_presentation_prompt(structured_intelligence, portfolio)` function
- System prompt instructs the Presentation Agent to:
  - Transform structured intelligence into human-readable summaries per category
  - Generate "so what?" insights for sellers (actionable takeaways)
  - Highlight the best conversation starters and angles of approach
  - Map findings to portfolio capabilities where relevant
  - Write in the language of a sales briefing, not an academic report
  - Output valid JSON matching the dashboard content schema

---

### Story 3.5: Research Sub-Agent Runner

**As a** developer,
**I want** a function that executes a single Research Sub-Agent from assignment to findings,
**So that** the orchestrator can dispatch multiple sub-agents in parallel.

**Acceptance Criteria:**
- `agents/research_agent.py` implements `async def run_research_agent(assignment: Assignment, tools: ToolRegistry) -> SubAgentResult`
- Creates a conversation with Claude using the research system prompt + assignment
- Executes the conversation loop: Claude responds → if tool calls, execute tools → add results → repeat
- Respects tool call budget (8–10 max) — forcefully stops if exceeded
- Handles Claude API errors (rate limits, timeouts) with retries (3 attempts, exponential backoff)
- Returns structured `SubAgentResult` with findings, tangential_signals, tools_used, exhausted flag
- Logs every tool call and its result summary
- Supports cancellation via an `asyncio.Event` (checked between tool calls)

---

### Story 3.6: Prime Agent Runner

**As a** developer,
**I want** a function that runs the Prime Agent to produce a research plan,
**So that** the orchestrator knows what to research each cycle.

**Acceptance Criteria:**
- `agents/prime_agent.py` implements `async def run_prime_agent(company, industry, initiative, prior_intelligence, cycle_number) -> ResearchPlan`
- Calls Claude with the prime system prompt and extended thinking enabled
- Parses the JSON response into a `ResearchPlan` Pydantic model containing:
  - `cycle` (int)
  - `reasoning` (string)
  - `assignments` (list of Assignment, max 5)
  - `discovered_initiatives` (list)
  - `confidence_assessment` (dict of category → level)
  - `should_stop` (bool)
- Validates the response — if JSON parsing fails, retries once with a clarifying message
- Logs the plan summary

---

### Story 3.7: Synthesis Agent Runner

**As a** developer,
**I want** a function that runs the Synthesis Agent to merge and categorize findings,
**So that** raw research data becomes structured intelligence.

**Acceptance Criteria:**
- `agents/synthesis_agent.py` implements `async def run_synthesis_agent(raw_findings: list[SubAgentResult], prior_intelligence: dict | None) -> SynthesizedIntelligence`
- Calls Claude with the synthesis system prompt and extended thinking enabled
- Input includes all raw findings from the current cycle + any prior intelligence
- Returns structured `SynthesizedIntelligence` Pydantic model with:
  - Categorized findings (people, initiative, technology, competitive, financial, market)
  - Confidence assessment per category
  - Identified gaps
  - Discovered initiatives
- Handles large inputs — if findings exceed context limits, summarizes before sending

---

### Story 3.8: Presentation Agent Runner

**As a** developer,
**I want** a function that runs the Presentation Agent to format intelligence for the dashboard,
**So that** users see readable, actionable content.

**Acceptance Criteria:**
- `agents/presentation_agent.py` implements `async def run_presentation_agent(intelligence: SynthesizedIntelligence, portfolio: list[PortfolioItem] | None) -> DashboardContent`
- Calls Claude with the presentation system prompt (no extended thinking)
- Returns `DashboardContent` Pydantic model with:
  - Per-category summaries (markdown-formatted text)
  - Key insights list
  - Conversation starters for sellers
  - Portfolio recommendations (if portfolio data provided)
- Output is ready to be serialized and sent to the frontend

---

### Story 3.9: Orchestrator — Full Cycle Loop

**As a** developer,
**I want** the orchestrator to manage the complete research cycle from start to finish,
**So that** a single function call runs the entire multi-agent research process.

**Acceptance Criteria:**
- `agents/orchestrator.py` implements `async def run_research_session(company, industry, initiative, event_callback)`
- Manages the loop:
  1. Run Prime Agent → get research plan
  2. Dispatch up to 5 Research Sub-Agents in parallel via `asyncio.gather`
  3. Collect results, run Synthesis Agent
  4. Run Presentation Agent
  5. Call `event_callback` with dashboard update
  6. Check: did Prime Agent signal stop? Two consecutive low-value cycles? Max cycles reached?
  7. If not done, pass synthesized intelligence back to Prime Agent and repeat
- Maximum cycle count: 6 (configurable, safety limit)
- Dashboard updates emitted after every cycle (not every other — changed from initial spec for v0.1 simplicity)
- Handles individual sub-agent failures gracefully (continue with remaining results)
- Supports per-path cancellation via a shared `stop_signals` dict
- Logs cycle-level metrics: duration, findings count, confidence progression
- Can be run standalone from CLI for testing: `python -m app.agents.orchestrator "Company" "Industry" "Initiative"`

---

# Epic 4: API Layer

**Goal:** Expose the research engine and data through RESTful API endpoints with SSE streaming.

**Sprint:** 2 (Week 2)

---

### Story 4.1: Research Session Endpoints

**As a** frontend developer,
**I want** API endpoints to start, monitor, and control research sessions,
**So that** the dashboard can trigger and interact with the research engine.

**Acceptance Criteria:**
- `POST /api/v1/research/start` — accepts `{company_name, industry, initiative_description}`, creates session, returns `{session_id, status}`
- `GET /api/v1/research/{session_id}` — returns current session state including latest dashboard content, cycle count, status
- `GET /api/v1/research/{session_id}/findings` — returns all findings for the session, filterable by `?category=people`
- `POST /api/v1/research/{session_id}/stop` — stops the entire research session gracefully
- `POST /api/v1/research/{session_id}/paths/{path_id}/stop` — stops a specific research sub-agent path
- `POST /api/v1/research/{session_id}/follow-up` — accepts `{question}`, triggers a new research cycle focused on the question
- All endpoints return consistent response envelope
- Research session start spawns the orchestrator as a background async task
- All endpoints validate inputs and return appropriate HTTP status codes

---

### Story 4.2: SSE Streaming Endpoint

**As a** frontend developer,
**I want** a Server-Sent Events stream for a research session,
**So that** the dashboard updates in real-time as agents work.

**Acceptance Criteria:**
- `GET /api/v1/research/{session_id}/stream` — returns an SSE stream
- Event types defined in `streams/events.py`:
  - `cycle_started` — `{cycle_number, plan_summary}`
  - `subagent_started` — `{path_id, topic, priority}`
  - `subagent_completed` — `{path_id, topic, findings_count, tangential_signals}`
  - `subagent_stopped` — `{path_id, topic, reason: "user" | "budget" | "error"}`
  - `synthesis_complete` — `{confidence_assessment, gaps, discovered_initiatives}`
  - `findings_updated` — `{dashboard_content}` (full updated dashboard payload)
  - `initiative_discovered` — `{initiative_name, description, evidence}`
  - `research_complete` — `{total_cycles, total_findings, final_confidence}`
  - `error` — `{message, recoverable}`
- Stream stays open for the duration of the research session
- Multiple clients can connect to the same session stream (for team collaboration)
- Stream sends a heartbeat ping every 30 seconds to prevent connection timeout
- Connection handles client disconnects gracefully

---

### Story 4.3: Company Profile Endpoints

**As a** frontend developer,
**I want** API endpoints to manage company profiles and their initiatives,
**So that** the dashboard can display and navigate company intelligence.

**Acceptance Criteria:**
- `GET /api/v1/companies` — list all company profiles for the user's team, with pagination
- `GET /api/v1/companies/{id}` — get company profile with all its initiatives
- `GET /api/v1/companies/{id}/initiatives` — list initiatives for a company
- `GET /api/v1/companies/{id}/initiatives/{init_id}` — get initiative with latest dashboard content and research history
- `DELETE /api/v1/companies/{id}` — soft delete a company profile
- `POST /api/v1/companies/{id}/initiatives/{init_id}/refresh` — trigger a new research session for an existing initiative
- Companies are scoped to the user's team

---

### Story 4.4: Portfolio Management Endpoints

**As a** frontend developer,
**I want** API endpoints to manage the team's vendor portfolio,
**So that** portfolio mapping can work in the Presentation Agent.

**Acceptance Criteria:**
- `GET /api/v1/portfolio` — list all portfolio entries for the user's team
- `POST /api/v1/portfolio` — add a portfolio entry: `{vendor_name, partnership_level, capabilities: [...]}`
- `PUT /api/v1/portfolio/{id}` — update a portfolio entry
- `DELETE /api/v1/portfolio/{id}` — delete a portfolio entry
- `POST /api/v1/portfolio/bulk` — bulk import portfolio from JSON (for initial setup)
- Portfolio data is passed to the Presentation Agent during research sessions

---

### Story 4.5: Persist Research Results to Database

**As a** developer,
**I want** the orchestrator to save all research data to PostgreSQL as it runs,
**So that** results survive server restarts and can be retrieved by the API.

**Acceptance Criteria:**
- Orchestrator creates `research_session` record when starting
- Each cycle creates a `research_cycle` record with the Prime Agent's plan and confidence assessment
- Each sub-agent assignment creates a `research_path` record (status updates as it progresses)
- Each finding creates a `research_finding` record with category, content, source, confidence
- Synthesis creates/updates `synthesized_intelligence` records per category per initiative
- Presentation creates/updates `dashboard_content` record for the initiative
- All writes use async SQLAlchemy with proper transaction boundaries
- If the orchestrator crashes mid-session, the session status reflects this (`status = "failed"`)

---

# Epic 5: Dashboard MVP

**Goal:** Build the frontend dashboard where sellers interact with Scout — input research targets, watch agents work, browse findings, and ask follow-up questions.

**Sprint:** 3 (Week 3)

---

### Story 5.1: Research Input Form

**As a** seller,
**I want** a simple form to start a new research session,
**So that** I can tell Scout what company and initiative to investigate.

**Acceptance Criteria:**
- Form with three fields: Company Name (text), Industry (text or dropdown), Initiative/Project (textarea)
- Initiative field has helper text: "Can be vague — e.g., 'I heard they're doing something with cloud'"
- Submit button calls `POST /api/v1/research/start`
- On success, redirects to the research session view
- Form validates: company name and initiative are required, industry is optional but encouraged
- Clean, professional UI — no clutter

---

### Story 5.2: Research Status Panel

**As a** seller,
**I want** to see what the research agents are doing in real-time,
**So that** I understand the progress and can control the research.

**Acceptance Criteria:**
- Connects to SSE stream for the active research session
- Shows current cycle number and total elapsed time
- Lists all active research sub-agents with:
  - Topic name
  - Status indicator (running spinner, completed checkmark, stopped icon)
  - Stop button (calls `POST /api/v1/research/{session_id}/paths/{path_id}/stop`)
- Shows Prime Agent's confidence assessment per category (progress bars or simple indicators)
- Shows a "Stop All Research" button
- Updates in real-time as SSE events arrive
- Handles disconnection gracefully (auto-reconnect with backoff)

---

### Story 5.3: Findings Dashboard — Category Panels

**As a** seller,
**I want** to browse research findings organized by category,
**So that** I can quickly find the intelligence I need for my conversation.

**Acceptance Criteria:**
- Dashboard displays categorized panels:
  - **People** — key contacts with names, titles, roles, relevant context
  - **Initiative Status** — what the initiative is, current state, timeline signals
  - **Technology** — what tech they're using or evaluating, stack signals
  - **Competitive Landscape** — what competitors and alternative vendors are doing
  - **Financial Signals** — budget indicators, earnings mentions, procurement signals
- Each panel shows the Presentation Agent's summary at the top, with expandable detailed findings below
- Each finding shows: content, source (linked), confidence indicator
- Panels show a confidence indicator (from the Synthesis Agent's assessment)
- Panels update in real-time when `findings_updated` SSE event arrives
- Empty panels show "No intelligence gathered yet" with appropriate context

---

### Story 5.4: Portfolio Recommendations Panel

**As a** seller,
**I want** to see how research findings map to my company's capabilities,
**So that** I know what solutions and services to lead with.

**Acceptance Criteria:**
- Panel displays the Presentation Agent's portfolio recommendations
- Shows: recommended vendor solutions, relevant service capabilities, suggested positioning
- Each recommendation links back to the findings that support it
- If no portfolio is configured, shows a prompt to set up portfolio in settings
- Panel updates when new `findings_updated` events include portfolio recommendations

---

### Story 5.5: Discovered Initiatives Component

**As a** seller,
**I want** to be notified when the agent discovers initiatives I didn't ask about,
**So that** I can expand my research to new opportunities.

**Acceptance Criteria:**
- When `initiative_discovered` SSE event arrives, show a notification/banner
- Banner shows: initiative name, brief description, evidence (why the agent thinks this exists)
- Two action buttons: "Research This" (creates new initiative + starts research) and "Dismiss"
- Dismissed initiatives don't reappear
- Accepted initiatives appear in the company's initiative list

---

### Story 5.6: Follow-Up Question Input

**As a** seller,
**I want** to ask follow-up questions that trigger more research,
**So that** I can dig deeper into specific areas.

**Acceptance Criteria:**
- Text input at the bottom of the dashboard (or top): "Ask a follow-up question..."
- Submit calls `POST /api/v1/research/{session_id}/follow-up` with the question
- Triggers a new research cycle — the Research Status Panel activates again
- New findings merge into existing dashboard panels
- Previous follow-up questions are visible as a history/log
- Input is disabled while a research cycle is actively running (to avoid race conditions in v0.1)

---

### Story 5.7: Company Profile Page

**As a** seller,
**I want** a page showing a company's profile with all its initiatives,
**So that** I can navigate between different research threads for the same account.

**Acceptance Criteria:**
- Displays company name, industry
- Lists all initiatives (both user-created and agent-discovered)
- Each initiative shows: name, status, last researched date, confidence summary
- Clicking an initiative navigates to its dashboard view
- "New Initiative" button to start research on a new initiative for this company
- "Refresh" button on each initiative to trigger a new research session

---

### Story 5.8: SSE Connection Hook

**As a** frontend developer,
**I want** a reusable React hook for SSE connections,
**So that** any component can subscribe to research session events.

**Acceptance Criteria:**
- `hooks/useResearchStream.ts` implements:
  - `useResearchStream(sessionId: string)` returns `{status, events, latestDashboard, activePaths, confidence}`
  - Connects to `GET /api/v1/research/{session_id}/stream`
  - Parses SSE events and updates state
  - Auto-reconnects on disconnection (3 attempts, exponential backoff)
  - Cleans up EventSource on unmount
  - Exposes `isConnected` boolean
- Type-safe event handling with discriminated unions for event types

---

# Epic 6: Authentication & Collaboration

**Goal:** Add simple authentication and team-based access so multiple sellers can share and collaborate on company intelligence.

**Sprint:** 4 (Week 4)

---

### Story 6.1: User Registration & Login (Backend)

**As a** user,
**I want** to create an account and log in,
**So that** my research is saved and scoped to my team.

**Acceptance Criteria:**
- `POST /api/v1/auth/register` — accepts `{name, email, password, team_name}`. Creates user + team. Returns JWT.
- `POST /api/v1/auth/login` — accepts `{email, password}`. Returns JWT.
- `GET /api/v1/auth/me` — returns current user info (requires valid JWT)
- Passwords hashed with bcrypt
- JWT tokens expire after 7 days
- All non-auth endpoints require valid JWT in Authorization header
- All data queries are scoped to `user.team_id`

---

### Story 6.2: Team & User Management

**As a** team admin,
**I want** to invite teammates to my team,
**So that** we can collaborate on the same company profiles.

**Acceptance Criteria:**
- `POST /api/v1/teams/invite` — accepts `{email}`, creates an invite (for v0.1: auto-creates user with temporary password, sends to stdout/log)
- `GET /api/v1/teams/members` — lists team members
- New users joining via invite are added to the existing team
- All company profiles, initiatives, and research are shared across the team
- Cap team size at 4 members for v0.1

---

### Story 6.3: Login & Auth UI (Frontend)

**As a** user,
**I want** a login and registration page,
**So that** I can access Scout.

**Acceptance Criteria:**
- `/login` page with email + password form
- `/register` page with name + email + password + team name form
- JWT stored in httpOnly cookie or localStorage (v0.1: localStorage is fine)
- `AuthContext` provider wraps the app, provides `user`, `login`, `logout`, `isAuthenticated`
- Protected routes redirect to `/login` if not authenticated
- User's name displayed in navigation

---

# Epic 7: Portfolio Management

**Goal:** Allow teams to configure their vendor partnerships and service capabilities so Scout can map research findings to the team's portfolio.

**Sprint:** 4 (Week 4)

---

### Story 7.1: Portfolio Configuration Page

**As a** team member,
**I want** a page to manage my company's vendor portfolio,
**So that** Scout can recommend relevant solutions when researching target companies.

**Acceptance Criteria:**
- `/portfolio` page with a list of portfolio entries
- Each entry shows: vendor name, partnership level, capabilities
- "Add Vendor" form: vendor name (text), partnership level (dropdown: Partner, Gold, Platinum, Premier, etc.), capabilities (multi-line text or tags)
- Edit and delete existing entries
- "Bulk Import" option: paste or upload JSON with multiple entries
- Portfolio data is persisted via the API and shared across the team

---

### Story 7.2: Wire Portfolio into Presentation Agent

**As a** developer,
**I want** the Presentation Agent to receive portfolio data during research,
**So that** it can generate portfolio mapping recommendations.

**Acceptance Criteria:**
- Orchestrator loads the team's portfolio from the database before running the Presentation Agent
- Portfolio data is passed into the Presentation Agent's prompt
- Presentation Agent output includes a `portfolio_recommendations` section
- Recommendations reference specific portfolio entries (vendor + capability) matched to findings
- If no portfolio is configured, Presentation Agent skips this section and notes it in the output

---

# Epic 8: Initiative Discovery & Multi-Initiative Tracking

**Goal:** Enable the agent to discover initiatives the user didn't know about, surface them for confirmation, and track multiple initiatives per company.

**Sprint:** 4 (Week 4)

---

### Story 8.1: Initiative Discovery in Prime Agent

**As a** developer,
**I want** the Prime Agent to identify and surface undiscovered initiatives,
**So that** sellers find opportunities they didn't know about.

**Acceptance Criteria:**
- Prime Agent system prompt includes explicit instructions to watch for signals of other initiatives
- When the Prime Agent identifies a potential initiative, it includes it in `discovered_initiatives` with:
  - Name/description
  - Evidence (what signals point to this)
  - Recommended research approach
- Orchestrator emits `initiative_discovered` SSE event for each discovery
- Discoveries are NOT automatically researched — they wait for user confirmation

---

### Story 8.2: Confirm or Dismiss Discovered Initiatives

**As a** seller,
**I want** to confirm or dismiss discovered initiatives from the dashboard,
**So that** I control what Scout researches.

**Acceptance Criteria:**
- `POST /api/v1/companies/{id}/initiatives/confirm-discovery` — accepts `{name, description}`, creates initiative with `discovered_by_agent = true`, optionally starts research
- Frontend `DiscoveredInitiatives` component (Story 5.5) wired to this endpoint
- "Research This" starts a new research session for the discovered initiative
- "Dismiss" marks the discovery as dismissed (not shown again)
- Confirmed initiatives appear in the company's initiative list alongside user-created ones

---

# Epic 9: Error Handling, Resilience & Polish

**Goal:** Make the system robust enough for real users — handle failures gracefully, provide good error messages, and polish the UX.

**Sprint:** 4 (Week 4)

---

### Story 9.1: Agent Error Handling & Recovery

**As a** developer,
**I want** the orchestrator to handle agent and tool failures gracefully,
**So that** a single failure doesn't crash the entire research session.

**Acceptance Criteria:**
- If a Research Sub-Agent fails (API error, timeout), the orchestrator:
  - Logs the error with full context
  - Continues with remaining sub-agent results
  - Notes the failure in the cycle record
  - Emits `subagent_stopped` event with `reason: "error"`
- If the Prime Agent fails, the orchestrator retries once, then stops the session with `status: "failed"`
- If the Synthesis Agent fails, retry once, then use raw findings directly (skip synthesis)
- If all sub-agents in a cycle fail, stop the session with appropriate error message
- All Anthropic API calls use retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)
- Tool timeouts are enforced (15s default) — timed-out tools return error results, not exceptions

---

### Story 9.2: Frontend Error States & Loading States

**As a** seller,
**I want** clear feedback when things are loading or when errors occur,
**So that** I'm never confused about what's happening.

**Acceptance Criteria:**
- Research input form shows loading spinner on submit
- Research status panel shows "Connecting..." state before SSE connects
- Dashboard panels show skeleton loading states while research is in progress
- If SSE disconnects, show a banner: "Connection lost. Reconnecting..." with auto-retry
- If research session fails, show clear error message with "Try Again" button
- Empty states for each panel when no data exists yet
- Toast notifications for important events (research complete, initiative discovered, error)

---

### Story 9.3: Rate Limiting & API Key Management

**As a** developer,
**I want** proper rate limiting and API key handling,
**So that** we don't exceed API quotas or expose secrets.

**Acceptance Criteria:**
- Brave Search API calls are rate-limited (client-side) to avoid hitting quota
- Anthropic API calls respect rate limits with backoff
- SEC EDGAR calls include proper User-Agent and respect fair use guidelines
- All API keys loaded from environment variables via Pydantic Settings
- No API keys in code, logs, or error messages
- `.env.example` documents all required keys with descriptions

---

# Epic 10: Deployment

**Goal:** Deploy Scout to GCP so the pilot users can access it.

**Sprint:** 4 (Week 4)

---

### Story 10.1: Backend Deployment (GCP)

**As a** developer,
**I want** the backend deployed to GCP,
**So that** pilot users can access Scout from anywhere.

**Acceptance Criteria:**
- Backend containerized with Docker (production Dockerfile with multi-stage build)
- Container image pushed to Google Artifact Registry
- Deployed to GCP Cloud Run (fully managed, scales to zero when idle)
- Cloud SQL for PostgreSQL instance provisioned (or free-tier Neon/Supabase for cost savings)
- Environment variables and API keys configured via GCP Secret Manager
- Health check endpoint verified
- HTTPS enabled (automatic with Cloud Run)
- Basic logging to Google Cloud Logging (automatic with Cloud Run)

---

### Story 10.2: Frontend Deployment (Vercel)

**As a** developer,
**I want** the frontend deployed to Vercel,
**So that** pilot users can access the dashboard.

**Acceptance Criteria:**
- Next.js app deployed to Vercel (connect GitHub repo)
- Environment variable `NEXT_PUBLIC_API_URL` points to the deployed backend
- Custom domain optional (Vercel default URL is fine for pilot)
- Automatic deployments on push to main branch

---

### Story 10.3: End-to-End Smoke Test

**As a** developer,
**I want** to verify the full system works end-to-end in production,
**So that** I'm confident before handing it to pilot users.

**Acceptance Criteria:**
- Register a new user and team
- Add 2-3 portfolio entries
- Start a research session for a well-known public company with a known initiative
- Verify: SSE stream connects, sub-agents run, findings appear on dashboard
- Ask a follow-up question, verify new cycle runs
- Verify data persists (refresh page, findings still there)
- Test with 2 users on the same team viewing the same profile simultaneously
- Document any known issues or limitations for pilot users

---

# Story Priority & Sprint Mapping Summary

| Sprint | Week | Epics | Focus |
|--------|------|-------|-------|
| **Sprint 1** | Week 1 | Epic 1 (Foundation), Epic 2 (Tools), Epic 3 (Agent Engine) | Get the multi-agent research loop working end-to-end in the terminal |
| **Sprint 2** | Week 2 | Epic 4 (API Layer) | Persist data, expose via REST + SSE, wire orchestrator to database |
| **Sprint 3** | Week 3 | Epic 5 (Dashboard MVP) | Build the frontend — input, real-time status, findings dashboard, follow-ups |
| **Sprint 4** | Week 4 | Epic 6 (Auth), Epic 7 (Portfolio), Epic 8 (Discovery), Epic 9 (Polish), Epic 10 (Deploy) | Auth, collaboration, portfolio mapping, error handling, deploy for pilot |

---

# Total Story Count

| Epic | Stories | Sprint |
|------|---------|--------|
| Epic 1: Foundation | 4 | 1 |
| Epic 2: Tools | 6 | 1 |
| Epic 3: Agent Engine | 9 | 1 |
| Epic 4: API Layer | 5 | 2 |
| Epic 5: Dashboard MVP | 8 | 3 |
| Epic 6: Auth & Collaboration | 3 | 4 |
| Epic 7: Portfolio | 2 | 4 |
| Epic 8: Initiative Discovery | 2 | 4 |
| Epic 9: Error Handling & Polish | 3 | 4 |
| Epic 10: Deployment | 3 | 4 |
| **Total** | **45 stories** | **4 sprints** |
