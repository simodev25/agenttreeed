# Vue d'ensemble du projet — Kairos Mesh

## Description

**Kairos Mesh** est un systeme de trading multi-agents gouverne orchestrant **8 agents IA specialises** dans un pipeline de recherche et decision structure. L'approche est **simulation-first**, avec trading paper/live optionnel via MetaAPI (MT4/MT5).

## Type de depot

**Monorepo multi-parts** compose de trois parties principales :

| Partie | Technologie | Description |
|--------|-------------|-------------|
| **Backend** | Python / FastAPI | API REST, pipeline multi-agents, moteur de risque, execution |
| **Frontend** | React 19 / TypeScript | Interface de trading, tableaux de bord, graphiques temps reel |
| **Infrastructure** | Docker / Helm / Observabilite | Orchestration conteneurs, monitoring, tracage distribue |

## Stack technologique

### Backend

| Categorie | Technologie | Version | Role |
|-----------|-------------|---------|------|
| Framework web | FastAPI | 0.116.1 | API REST + WebSocket |
| ORM | SQLAlchemy | 2.0.43 | Modeles et acces base de donnees |
| File de taches | Celery | 5.5.3 | Taches asynchrones (analyse, backtest, monitoring) |
| Base de donnees | PostgreSQL | 16 | Stockage persistant |
| Cache | Redis | 7 | Cache, broker Celery, sessions |
| Message broker | RabbitMQ | 3 | File de messages pour Celery |
| Framework agents | AgentScope | 1.0.18 | Orchestration des agents IA |
| Protocole outils | MCP / FastMCP | — | Serveur d'outils pour les agents (18 outils) |
| LLM | Ollama / OpenAI / Mistral | — | Modeles de langage (local et cloud) |
| Donnees marche | yfinance | — | Recuperation des donnees de marche |
| Analyse donnees | pandas | — | Manipulation et analyse des donnees |
| Indicateurs techniques | ta | — | Calcul des indicateurs techniques |
| Observabilite | Prometheus / OpenTelemetry | — | Metriques et tracage distribue |

### Frontend

| Categorie | Technologie | Version | Role |
|-----------|-------------|---------|------|
| Framework UI | React | 19.1 | Interface utilisateur reactive |
| Bundler | Vite | 7.1 | Build et dev server |
| CSS | Tailwind CSS | 4.2 | Styles utilitaires |
| Graphiques | MUI (charts) | 7.3 | Graphiques et visualisations |
| Graphiques trading | Lightweight Charts | 5.1 | Graphiques chandeliers temps reel |
| Langage | TypeScript | 5.9 | Typage statique |
| Tests E2E | Playwright | — | Tests bout en bout |

### Infrastructure

| Categorie | Technologie | Version | Role |
|-----------|-------------|---------|------|
| Conteneurs | Docker Compose | — | Orchestration de 8 services |
| Metriques | Prometheus | 2.55 | Collecte et stockage des metriques |
| Tableaux de bord | Grafana | 11.2 | Visualisation des metriques et alertes |
| Tracage | Tempo | 2.6 | Tracage distribue |
| Deploiement | Helm charts | — | Deploiement Kubernetes |
| CI/CD | GitHub Actions | — | Integration continue |

## Architecture

Le systeme repose sur un **pipeline multi-agents en 4 phases** :

1. **Recherche** — Collecte des donnees de marche, actualites et indicateurs techniques
2. **Analyse** — Analyse approfondie par des agents specialises (technique, fondamental, sentiment)
3. **Debat** — Confrontation des analyses entre agents pour identifier les convergences et divergences
4. **Decision** — Synthese et generation de signaux de trading

Ce pipeline est complete par :

- **Moteur de risque deterministe** — Validation systematique des signaux avant execution (taille de position, drawdown, exposition)
- **Execution paper/live** — Simulation par defaut, execution reelle optionnelle via MetaAPI (MT4/MT5)
- **Gouvernance des positions** — Suivi, ajustement et cloture des positions ouvertes

## Documentation detaillee

| Document | Description |
|----------|-------------|
| [Analyse de l'arborescence source](./source-tree-analysis.md) | Structure annotee du projet |
| [Rapport de scan](./project-scan-report.json) | Etat du scan initial du projet |
