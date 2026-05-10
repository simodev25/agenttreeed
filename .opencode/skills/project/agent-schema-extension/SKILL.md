---
description: Ajouter ou modifier un champ dans le schéma Pydantic de sortie d'un agent trading de Kairos Mesh, en respectant le contrat LLM-First et la chaîne de normalisation.
---

# agent-schema-extension

## When to use

Utiliser ce skill quand :
- On doit ajouter un champ de sortie à un agent existant (ex : `volatility_regime` pour `market-context-analyst`)
- On modifie les valeurs acceptées d'un champ `Literal` (ex : ajouter `"mixed"` à un champ de biais)
- On change la valeur par défaut d'un champ optionnel
- On veut comprendre pourquoi le LLM retourne un champ ignoré (`extra="ignore"` par défaut)

**Ne pas utiliser pour modifier le moteur de risque** — voir zone critique dans `.samourai/ai/agent/project-profile.md`.

## Inputs

- Nom de l'agent cible : l'un de `technical-analyst`, `news-analyst`, `market-context-analyst`, `bullish-researcher`, `bearish-researcher`, `trader-agent`, `risk-manager`, `execution-manager`
- Nom et type du nouveau champ
- Valeur par défaut souhaitée (obligatoire — tous les champs doivent avoir un défaut)

## Procedure

### Étape 1 — Localiser le schéma de l'agent

```
backend/app/services/agentscope/schemas.py
```

Mapping agent → classe Pydantic (défini aussi dans `registry.py:AGENT_STRUCTURED_MODELS`) :

| Agent | Classe |
|-------|--------|
| `technical-analyst` | `TechnicalAnalysisResult` |
| `news-analyst` | `NewsAnalysisResult` |
| `market-context-analyst` | `MarketContextResult` |
| `bullish-researcher` / `bearish-researcher` | `DebateThesis` |
| `trader-agent` | `TraderDecisionDraft` |
| `risk-manager` | `RiskAssessmentResult` |
| `execution-manager` | `ExecutionPlanResult` |

### Étape 2 — Appliquer la philosophie LLM-First avant d'ajouter le champ

Règles du projet (`schemas.py` docstring) :
- **Analystes** (`Phase 1`) → produisent des FAITS qualitatifs, pas des scores ni recommandations
- **Trader** → décide librement (conviction, pas score contraint)
- **Risk-manager** → ne peut que rendre plus conservatif, jamais plus agressif
- **Débat** (`bullish/bearish`) → doit trancher (bullish / bearish / no_edge)

❌ Ne pas ajouter un champ `score: float` à `TechnicalAnalysisResult` — viole LLM-First.
✅ Ajouter un champ `volatility_context: Literal["high", "medium", "low"] = "low"` est conforme.

### Étape 3 — Ajouter le champ avec une valeur par défaut safe

```python
# Dans schemas.py, classe cible
class TechnicalAnalysisResult(_SchemaBase):
    # ... champs existants ...
    mon_nouveau_champ: Literal["valeur_a", "valeur_b"] = "valeur_a"  # défaut obligatoire
```

Si le champ nécessite une normalisation (valeurs LLM imprécises attendues), ajouter la logique
dans le `@model_validator(mode="before")` existant de la classe :

```python
@model_validator(mode="before")
@classmethod
def normalize_fields(cls, data: Any) -> Any:
    if isinstance(data, dict):
        # normalisation existante...
        if "mon_nouveau_champ" in data:
            val = str(data["mon_nouveau_champ"]).strip().lower()
            if val not in {"valeur_a", "valeur_b"}:
                data["mon_nouveau_champ"] = "valeur_a"  # fallback safe
    return data
```

### Étape 4 — Vérifier que le schéma est bien branché dans le registry

```python
# backend/app/services/agentscope/registry.py
AGENT_STRUCTURED_MODELS: dict[str, type] = {
    "technical-analyst": TechnicalAnalysisResult,
    # ...
}
```

Aucune modification nécessaire ici si le schéma de l'agent concerné est déjà présent.

### Étape 5 — Mettre à jour les tests unitaires

```bash
# Tests des schémas à mettre à jour
backend/tests/unit/test_agentscope_schemas.py
```

Ajouter au moins :
1. Un test avec `mon_nouveau_champ` présent et valide
2. Un test avec une valeur imprécise (alias LLM) qui doit normaliser vers le défaut
3. Un test sans `mon_nouveau_champ` (doit utiliser le défaut, pas planter)

### Étape 6 — Vérifier l'impact sur le prompt de l'agent

Le prompt de l'agent doit explicitement demander au LLM de produire le nouveau champ, sinon il
sera absent dans 70%+ des réponses et le défaut sera toujours utilisé.

Prompts fallback : `backend/app/services/agentscope/prompts.py`
Prompts en DB : consultables via `GET /api/v1/prompts/{agent_name}` (si endpoint disponible)

### Étape 7 — Lancer les tests

```bash
cd backend && pytest tests/unit/test_agentscope_schemas.py -v
cd backend && pytest tests/unit/test_agentscope_registry.py -v
cd backend && pytest -q  # suite complète
```

## Validation

- [ ] `pytest tests/unit/test_agentscope_schemas.py -v` : tous les cas du nouveau champ passent
- [ ] Le nouveau champ a une valeur par défaut non-None définie dans le schéma
- [ ] Le `@model_validator` normalise les valeurs imprécises sans lever d'exception
- [ ] `pytest tests/unit/test_agentscope_registry.py -v` passe (le registry sérialise/désérialise correctement)
- [ ] Le prompt de l'agent demande explicitement le nouveau champ (sinon le défaut sera toujours utilisé)

## Source Anchors

- `backend/app/services/agentscope/schemas.py` — toutes les classes Pydantic, philosophie LLM-First, `_normalize_signal()`, `_normalize_decision()`, `@model_validator`
- `backend/app/services/agentscope/registry.py` — `AGENT_STRUCTURED_MODELS` dict, désérialisation des outputs
- `backend/app/services/agentscope/prompts.py` — prompts fallback, philosophie par agent
- `backend/tests/unit/test_agentscope_schemas.py` — exemples de tests de normalisation existants
- `docs/decision-pipeline.md` — philosophie LLM-First, règles par phase (analysts = FACTS, trader = libre)
