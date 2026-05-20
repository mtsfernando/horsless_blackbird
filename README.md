# 🏌️ Horseless Blackbird

A full-stack golf leaderboard & stats platform for your friend group. Automated data collection from 18Birdies, AI-generated match summaries, and weekly email reports.

## Architecture

```
GoDaddy Domain → EC2 Instance → NGINX Reverse Proxy
                                      ↓
                    ┌─────────────────────────────────┐
                    │         Docker Compose           │
                    │                                  │
                    │  React Frontend  (Dashboard UI)  │
                    │  FastAPI Backend (Business Logic) │
                    │  Playwright Scraper (Data Import) │
                    │  PostgreSQL (Database)            │
                    │  Jenkins (Automation)             │
                    └─────────────────────────────────┘
                                      ↓
                    External: OpenAI API · Mailgun · New Relic
```

## Quick Start (Development)

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

### 1. Clone & Configure
```bash
cp .env.example .env
# Edit .env with your secrets (see comments in file for generation commands)
```

### 2. Start All Services
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### 3. Access
| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api |
| API Docs | http://localhost:8000/docs |

### 4. Run Migrations
```bash
docker compose exec backend alembic upgrade head
```

## Project Structure

```
├── frontend/     # Vite + React (JavaScript)
├── backend/      # FastAPI (Python 3.12)
├── scraper/      # Playwright browser automation
├── nginx/        # Reverse proxy config
├── jenkins/      # CI/CD automation
├── db/           # Database init scripts
└── docker-compose.yml
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vite + React 19 |
| Backend | FastAPI + SQLAlchemy 2.x |
| Database | PostgreSQL 16 |
| Scraping | Playwright (Chromium) |
| AI | OpenAI GPT-4o-mini |
| Email | Mailgun |
| Proxy | NGINX |
| CI/CD | Jenkins |
| Monitoring | New Relic |

## License

Private project — not for distribution.
