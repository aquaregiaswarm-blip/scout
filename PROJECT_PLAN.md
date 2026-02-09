# Scout — Project Plan

## Overview

**Scout** is an agentic sales intelligence platform for VAR/SI sales teams.  
**Timeline:** Accelerated 3-week sprint  
**Pilot:** 6 users (3 groups of 2)  
**Domain:** scout.aquaregia.life

---

## Critical Dependencies & Blockers

### Blockers (Must Resolve Before Starting)

| # | Blocker | Owner | Status | Resolution |
|---|---------|-------|--------|------------|
| B1 | **Anthropic via Vertex AI setup** — Need to enable Claude on Vertex AI in GCP project | Doc | ⏳ Pending | Enable Vertex AI API, request Claude access |
| B2 | **Brave Search API key** — Required for web search tool | Doc | ✅ Has key | Add to GCP Secret Manager |
| B3 | **GCP Service Account permissions** — Need Vertex AI User role | AR | ⏳ Pending | Add role to deployer SA |

### Dependencies (External)

| # | Dependency | Required By | Notes |
|---|------------|-------------|-------|
| D1 | Claude access on Vertex AI | Sprint 1, Day 2 | Without this, no agent development |
| D2 | Brave API key configured | Sprint 1, Day 3 | Needed for web_search tool |
| D3 | Portfolio data from Doc | Sprint 2 | Can use researched Pellera data as fallback |

---

## Architecture Adjustments

### Claude via Vertex AI (Not Direct Anthropic API)

```python
# Instead of:
from anthropic import Anthropic
client = Anthropic(api_key="sk-ant-...")

# We use:
from anthropic import AnthropicVertex
client = AnthropicVertex(region="us-east1", project_id="prj-cts-lab-vertex-sandbox")

# Model name format:
model = "claude-sonnet-4@20250514"  # Not "claude-sonnet-4-5-20250514"
```

**Key differences:**
- Uses Google Cloud auth (ADC) instead of API key
- Model names have `@` instead of `-` before date
- Region-specific endpoints
- Billing through GCP, not Anthropic

---

## Sprint Plan (Accelerated: 3 Weeks)

### Sprint 1: Foundation + Agent Engine (Days 1-7)

**Goal:** Multi-agent research loop works end-to-end with persistence.

#### Day 1-2: Project Setup & Infrastructure

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **1.1 Initialize Backend** | | | |
| 1.1.1 Create FastAPI skeleton | Health endpoint, config | `test_health_endpoint()` | |
| 1.1.2 Configure Vertex AI client | AnthropicVertex setup | `test_vertex_connection()` | B1 |
| 1.1.3 Set up async SQLAlchemy | Database connection | `test_db_connection()` | |
| 1.1.4 Configure structlog | JSON logging | Manual verify | |
| **1.2 Initialize Frontend** | | | |
| 1.2.1 Create Next.js project | TypeScript, Tailwind | `npm run build` passes | |
| 1.2.2 Set up API client | Typed fetch wrapper | `test_api_types.ts` | |
| 1.2.3 Create layout shell | Navigation, auth placeholder | Visual check | |
| **1.3 Docker Compose** | | | |
| 1.3.1 Backend Dockerfile | Multi-stage build | `docker build` passes | |
| 1.3.2 Frontend Dockerfile | Next.js production | `docker build` passes | |
| 1.3.3 Compose file | All services start | `docker-compose up` works | |
| **1.4 Database Schema** | | | |
| 1.4.1 Create Alembic config | Async migrations | Migration runs | |
| 1.4.2 Define all tables | 12 tables per spec | Schema validates | |
| 1.4.3 Initial migration | `alembic upgrade head` | Migration succeeds | |
| 1.4.4 Basic query functions | CRUD for core entities | `test_queries.py` | |

**Day 1-2 Exit Criteria:**
- [ ] `docker-compose up` starts all services
- [ ] Backend health check returns 200
- [ ] Frontend loads at localhost:3000
- [ ] Database migrations run successfully
- [ ] Vertex AI connection test passes

