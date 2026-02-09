# 🔭 Scout

**Agentic Sales Intelligence Platform for VAR/SI Sales Teams**

Scout autonomously researches companies and initiatives using a multi-agent AI system, building living intelligence profiles that help sellers have more effective conversations.

## Features

- **Multi-Agent Research** — 4 specialized AI agents (Prime, Research, Synthesis, Presentation) work in parallel
- **Real-Time Dashboard** — Watch research happen live via SSE streaming
- **Initiative Discovery** — AI discovers opportunities you didn't know about
- **Portfolio Mapping** — Findings mapped to your vendor partnerships
- **Team Collaboration** — Share intelligence across deal teams

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.12+ / FastAPI |
| Frontend | Next.js 14 / React / TypeScript / Tailwind |
| Database | PostgreSQL + JSONB |
| AI | Claude Sonnet 4 via Vertex AI |
| Search | Brave Search API |
| Scraping | httpx + BeautifulSoup |
| Real-time | Server-Sent Events (SSE) |
| Deployment | GCP Cloud Run + Vercel |

## Quick Start

```bash
# Clone
git clone https://github.com/aquaregiaswarm-blip/scout.git
cd scout

# Start local environment
docker-compose up -d

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## Project Structure

```
scout/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── agents/    # Multi-agent research engine
│   │   ├── routers/   # API endpoints
│   │   ├── db/        # Database layer
│   │   └── models/    # Pydantic models
│   └── tests/
├── frontend/          # Next.js dashboard
│   └── src/
│       ├── app/       # Pages
│       ├── components/
│       └── hooks/
└── docs/              # Documentation
```

## Documentation

- [CLAUDE.md](./CLAUDE.md) — AI assistant guide
- [PROJECT_PLAN.md](./PROJECT_PLAN.md) — Sprint plan with tasks
- [Scout-Complete-Specification.md](./Scout-Complete-Specification.md) — Full product spec
- [Scout-Epics-and-Stories.md](./Scout-Epics-and-Stories.md) — User stories

## Environment Variables

### Backend
```
GOOGLE_CLOUD_PROJECT=prj-cts-lab-vertex-sandbox
BRAVE_SEARCH_API_KEY=...
DATABASE_URL=postgresql+asyncpg://...
JWT_SECRET=...
```

### Frontend
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

*Part of the [Aqua Regia](https://aquaregia.life) suite* 🜆
