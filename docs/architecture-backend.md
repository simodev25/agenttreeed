# Architecture Backend — Kairos Mesh

## Résumé Exécutif

Kairos Mesh est un système de trading multi-agents gouverné, construit avec **FastAPI**, orchestrant **8 agents IA spécialisés** via AgentScope dans un pipeline en 4 phases. L'architecture suit un pattern **monolithe en couches** avec déport de tâches asynchrones via **Celery**.

Le système implémente un contrôle de risque déterministe, un workflow de gouvernance avec approbation humaine, et supporte plusieurs fournisseurs LLM (Ollama local, OpenAI, Mistral) interchangeables à chaud.

---

## Pattern Architectural

**Monolithe en couches (Repository-Service-Router)** avec déport asynchrone Celery.

```
Routes (app/api/routes/) ──► Services (app/services/) ──► Modèles (app/db/models/)
```

### Principes Fondamentaux

- **Settings singleton** via `pydantic-settings` + `@lru_cache` pour la configuration centralisée
- **Lifespan context manager** pour le bootstrap applicatif (création admin, connecteurs, chargement skills agents) avec **file locking inter-processus** pour la sécurité multi-worker
- **RBAC 5 rôles** : `super-admin`, `admin`, `trader-operator`, `analyst`, `viewer`
- **JWT Bearer auth** (HS256) via `python-jose` pour l'authentification sans état
- **WebSocket polling** pour les mises à jour temps réel vers le frontend

### Flux de Données Typique

```
Client HTTP/WS
    │
    ▼
FastAPI Router (validation Pydantic, auth JWT, vérification RBAC)
    │
    ▼
Service Layer (logique métier, orchestration)
    │
    ├──► SQLAlchemy Models (persistance)
    ├──► Celery Task Queue (tâches longues : analyse, backtests)
    └──► AgentScope (pipeline multi-agents)
```

---

## Pipeline Multi-Agents (4 Phases)

Le cœur du système repose sur un pipeline séquentiel en 4 phases où chaque phase produit des artefacts consommés par la suivante.

### Phase 1 — Recherche

Quatre agents spécialisés analysent le marché en parallèle :

| Agent | Rôle |
|---|---|
| **Technical Analyst** | Analyse technique (indicateurs, patterns, niveaux clés) |
| **Fundamental Analyst** | Analyse fondamentale (données macro, calendrier économique) |
| **Sentiment Analyst** | Analyse de sentiment (news, réseaux sociaux, positionnement) |
| **Market Context Analyst** | Contexte de marché (corrélations, volatilité, régime de marché) |

### Phase 2 — Synthèse

- **Senior Analyst** : synthétise les 4 rapports de recherche en une vue consolidée avec conviction pondérée

### Phase 3 — Débat

- **Debate Agent** : challenge contradictoire de la synthèse, identifie les biais, teste la robustesse de la thèse d'investissement

### Phase 4 — Décision

- **Master Decision Agent** : décision finale (BUY/SELL/HOLD) basée sur la synthèse et le débat
- **Risk Engine déterministe** : gating, sizing de position, vérification des limites
- **Execution** : passage d'ordre (paper ou live)

```
Phase 1: Recherche          Phase 2: Synthèse     Phase 3: Débat       Phase 4: Décision
┌──────────────────┐
│ Technical Analyst │──┐
│ Fundamental Analyst│──┤
│ Sentiment Analyst  │──┼──► Senior Analyst ──► Debate Agent ──► Master Decision
│ Market Context     │──┘                                         │
└──────────────────┘                                        Risk Engine
                                                                  │
                                                             Execution
```

---

## Services Critiques

### `agentscope/` — Orchestration Multi-Agents

Orchestration des 8 agents IA, registre des agents, logique de débat contradictoire, schémas de communication, et toolkit MCP pour l'outillage des agents.

### `risk/` — Moteur de Risque Déterministe

Moteur de risque entièrement déterministe (pas de LLM) :
- **Gating** : vérification des préconditions avant tout trade
- **Sizing** : calcul de la taille de position (% du capital, ATR-based)
- **Limites hard/soft** : drawdown max, exposition max par paire, nombre max de positions simultanées

### `execution/` — Exécution des Ordres

- **Paper trading** : exécution simulée pour validation
- **Live trading** via MetaAPI (connexion aux brokers MT4/MT5)
- **Preflight checks** : vérifications pré-exécution (spread, slippage, horaires de marché)

### `governance/` — Gouvernance et Monitoring