#### Day 3-4: Research Tools

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **2.1 Tool Base Interface** | | | |
| 2.1.1 Define Tool protocol | Schema, execute interface | Type checks pass | |
| 2.1.2 Create ToolRegistry | Collect & dispatch tools | `test_tool_registry()` | |
| 2.1.3 Error/timeout handling | Graceful failures | `test_tool_timeout()` | |
| **2.2 Web Search Tool** | | | B2 |
| 2.2.1 Brave Search wrapper | Query, parse results | `test_web_search_mock()` | |
| 2.2.2 Rate limiting | Respect API limits | `test_rate_limit()` | |
| 2.2.3 Integration test | Real API call | `test_web_search_live()` | |
| **2.3 Web Scrape Tool** | | | |
| 2.3.1 httpx + BeautifulSoup | Fetch & extract | `test_scrape_mock()` | |
| 2.3.2 Content truncation | Smart truncation | `test_truncation()` | |
| 2.3.3 Error handling | 404, timeout, SSL | `test_scrape_errors()` | |
| **2.4 SEC Filings Tool** | | | |
| 2.4.1 EDGAR API client | Search filings | `test_sec_mock()` | |
| 2.4.2 Excerpt extraction | Relevant snippets | `test_sec_excerpts()` | |
| **2.5 News Search Tool** | | | |
| 2.5.1 Brave News wrapper | News-specific search | `test_news_mock()` | |
| **2.6 Job Postings Tool** | | | |
| 2.6.1 Career page scraper | Find & extract jobs | `test_jobs_mock()` | |

**Day 3-4 Exit Criteria:**
- [ ] All 5 tools implemented with mocked tests
- [ ] At least 2 tools verified with live API calls
- [ ] ToolRegistry correctly dispatches all tools
- [ ] Error handling verified for all failure modes

#### Day 5-7: Multi-Agent Engine

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **3.1 Agent Prompts** | | | |
| 3.1.1 Prime Agent prompt | Planning, delegation | Manual eval | |
| 3.1.2 Research Agent prompt | Focused execution | Manual eval | |
| 3.1.3 Synthesis Agent prompt | Merge, categorize | Manual eval | |
| 3.1.4 Presentation Agent prompt | Dashboard formatting | Manual eval | |
| **3.2 Agent Runners** | | | B1 |
| 3.2.1 Prime Agent runner | Plan generation | `test_prime_agent_mock()` | |
| 3.2.2 Research Agent runner | Tool execution loop | `test_research_agent_mock()` | |
| 3.2.3 Synthesis Agent runner | Findings merge | `test_synthesis_agent_mock()` | |
| 3.2.4 Presentation Agent runner | Content formatting | `test_presentation_agent_mock()` | |
| **3.3 Orchestrator** | | | |
| 3.3.1 Cycle loop manager | Run full cycle | `test_orchestrator_mock()` | |
| 3.3.2 Parallel dispatch | asyncio.gather | `test_parallel_agents()` | |
| 3.3.3 Stop signals | Per-path cancellation | `test_stop_signal()` | |
| 3.3.4 Persistence hooks | Save to DB as running | `test_persistence()` | |
| **3.4 Integration** | | | |
| 3.4.1 End-to-end CLI test | Full research run | `test_e2e_research()` | |
| 3.4.2 Multi-cycle test | 2-3 cycles complete | `test_multi_cycle()` | |

**Day 5-7 Exit Criteria:**
- [ ] `python -m app.agents.orchestrator "Acme Corp" "Tech" "cloud migration"` produces structured intelligence
- [ ] All 4 agents produce valid JSON output
- [ ] Parallel sub-agents execute correctly
- [ ] Results persist to database
- [ ] At least 2 real research cycles complete successfully

---

### Sprint 2: API + Dashboard (Days 8-14)

**Goal:** Full web UI with real-time SSE updates.

#### Day 8-9: API Layer

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **4.1 Research Endpoints** | | | |
| 4.1.1 POST /research/start | Create session | `test_start_research()` | |
| 4.1.2 GET /research/{id} | Get session state | `test_get_research()` | |
| 4.1.3 POST /research/{id}/stop | Stop session | `test_stop_research()` | |
| 4.1.4 POST /research/{id}/paths/{id}/stop | Stop path | `test_stop_path()` | |
| 4.1.5 POST /research/{id}/follow-up | Follow-up question | `test_follow_up()` | |
| **4.2 SSE Streaming** | | | |
| 4.2.1 Event types enum | All event types | Type checks | |
| 4.2.2 SSE endpoint | GET /research/{id}/stream | `test_sse_connection()` | |
| 4.2.3 Event emission | All event types fire | `test_sse_events()` | |
| 4.2.4 Multi-client support | Multiple connections | `test_sse_multi_client()` | |
| **4.3 Company Endpoints** | | | |
| 4.3.1 CRUD endpoints | List, get, delete | `test_company_crud()` | |
| 4.3.2 Initiative endpoints | Nested under company | `test_initiative_crud()` | |
| **4.4 Portfolio Endpoints** | | | |
| 4.4.1 CRUD endpoints | Manage portfolio | `test_portfolio_crud()` | |
| 4.4.2 Bulk import | JSON upload | `test_portfolio_bulk()` | |

