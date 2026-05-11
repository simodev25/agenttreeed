---
description: Diagnostiquer et localiser la cause d'un échec dans le pipeline 4-phases de Kairos Mesh (AgentStep, logs, simulation mode).
---

# agent-pipeline-debug

## When to use

Utiliser ce skill quand :
- Un run renvoie `status=failed` ou un agent renvoie `status=failed` dans la table `agent_steps`
- Le pipeline s'arrête sans décision de trading lisible
- Un agent sort une erreur de désérialisation JSON / schéma Pydantic
- Un run timeout sur un agent spécifique (Phase 1 parallèle ou Phase 2+3 débat)

## Inputs

- `run_id` : UUID ou ID entier du run à analyser (visible dans la réponse `POST /api/v1/runs`)
- Accès à la base SQLite locale (`backend/test.db`) ou PostgreSQL selon l'environnement

## Procedure

### Étape 1 — Identifier le point d'échec dans `agent_steps`

```bash
# SQLite (dev local)
sqlite3 backend/test.db "
SELECT agent_name, status, error, created_at
FROM agent_steps
WHERE run_id = <run_id>
ORDER BY created_at ASC;
"

# PostgreSQL (docker-compose)
docker compose exec backend python -c "
from app.db.session import get_db_sync
from app.db.models.agent_step import AgentStep
with get_db_sync() as db:
    steps = db.query(AgentStep).filter(AgentStep.run_id == <run_id>).all()
    for s in steps:
        print(s.agent_name, s.status, s.error[:200] if s.error else None)
"
```

Agents dans l'ordre d'exécution :
1. **Phase 1** (parallèle) : `technical-analyst`, `news-analyst`, `market-context-analyst`
2. **Phase 2+3** (conditionnel) : `bullish-researcher`, `bearish-researcher`, `trader-agent` (débat)
3. **Phase 4** : `trader-agent` (décision), `risk-manager`, `execution-manager`

### Étape 2 — Lire le payload de sortie de l'agent en erreur

```bash
sqlite3 backend/test.db "
SELECT agent_name, output_payload, error
FROM agent_steps
WHERE run_id = <run_id> AND agent_name = '<agent_name>';
" | python3 -m json.tool
```

Champs clés dans `output_payload` :
- `metadata.confidence` — valeur 0.0 si absente ou non parsée par le LLM
- `degraded` — `true` si l'agent a utilisé le fallback déterministe
- `status` dans la réponse `Msg` — distinguer echec schema vs echec outil

### Étape 3 — Reproduire en simulation (sans broker, sans LLM si besoin)

```bash
# Lancer un run en mode simulation directement
cd backend && pytest tests/unit/test_agentscope_registry.py -v -k "simulation"

# Ou via l'API locale
curl -s -X POST http://localhost:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"pair": "EURUSD", "timeframe": "H1", "mode": "simulation"}' | python3 -m json.tool
```

### Étape 4 — Inspecter les traces Prometheus / OpenTelemetry

```bash
# Métriques exposées sur le backend
curl -s http://localhost:8000/metrics | grep -E "agent_(step|run|error)"
```

Métriques clés définies dans `backend/app/observability/metrics.py` :
- `agent_step_duration_seconds{agent_name}`
- `agent_step_errors_total{agent_name}`

### Étape 5 — Tests ciblés par agent défaillant

```bash
# Tests du registry (orchestration complète)
cd backend && pytest tests/unit/test_agentscope_registry.py -v

# Tests des schémas (désérialisation JSON → Pydantic)
cd backend && pytest tests/unit/test_agentscope_schemas.py -v

# Tests toolkit (outils MCP par agent)
cd backend && pytest tests/unit/test_agentscope_toolkit.py -v

# Test débat Phase 2+3
cd backend && pytest tests/unit/test_agentscope_debate.py -v
```

### Étape 6 — Vérifier le fallback déterministe (Phase 1)

Si un agent Phase 1 `degraded=true` dans le payload, le pipeline a utilisé le fallback déterministe.
Ce mode est testé dans :
```bash
cd backend && pytest tests/unit/test_deterministic_fallback.py -v
```

## Validation

- [ ] `agent_steps` ne contient plus de lignes avec `status=failed` pour un nouveau run
- [ ] `pytest tests/unit/test_agentscope_registry.py -v` passe au vert
- [ ] Le payload `output_payload` de chaque agent contient tous les champs obligatoires de son schéma (voir `backend/app/services/agentscope/schemas.py`)
- [ ] `degraded=false` dans les outputs Phase 1 si le LLM est configuré

## Source Anchors

- `backend/app/services/agentscope/registry.py` — pipeline 4-phases, AgentStep persistence, timeout/retry
- `backend/app/db/models/agent_step.py` — schéma table `agent_steps` (run_id, agent_name, status, error, output_payload)
- `backend/app/db/models/agent_runtime_session.py` — sessions d'exécution (phase, turn, error)
- `backend/app/services/agentscope/schemas.py` — schémas Pydantic de sortie par agent, champ `degraded`
- `backend/app/observability/metrics.py` — métriques Prometheus par agent
- `docs/runtime-flow.md` — flow complet de dispatch → Celery → registry → DB
- `docs/decision-pipeline.md` — seuils de confiance, gating, comportement Phase 2+3 conditionnel
- `backend/tests/unit/test_agentscope_registry.py` — tests d'intégration du pipeline
