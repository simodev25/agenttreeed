# Analyse de l'arborescence source — Kairos Mesh

## Arborescence complete annotee

```
MultiAgentTrading/
├── backend/                    # Backend Python/FastAPI
│   ├── app/
│   │   ├── main.py            # Point d'entree FastAPI + bootstrap lifespan
│   │   ├── api/
│   │   │   ├── router.py      # Montage des routes (/api/v1)
│   │   │   └── routes/        # 11 domaines de routes REST
│   │   │       ├── health.py, auth.py, runs.py, trading.py
│   │   │       ├── connectors.py, prompts.py, backtests.py
│   │   │       ├── analytics.py, portfolio.py, strategies.py
│   │   │       └── governance.py
│   │   ├── core/              # Configuration, auth JWT, securite
│   │   ├── db/                # Modeles SQLAlchemy (18 tables)
│   │   ├── schemas/           # Schemas Pydantic
│   │   ├── services/
│   │   │   ├── agentscope/    # Pipeline 4 phases multi-agents
│   │   │   ├── llm/           # Clients LLM (Ollama, OpenAI, Mistral)
│   │   │   ├── mcp/           # Serveur MCP (18 outils)
│   │   │   ├── risk/          # Moteur de risque deterministe
│   │   │   ├── execution/     # Execution paper/live MetaAPI
│   │   │   ├── backtest/      # Moteur de backtesting
│   │   │   ├── market/        # Donnees marche, instruments, news
│   │   │   ├── governance/    # Gouvernance des positions
│   │   │   ├── strategy/      # Designer + moniteur de strategies
│   │   │   ├── analytics/     # Analytiques LLM
│   │   │   ├── config/        # Configuration trading
│   │   │   ├── connectors/    # Connecteurs broker
│   │   │   ├── news/          # Service de news
│   │   │   ├── prompts/       # Templates prompts agents
│   │   │   └── trading/       # Service trading
│   │   ├── tasks/             # Taches Celery (analyse, backtest, monitoring)
│   │   └── observability/     # Prometheus, OpenTelemetry
│   ├── alembic/               # Migrations DB (12 revisions)
│   ├── config/                # Bootstrap JSON skills agents
│   ├── tests/                 # Tests pytest
│   └── Dockerfile
├── frontend/                   # Frontend React 19 / TypeScript
│   ├── src/
│   │   ├── pages/             # 9 pages (Terminal, Portfolio, Orders, Strategies, etc.)
│   │   ├── components/        # 20+ composants (Charts, Tables, Panels, Modals)
│   │   ├── hooks/             # 6 hooks (auth, portfolio WS, trading data, etc.)
│   │   ├── api/               # Client API unifie (40+ methodes)
│   │   ├── types/             # Definitions TypeScript (24 types)
│   │   ├── config/            # Feature flags runtime
│   │   ├── constants/         # Paires forex/crypto, timeframes
│   │   ├── lib/               # Utilitaires (cn())
│   │   ├── utils/             # Prix, symboles
│   │   └── styles/            # Theme Tailwind v4
│   ├── tests/                 # Tests E2E Playwright
│   └── Dockerfile
├── infra/                      # Infrastructure
│   ├── docker/                # Configs Prometheus, Grafana, Tempo
│   └── helm/                  # Charts Helm (forex-platform)
├── docs/                       # Documentation projet
├── governance/                 # Conventions, lifecycle, policies
├── doc/changes/               # Specs de changements (GH-19, GH-20)
├── templates/                  # Templates (spec, plan, test-plan, PR)
├── docker-compose.yml         # Stack dev (8 services)
├── docker-compose.prod.yml    # Stack prod (hardened)
├── Makefile                   # Raccourcis make
└── README.md
```

## Dossiers critiques du backend