#### Day 10-12: Dashboard Frontend

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **5.1 Research Input** | | | |
| 5.1.1 Input form component | Company, industry, initiative | Visual test | |
| 5.1.2 Form validation | Required fields | `test_form_validation()` | |
| 5.1.3 Submit handler | API call + redirect | E2E test | |
| **5.2 SSE Hook** | | | |
| 5.2.1 useResearchStream hook | Connect, parse, state | `test_sse_hook()` | |
| 5.2.2 Auto-reconnect | Backoff logic | `test_reconnect()` | |
| **5.3 Research Status** | | | |
| 5.3.1 Status panel component | Active paths, stop buttons | Visual test | |
| 5.3.2 Confidence indicators | Per-category progress | Visual test | |
| **5.4 Findings Dashboard** | | | |
| 5.4.1 Category panels | People, Tech, etc. | Visual test | |
| 5.4.2 FindingsCard component | Individual finding | Visual test | |
| 5.4.3 Real-time updates | SSE → UI updates | E2E test | |
| **5.5 Follow-up Input** | | | |
| 5.5.1 Question input | Text field + submit | Visual test | |
| 5.5.2 History display | Previous questions | Visual test | |
| **5.6 Company Profile Page** | | | |
| 5.6.1 Profile view | Company + initiatives | Visual test | |
| 5.6.2 Navigation | Between initiatives | E2E test | |

#### Day 13-14: Integration & Polish

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **6.1 E2E Integration** | | | |
| 6.1.1 Full flow test | Input → research → results | E2E Playwright | |
| 6.1.2 Follow-up flow | Ask question → new cycle | E2E Playwright | |
| 6.1.3 Multi-user test | 2 users same session | Manual test | |
| **6.2 Error Handling** | | | |
| 6.2.1 API error states | Toast notifications | Visual test | |
| 6.2.2 SSE disconnect | Reconnect banner | E2E test | |
| 6.2.3 Research failure | Error message + retry | E2E test | |

**Sprint 2 Exit Criteria:**
- [ ] Can start research from web UI
- [ ] SSE streams events in real-time
- [ ] Dashboard updates as agents work
- [ ] Can stop individual research paths
- [ ] Can ask follow-up questions
- [ ] All API endpoints have tests
- [ ] E2E tests pass

---

### Sprint 3: Auth, Portfolio, Deploy (Days 15-21)

**Goal:** Production-ready with auth and portfolio mapping.

#### Day 15-16: Authentication

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **7.1 Backend Auth** | | | |
| 7.1.1 User model + bcrypt | Password hashing | `test_password_hash()` | |
| 7.1.2 JWT generation | Token create/verify | `test_jwt()` | |
| 7.1.3 Register endpoint | Create user + team | `test_register()` | |
| 7.1.4 Login endpoint | Auth + return JWT | `test_login()` | |
| 7.1.5 Auth middleware | Protect routes | `test_auth_required()` | |
| 7.1.6 Team scoping | Data isolation | `test_team_scoping()` | |
| **7.2 Frontend Auth** | | | |
| 7.2.1 AuthContext | User state management | `test_auth_context()` | |
| 7.2.2 Login page | Form + validation | Visual test | |
| 7.2.3 Register page | Form + team creation | Visual test | |
| 7.2.4 Protected routes | Redirect if not auth | E2E test | |

#### Day 17-18: Portfolio & Discovery

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **8.1 Portfolio UI** | | | |
| 8.1.1 Portfolio page | List + add/edit/delete | Visual test | |
| 8.1.2 Bulk import | JSON upload | E2E test | |
| **8.2 Portfolio in Agents** | | | D3 |
| 8.2.1 Load portfolio | Pass to Presentation Agent | `test_portfolio_load()` | |
| 8.2.2 Mapping logic | Match findings → portfolio | `test_portfolio_mapping()` | |
| **8.3 Initiative Discovery** | | | |
| 8.3.1 Prime Agent discovery | Detect new initiatives | `test_discovery()` | |
| 8.3.2 Discovery SSE event | Surface to UI | E2E test | |
| 8.3.3 Confirm/dismiss UI | User actions | E2E test | |

#### Day 19-20: Deployment

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **9.1 Backend Deployment** | | | |
| 9.1.1 Production Dockerfile | Multi-stage, optimized | Build passes | |
| 9.1.2 Cloud Build config | Build + push to Artifact Registry | Build succeeds | |
| 9.1.3 Cloud Run deploy | Deploy with env vars | Service runs | |
| 9.1.4 Cloud SQL setup | PostgreSQL instance | Connection works | |
| 9.1.5 Secret Manager | All secrets configured | Secrets accessible | |
| **9.2 Frontend Deployment** | | | |
| 9.2.1 Vercel config | Environment variables | Deploy succeeds | |
| 9.2.2 Domain setup | scout.aquaregia.life | DNS works | |
| **9.3 Smoke Tests** | | | |
| 9.3.1 E2E production test | Full flow in prod | Manual test | |
| 9.3.2 Multi-user test | 2 users simultaneously | Manual test | |

