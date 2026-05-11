# Architecture d'intégration

## Vue d'ensemble

Le système est déployé sous forme de 8 services Docker orchestrés via Docker Compose, avec des profils optionnels pour le monitoring.

---

## Topologie des services

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│  Frontend React │────▶│  Backend FastAPI      │────▶│ PostgreSQL 16   │
│  port 5173      │     │  port 8000            │     │ port 5432       │
│  (HTTP + WS)    │     │  (REST + WebSocket)   │     │                 │
└─────────────────┘     └──────┬───────┬────────┘     └─────────────────┘
                               │       │
                    ┌──────────┘       └──────────┐
                    ▼                              ▼
             ┌─────────────┐              ┌──────────────┐
             │  Redis 7    │              │  RabbitMQ 3  │
             │  port 6380  │              │  port 5672   │
             │  cache +    │              │  port 15672  │
             │  résultats  │              │  (management)│
             └──────┬──────┘              └──────┬───────┘
                    │                             │
                    └──────────┐   ┌──────────────┘
                               ▼   ▼
                        ┌──────────────┐
                        │ Worker Celery│
                        │ (tâches      │
                        │  asynchrones)│
                        └──────────────┘

┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Tempo      │────▶│   Grafana    │◀────│ Prometheus  │
│ ports 3200   │     │   port 3000  │     │ port 9090   │
│ 4317, 4318   │     │              │     │             │
│ (traces)     │     │              │     │ (métriques) │
└─────────────┘     └──────────────┘     └─────────────┘
```

### Détail des services

| Service | Technologie | Port(s) | Rôle | Dépendances |
|---------|-------------|---------|------|-------------|
| PostgreSQL | PostgreSQL 16 | 5432 | Base de données relationnelle principale | - |
| Redis | Redis 7 | 6380 | Cache applicatif + backend de résultats Celery | - |
| RabbitMQ | RabbitMQ 3 | 5672 / 15672 | Broker de messages pour les tâches Celery | - |
| Backend | FastAPI (Uvicorn) | 8000 | API REST + endpoints WebSocket | PostgreSQL, Redis, RabbitMQ |
| Worker | Celery | - | Exécution des tâches asynchrones (agents IA, backtests) | PostgreSQL, Redis, RabbitMQ |
| Frontend | React (Vite) | 5173 | Interface utilisateur SPA | Backend |
| Tempo | Grafana Tempo | 3200 / 4317 / 4318 | Collecte et stockage des traces distribuées | - |
| Prometheus | Prometheus | 9090 | Collecte et stockage des métriques | Backend, Worker |
| Grafana | Grafana | 3000 | Visualisation des traces et métriques | Tempo, Prometheus |

---

## Points d'intégration

### 1. Frontend ↔ Backend

- **API REST** : tous les endpoints sous `/api/v1/*`
- **WebSocket** : 5 endpoints pour les flux temps réel (portfolio, runs, gouvernance, prix, ordres)

### 2. Backend ↔ PostgreSQL

- **ORM** : SQLAlchemy pour l'accès aux données
- **Migrations** : Alembic pour le versionnement du schéma de base de données

### 3. Backend ↔ Redis

- **Cache** : mise en cache des données fréquemment accédées
- **Celery result backend** : stockage des résultats des tâches asynchrones

### 4. Backend ↔ RabbitMQ

- **Broker Celery** : distribution des messages vers les workers
- **Files d'attente** : `analysis` (runs d'analyse), `backtests` (exécution de backtests)

### 5. Backend / Worker ↔ Tempo

- **Traces OpenTelemetry** : envoi via protocole OTLP (HTTP port 4318, gRPC port 4317)
- Instrumentation automatique des requêtes, tâches Celery et appels LLM

### 6. Backend / Worker ↔ Prometheus

- **Endpoint `/metrics`** : exposition des métriques au format Prometheus
- Métriques personnalisées : latence des agents, nombre de runs, taux d'erreur

### 7. Backend ↔ MetaAPI

- **SDK cloud MetaAPI** : connexion aux brokers MT4/MT5
- Opérations : récupération des comptes, positions, ordres, deals, exécution d'ordres

### 8. Backend ↔ Fournisseurs LLM

- **Ollama** : modèles locaux (développement, inférence sans coût)
- **OpenAI** : modèles GPT (production)
- **Mistral** : modèles Mistral (alternative)

### 9. Backend ↔ yfinance

- **Données de marché historiques** : récupération des cours, volumes et indicateurs via la bibliothèque yfinance

### 10. Backend ↔ Serveurs MCP

- **Model Context Protocol** : 18 outils internes enregistrés + possibilité de connecter des serveurs MCP externes
- Découverte dynamique des outils disponibles sur les serveurs externes

---

## Flux de données

### Flux d'analyse

```
Frontend                Backend              Celery Worker           Frontend
   │                       │                       │                    │
   │  POST /api/v1/runs    │                       │                    │
   │──────────────────────▶│                       │                    │
   │                       │  Envoi tâche Celery   │                    │
   │                       │──────────────────────▶│                    │
   │                       │                       │  Exécution des     │
   │                       │                       │  8 agents IA       │
   │                       │                       │  (séquentiel/      │
   │                       │                       │   parallèle)       │
   │                       │                       │                    │
   │                       │                       │  Décision finale   │
   │                       │                       │  + Exécution ordre │
   │                       │                       │                    │
   │                       │  Mise à jour état     │                    │
   │                       │◀─────────────────────│                    │
   │  WebSocket (updates)  │                       │                    │
   │◀──────────────────────│                       │                    │
```

### Flux de gouvernance

```
Celery Beat (toutes les 5 min)
   │
   ▼
Gouvernance des positions ouvertes
   │
   ▼
Recommandation (maintenir / clôturer / ajuster)
   │
   ├──▶ Approbation automatique (si configuré)
   │         │
   │         ▼
   │    Exécution de l'ordre
   │
   └──▶ Approbation humaine requise
             │
             ▼
        Notification Frontend (WebSocket)
             │
             ▼
        Décision utilisateur (approuver / rejeter)
             │
             ▼
        Exécution ou annulation
```

### Flux portefeuille

```
Celery Beat (périodique)
   │
   ▼
Snapshot du portefeuille (MetaAPI + base de données)
   │
   ▼
Stockage en base + publication Redis
   │
   ▼
WebSocket → Frontend (mise à jour temps réel du tableau de bord)
```

### Flux des prix en temps réel

```
MetaAPI SDK
   │
   ▼
Redis pub/sub (canal de prix)
   │
   ▼
WebSocket Backend
   │
   ▼
Frontend (mise à jour des graphiques et positions)
```

---

## Configuration : Développement vs Production

| Aspect | Développement | Production |
|--------|---------------|------------|
| Workers Uvicorn | 1 | 4 |
| Concurrence Celery | 2 | 4 |
| Ports d'infrastructure | Exposés (accès direct aux services) | Fermés (accès uniquement via le backend) |
| Identifiants | Codés en dur dans la configuration | Paramétrage via fichier `.env.prod` |
| Frontend | Serveur de développement Vite avec HMR | Build optimisé (`npm run build`) + preview |
| Monitoring | Toujours actif (démarré par défaut) | Opt-in via `--profile monitoring` |

---

## Tableaux de bord Grafana pré-configurés

Le système inclut 5 tableaux de bord Grafana provisionnés automatiquement :

| Identifiant | Nom | Description |
|-------------|-----|-------------|
| `agent-runtime-overview` | Vue d'ensemble du runtime agents | Métriques globales : nombre de runs, durée moyenne, taux de succès, agents actifs |
| `agent-runtime-sessions` | Sessions agents détaillées | Détail par session : timeline des agents, durée par étape, erreurs |
| `agentscope-tracing` | Traces AgentScope | Traces distribuées des interactions entre agents, appels LLM, outils MCP |
| `backend-performance` | Performance backend | Latence des endpoints, débit de requêtes, utilisation mémoire, connexions actives |
| `llm-observability` | Observabilité LLM | Tokens consommés, latence par modèle, coût estimé, taux d'erreur par fournisseur |
