---
description: Modifier le system prompt d'un agent trading de Kairos Mesh sans casser la sortie structurée Pydantic ni introduire du français dans les prompts de production.
---

# agent-prompt-modification

## When to use

Utiliser ce skill quand :
- On veut ajuster les instructions d'un agent (renforcer une règle, changer le style d'analyse)
- On ajoute un nouveau champ au schéma (le prompt doit demander ce champ explicitement)
- On veut basculer entre le prompt stocké en DB et le prompt fallback dans `prompts.py`
- Un agent produit des sorties hors-schéma ou des valeurs non normalisées de façon répétée

## Inputs

- Nom de l'agent cible (l'un des 8 agents de `ALL_AGENT_FACTORIES`)
- Nature de la modification (ajouter instruction / modifier critère existant / ajouter champ)
- Source à modifier : `prompts.py` (fallback) ou DB (via API)

## Procedure

### Étape 1 — Identifier la source active du prompt

```bash
# Via l'API (si le backend tourne)
curl -s http://localhost:8000/api/v1/prompts | python3 -m json.tool
# Chercher l'agent cible — si absent, le fallback de prompts.py est utilisé
```

```python
# Dans le code : backend/app/services/agentscope/prompts.py
AGENT_PROMPTS: dict[str, dict[str, str]] = {
    "technical-analyst": { "system": "...", "user": "..." },
    "news-analyst":      { "system": "...", "user": "..." },
    # ... 8 agents ...
}
```

**Priorité** : le prompt stocké en DB prime sur `prompts.py`. Si la DB contient un prompt pour l'agent, modifier `prompts.py` n'a aucun effet tant que le prompt DB n'est pas supprimé/mis à jour.

### Étape 2 — Contraintes à respecter avant toute modification

1. **Pas de français dans les prompts de production**
   Le test `backend/tests/unit/test_no_french_in_production.py` vérifie que les prompts ne contiennent pas de contenu en français. Toute modification doit rester en anglais.

2. **Ne pas casser les critères de sortie structurée**
   Les prompts doivent demander explicitement les champs du schéma Pydantic correspondant.
   Exemple pour `technical-analyst` :
   - ✅ `"SETUP QUALITY CRITERIA (apply strictly): HIGH: ..."` — ancré dans `TechnicalAnalysisResult.setup_quality`
   - ❌ Supprimer cette section casserait le champ `setup_quality` dans 80%+ des runs

3. **Règle SafeDict** : les placeholders `{pair}`, `{timeframe}` etc. doivent rester intacts.
   Le test `test_prompt_placeholders_gh19.py` valide l'absence de `<MISSING:...>` dans les prompts rendus.

4. **Ne pas ajouter de recommandation de trading dans les analystes Phase 1**
   Les analystes (`technical-analyst`, `news-analyst`, `market-context-analyst`) décrivent des FAITS uniquement. Toute instruction du type "recommend BUY/SELL" viole la philosophie LLM-First.

### Étape 3 — Modifier le prompt fallback dans `prompts.py`

```python
# backend/app/services/agentscope/prompts.py
AGENT_PROMPTS["technical-analyst"]["system"] = (
    # Copier le prompt existant et ajouter/modifier la section concernée
    "You are a technical analyst. Your job is to describe what you SEE in the data, "
    "not to make a trading decision.\n\n"
    # ... section à modifier ...
    "NEW INSTRUCTION: <ajout en anglais>\n\n"
    # ... reste du prompt inchangé ...
)
```

### Étape 4 — Si le prompt est en DB, mettre à jour via l'API

```bash
# Récupérer le prompt actuel
curl -s http://localhost:8000/api/v1/prompts/<agent_name> | python3 -m json.tool

# Mettre à jour (exemple)
curl -s -X PATCH http://localhost:8000/api/v1/prompts/<agent_name> \
  -H "Content-Type: application/json" \
  -d '{"system": "<nouveau prompt complet en anglais>"}'
```

### Étape 5 — Valider que le nouveau champ est demandé dans le prompt

Si la modification vise à faire produire un nouveau champ par le LLM, ajouter une section explicite :

```
OUTPUT FIELD <mon_nouveau_champ>:
- Allowed values: "valeur_a", "valeur_b"
- Default if uncertain: "valeur_a"
- Do NOT omit this field.
```

### Étape 6 — Lancer les tests de validation des prompts

```bash
cd backend && pytest tests/unit/test_no_french_in_production.py -v
cd backend && pytest tests/unit/test_prompt_placeholders_gh19.py -v
cd backend && pytest tests/unit/test_prompt_registry.py -v
cd backend && pytest -q  # suite complète
```

### Étape 7 — Vérifier sur un run de simulation

```bash
# Lancer un run simulation pour observer la sortie de l'agent modifié
curl -s -X POST http://localhost:8000/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"pair": "EURUSD", "timeframe": "H1", "mode": "simulation"}' | python3 -m json.tool

# Puis inspecter le step de l'agent dans la DB
sqlite3 backend/test.db "
SELECT output_payload FROM agent_steps
WHERE run_id = <run_id> AND agent_name = '<agent_name>';
" | python3 -m json.tool
```

## Validation

- [ ] `pytest tests/unit/test_no_french_in_production.py -v` — PASS (aucun français dans les prompts)
- [ ] `pytest tests/unit/test_prompt_placeholders_gh19.py -v` — PASS (aucun `<MISSING:...>`)
- [ ] `pytest tests/unit/test_prompt_registry.py -v` — PASS
- [ ] `pytest tests/unit/test_agentscope_schemas.py -v` — PASS (schéma toujours satisfait)
- [ ] Le champ nouveau/modifié apparaît dans `output_payload` d'un run simulation avec la valeur attendue

## Anti-Patterns

- Ne jamais inclure de texte en français dans un prompt de production — le test `test_no_french_in_production.py` bloquera.
- Ne jamais supprimer les critères de sortie structurée sans mettre à jour le schéma Pydantic correspondant.
- Ne jamais ajouter `"recommend BUY/SELL"` dans le prompt d'un analyste Phase 1 (philosophie LLM-First).
- Ne pas modifier `prompts.py` si la DB contient déjà un prompt pour cet agent — la modification sera silencieusement ignorée.

## Source Anchors

- `backend/app/services/agentscope/prompts.py` — `AGENT_PROMPTS` dict, prompts fallback des 8 agents
- `backend/tests/unit/test_no_french_in_production.py` — validation : aucun français dans les prompts
- `backend/tests/unit/test_prompt_placeholders_gh19.py` — validation : placeholders SafeDict résolus
- `backend/tests/unit/test_prompt_registry.py` — tests de cohérence du registre de prompts
- `backend/app/services/agentscope/schemas.py` — schémas Pydantic à maintenir en cohérence avec les prompts
- `docs/decision-pipeline.md` — philosophie LLM-First : règles de contenu par agent et par phase