#### Day 21: Buffer & Polish

| Task | Subtasks | Tests | Blocker |
|------|----------|-------|---------|
| **10.1 Final Polish** | | | |
| 10.1.1 Bug fixes | Issues from testing | Regression tests | |
| 10.1.2 Performance check | Latency, errors | Monitoring | |
| 10.1.3 Documentation | User guide for pilots | Doc review | |

**Sprint 3 Exit Criteria:**
- [ ] Users can register and login
- [ ] Teams share company profiles
- [ ] Portfolio mapping appears in results
- [ ] Initiative discovery works
- [ ] Deployed to GCP + Vercel
- [ ] 6 pilot users can access

---

## Test Strategy

### Unit Tests (pytest)
- Every agent runner
- Every tool function
- Every database query
- Every API endpoint handler
- **Coverage target:** 80%

### Integration Tests (pytest-asyncio)
- Orchestrator with mocked Claude
- API with real database
- SSE streaming end-to-end

### E2E Tests (Playwright)
- Full research flow
- Follow-up questions
- Auth flows
- Error states

### Regression Tests
- Run on every PR
- Block merge if failing

---

## Portfolio Data (Pellera)

Based on research, here's the initial portfolio structure:

```json
{
  "company": "Pellera Technologies",
  "description": "Premier IT solutions partner (Mainline + Converge merger)",
  "partners": [
    {"vendor": "IBM", "level": "Premier", "capabilities": ["Power Systems", "Storage", "Z Systems", "IP4G"]},
    {"vendor": "Dell Technologies", "level": "Titanium", "capabilities": ["PowerStore", "VxRail", "PowerEdge"]},
    {"vendor": "HPE", "level": "Platinum", "capabilities": ["ProLiant", "Synergy", "Storage"]},
    {"vendor": "VMware", "level": "Principal", "capabilities": ["vSphere", "NSX", "vSAN"]},
    {"vendor": "Red Hat", "level": "Premier", "capabilities": ["OpenShift", "RHEL", "Ansible"]},
    {"vendor": "Palo Alto Networks", "level": "Diamond", "capabilities": ["NGFW", "Prisma", "Cortex"]},
    {"vendor": "NetApp", "level": "Star", "capabilities": ["ONTAP", "Cloud Volumes"]},
    {"vendor": "Rubrik", "level": "Elite", "capabilities": ["Backup", "Recovery", "Ransomware"]},
    {"vendor": "Nutanix", "level": "Partner", "capabilities": ["HCI", "AHV", "Files"]},
    {"vendor": "Juniper", "level": "Elite", "capabilities": ["Switching", "Routing", "Mist AI"]},
    {"vendor": "Broadcom", "level": "Partner", "capabilities": ["CA Technologies", "Symantec"]},
    {"vendor": "Google Cloud", "level": "Partner", "capabilities": ["IP4G", "GKE", "BigQuery"]},
    {"vendor": "NVIDIA", "level": "Partner", "capabilities": ["DGX", "Networking", "AI"]}
  ],
  "services": [
    "Digital Infrastructure",
    "Hybrid Cloud & App Modernization", 
    "Cybersecurity (Pen Testing, IR, IAM, Managed Security)",
    "Data & AI (ML, Custom AI Apps, Data & AI Design Studio)",
    "Managed Services",
    "IBM Power for Google Cloud (IP4G)"
  ],
  "industries": [
    "Banking", "Healthcare", "Financial Services", 
    "Government (Local & Federal)", "Manufacturing",
    "Transportation", "Retail", "Technology", "Automotive"
  ]
}
```

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Claude Vertex AI not enabled | Medium | High | Check immediately, escalate if blocked |
| Prompt quality issues | High | Medium | Budget time for iteration, use structured outputs |
| Tool failures at scale | Medium | Medium | Graceful degradation, retry logic |
| SSE connection issues | Low | Medium | Auto-reconnect, heartbeat |
| Pilot user feedback overwhelm | Medium | Low | Prioritize based on impact |

---

## Next Steps

1. **Confirm blockers B1-B3 are resolved**
2. **Create GitHub repo**
3. **Start Sprint 1, Day 1 tasks**

Ready to begin when you confirm Vertex AI Claude access is enabled!