| Dossier | Role | Contenu cle |
|---------|------|-------------|
| `backend/app/services/agentscope/` | Pipeline multi-agents | Orchestration des 8 agents IA en 4 phases (recherche, analyse, debat, decision) |
| `backend/app/services/risk/` | Moteur de risque | Validation deterministe des signaux : taille de position, drawdown max, exposition par devise |
| `backend/app/services/execution/` | Execution des ordres | Mode paper (simulation) et mode live via MetaAPI (MT4/MT5) |
| `backend/app/services/mcp/` | Serveur d'outils MCP | 18 outils exposes aux agents (donnees marche, indicateurs, analyse technique) |
| `backend/app/services/governance/` | Gouvernance des positions | Suivi du cycle de vie des positions, ajustements, regles de cloture |
| `backend/app/services/llm/` | Clients LLM | Abstraction multi-fournisseur : Ollama (local), OpenAI, Mistral |
| `backend/app/db/` | Modeles de donnees | 18 tables SQLAlchemy couvrant runs, agents, positions, ordres, strategies |
| `backend/app/tasks/` | Taches asynchrones | Workers Celery pour analyse, backtesting et monitoring en arriere-plan |
| `backend/alembic/` | Migrations | 12 revisions de schema, historique complet des evolutions de la base |

## Dossiers critiques du frontend

| Dossier | Role | Contenu cle |
|---------|------|-------------|
| `frontend/src/pages/` | Pages principales | 9 pages : Terminal, Portfolio, Ordres, Strategies, Backtests, Analytiques, Connecteurs, Prompts, Gouvernance |
| `frontend/src/components/` | Composants reutilisables | 20+ composants : graphiques chandeliers, tableaux de positions, panneaux de configuration, modales |
| `frontend/src/hooks/` | Hooks React | 6 hooks : authentification, WebSocket portfolio temps reel, donnees trading, strategies |
| `frontend/src/api/` | Client API | Client HTTP unifie avec 40+ methodes couvrant tous les endpoints backend |
| `frontend/src/types/` | Types TypeScript | 24 definitions de types partages (Run, Agent, Position, Ordre, Strategie, etc.) |

## Points d'entree

| Point d'entree | Fichier | Description |
|----------------|---------|-------------|
| API backend | `backend/app/main.py` | Demarrage FastAPI avec lifespan bootstrap (connexion DB, Redis, demarrage workers) |
| Routes API | `backend/app/api/router.py` | Montage de toutes les routes sous `/api/v1` |
| Frontend | `frontend/src/main.tsx` | Point d'entree React avec routing et providers |
| Stack dev | `docker-compose.yml` | Orchestration des 8 services (backend, frontend, PostgreSQL, Redis, RabbitMQ, Celery, Prometheus, Grafana) |
| Stack prod | `docker-compose.prod.yml` | Configuration durcie pour la production |
| Deploiement K8s | `infra/helm/` | Charts Helm pour deploiement Kubernetes |

## Points d'integration

| Integration | Source | Cible | Mecanisme |
|-------------|--------|-------|-----------|
| Frontend → Backend | `frontend/src/api/` | `backend/app/api/routes/` | HTTP REST + WebSocket |
| Agents → LLM | `backend/app/services/agentscope/` | `backend/app/services/llm/` | Appels API LLM (Ollama/OpenAI/Mistral) |
| Agents → Outils | `backend/app/services/agentscope/` | `backend/app/services/mcp/` | Protocole MCP (18 outils) |
| Backend → Broker | `backend/app/services/execution/` | MetaAPI (MT4/MT5) | API REST MetaAPI |
| Backend → Marche | `backend/app/services/market/` | yfinance | API Python yfinance |
| Taches async | `backend/app/tasks/` | `backend/app/services/` | Celery via RabbitMQ/Redis |
| Metriques | `backend/app/observability/` | `infra/docker/prometheus/` | Prometheus scraping + OpenTelemetry |
| Tracage | `backend/app/observability/` | `infra/docker/tempo/` | OpenTelemetry traces → Tempo |
