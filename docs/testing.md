# Tests

## Prérequis

```bash
cp backend/.env.example backend/.env
docker compose up -d --build
```

## Backend

Couverture actuelle:

- unit tests:
  - règles de risque
  - décision trader
  - orchestration
  - backtest engine
  - prompts versionnés
- integration API:
  - auth/login
  - runs
  - backtests
  - connecteurs

Commande:

```bash
docker compose exec backend pytest -q
```

## Frontend

- build vérifié:

```bash
docker compose exec frontend npm run build
```

- e2e smoke (Playwright):

```bash
docker compose exec frontend npm run test:e2e
```

## Smoke tests fonctionnels (manuel)

1. Auth

```bash
curl -sS -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@local.dev","password":"admin1234"}'
```

2. Lancer un run async

```bash
curl -sS -X POST "http://localhost:8000/api/v1/runs?async_execution=true" \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"pair":"EURUSD","timeframe":"H1","mode":"simulation","risk_percent":1}'
```

3. Vérifier exécution agents dans les logs

```bash
docker compose logs -f worker | rg "agent_step|ollama_chat_call|orchestration"
```

4. Backtest agents_v1

```bash
curl -sS -X POST http://localhost:8000/api/v1/backtests \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"pair":"EURUSD","timeframe":"H1","start_date":"2025-01-01","end_date":"2025-03-01","strategy":"agents_v1"}'
```

5. Vérifier workflow source du backtest

`metrics.workflow_source` doit valoir `ForexOrchestrator.analyze_context`.

## Tests connecteurs

- `POST /api/v1/connectors/ollama/test`
- `POST /api/v1/connectors/metaapi/test`
- `POST /api/v1/connectors/yfinance/test`
- `POST /api/v1/connectors/qdrant/test`

## Vérification observabilité

- API metrics: `http://localhost:8000/metrics`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Rebuild ciblé (sans tout relancer)

- backend:
```bash
docker compose up -d --build backend
```
- worker:
```bash
docker compose up -d --build worker
```
- frontend:
```bash
docker compose up -d --build frontend
```

## Scale workers Celery

```bash
docker compose up -d --scale worker=3 worker
```

## Régressions à surveiller

- run bloqué en `running` sans étapes agents.
- absence d'appels LLM dans les logs malgré LLM activé.
- backtest `agents_v1` tombant sur workflow `ema_rsi`.
- paper/live exécuté sans contrôle risque.