- Monitoring des positions ouvertes
- Recommandations automatiques : Stop-Loss, Take-Profit, CLOSE
- Workflow d'approbation humaine pour les décisions de trading

### `strategy/` — Gestion des Stratégies

- **Designer LLM** : création de stratégies assistée par IA
- **Backtesting** : validation historique des stratégies
- **Monitoring de signaux** : suivi en temps réel des signaux actifs

### `llm/` — Abstraction Multi-Fournisseur LLM

Multi-provider switchable via la variable `LLM_PROVIDER` :
- **Ollama** : modèles locaux (aucune donnée envoyée à l'extérieur)
- **OpenAI** : GPT-4, GPT-3.5
- **Mistral** : modèles Mistral AI

### `mcp/` — Outils MCP (Model Context Protocol)

**18 outils MCP** exposés aux agents pour l'interaction avec les données :
- Analyse technique (indicateurs, patterns)
- News et sentiment
- Données de marché (prix, volumes, corrélations)
- Évaluation de risque

### `backtest/` — Moteur de Backtesting

Moteur de backtesting avec génération de courbe d'équité, métriques de performance (Sharpe, Sortino, drawdown max), et comparaison benchmark.

---

## Décisions de Design Notables

### 1. Trois Modes de Décision

| Mode | Comportement |
|---|---|
| **Conservative** | Seuils de conviction élevés, sizing réduit, validation humaine systématique |
| **Balanced** | Paramètres équilibrés, validation humaine au-dessus d'un seuil de risque |
| **Permissive** | Seuils relâchés, auto-exécution possible pour les trades à faible risque |

### 2. Workflow d'Approbation Gouvernance

```
pending ──► approved ──► exécution
    │
    ├──► rejected (refus humain)
    ├──► expired (timeout dépassé)
    └──► auto_executed (mode permissif, critères remplis)
```

### 3. Cycle de Vie des Stratégies

```
DRAFT ──► BACKTESTING ──► VALIDATED ──► PAPER ──► LIVE
                │                                    │
                └──► REJECTED ◄──────────────────────┘
```

### 4. Sécurité Multi-Worker

File lock (`/tmp/trading_startup.lock`) pour garantir qu'un seul worker exécute le bootstrap applicatif (création admin, initialisation des connecteurs). Évite les race conditions en déploiement multi-processus (Gunicorn, Uvicorn multi-workers).

### 5. Middleware de Sécurité

Headers de sécurité injectés systématiquement :
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`

### 6. Double Base de Données

| Environnement | Base | Notes |
|---|---|---|
| **Développement** | SQLite | Zéro configuration, fichier local |
| **Production** | PostgreSQL | Pool de connexions tunés (`pool_size`, `max_overflow`, `pool_recycle`) |

### 7. Celery : Deux Queues Séparées

| Queue | Usage | Time Limit |
|---|---|---|
| `analysis` | Pipelines d'analyse multi-agents | Limite adaptée aux appels LLM |
| `backtests` | Exécution de backtests | Limite plus longue (simulations historiques) |

### 8. Bootstrap des Skills Agents au Démarrage

Les compétences (skills) des agents sont chargées au démarrage de l'application depuis un fichier de configuration JSON. Chaque agent reçoit son jeu d'outils MCP et ses instructions système selon son rôle.

---

## Observabilité

### Métriques — Prometheus

Client Prometheus intégré pour l'exposition de métriques applicatives (compteurs de requêtes, latences, taux d'erreur, métriques métier).

### Traces Distribuées — OpenTelemetry

- Export OTLP vers **Tempo** pour la visualisation des traces
- **Instrumentation automatique FastAPI** : chaque requête HTTP génère une trace
- Propagation de contexte à travers les appels de service

### Logs d'Appels LLM

Table `llm_call_logs` pour le suivi du coût et de la latence de chaque appel LLM :
- Fournisseur et modèle utilisés
- Tokens consommés (input/output)
- Latence de réponse
- Coût estimé

---

## Diagramme de Déploiement

```
┌─────────────────────────────────────────────────┐
│                 Docker Compose                   │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐ │
│  │ Frontend │  │ Backend  │  │ Celery Worker │ │
│  │ (Next.js)│  │ (FastAPI)│  │  (2 queues)   │ │
│  └────┬─────┘  └────┬─────┘  └───────┬───────┘ │
│       │              │                │          │
│  ┌────┴──────────────┴────────────────┴───────┐ │
│  │           Infrastructure                    │ │
│  │  PostgreSQL · Redis · RabbitMQ · Ollama    │ │
│  │  Prometheus · Tempo                         │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```
