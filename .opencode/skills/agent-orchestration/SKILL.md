---
name: agent-orchestration
description: "Use when @pm orchestre plusieurs agents en parallèle ou en séquence — patterns de coordination multi-agents, handoff de contexte, gestion de l'état partagé. Renforce @pm dans les phases de delivery complexes."
---

# Agent Orchestration

Patterns de coordination multi-agents pour le pipeline Samourai. Fournit les techniques de handoff, gestion de contexte et parallélisation entre agents.

## Inputs

- Référence du change (`workItemRef`) et phase en cours
- État des artefacts disponibles (spec, plan, test-plan, pm-notes)
- Dépendances entre tâches (parallèle possible vs séquentiel requis)
- Critères de succès attendus pour chaque délégation

## Outputs

- Plan de délégation clair (agents, ordre, parallélisation)
- Handoffs structurés avec contexte complet par agent
- État de coordination mis à jour avec décisions, blocages, et reprises

## Output Format

- Rapport de délégation par phase : agent ciblé, objectif, prérequis, critères de succès
- Statut consolidé : PASS/FAIL/BLOCKED/PARTIAL avec action de continuation

## Activation dans Samourai

Activé automatiquement par `@pm` lors de :
- Délégation parallèle (spec + test-plan + plan en simultané)
- Handoff séquentiel entre phases (coder → reviewer → fixer → reviewer)
- Gestion d'état entre sessions longues

## Patterns fondamentaux

### 1. Handoff de contexte entre agents

Lors de toute délégation, transmettre un bloc de contexte structuré :

```markdown
## Contexte pour <agent>

**workItemRef**: <ref>
**Phase**: <phase>
**Change folder**: <path>
**Artifacts disponibles**:
  - spec: <path ou "absent">
  - plan: <path ou "absent">
  - test-plan: <path ou "absent">
**Résultat attendu**: <description précise>
**Critères de succès**: <liste>
```

Ne jamais déléguer sans ce bloc. Un agent sans contexte produit un travail déconnecté.

### 2. Parallélisation (dispatching)

Quand plusieurs agents peuvent travailler indépendamment :

```
PARALLÈLE (safe) :
  @spec-writer + @test-plan-writer  →  pas de dépendance mutuelle
  @runner (tests) + @doc-syncer     →  pas de dépendance mutuelle

SÉQUENTIEL (obligatoire) :
  @spec-writer → @plan-writer        →  le plan dépend de la spec
  @coder → @reviewer                 →  la review dépend du code
  @reviewer (FAIL) → @coder → @reviewer  →  iteration review/fix
```

Règle : si l'output de A est l'input de B → séquentiel. Sinon → parallèle.

### 3. Boucle review/fix

Pattern d'itération pour la phase `review_fix` :

```
MAX_ITERATIONS = 3

boucle:
  1. @reviewer → rapport (PASS | FAIL + remediation tasks)
  2. si PASS → sortir
  3. si FAIL :
     a. vérifier que les tâches de remediation sont dans le plan
     b. @coder → implémenter la remediation
     c. @doc-syncer si changements impactent la doc
     d. itération++
     e. si itération > MAX_ITERATIONS → escalader à l'humain
  4. retour en 1
```

Ne jamais merger des itérations. Chaque cycle est une passe complète.

### 4. Gestion de l'état entre agents

Pour les livraisons longues (multi-sessions), maintenir l'état dans `chg-<workItemRef>-pm-notes.yaml` :

```yaml
phases:
  delivery:
    started: "2026-04-25T10:00:00Z"
    completed: null
    last_agent: "@coder"
    last_artifact: "chg-GH-42-plan.md phase 3/7"
```

Au reprise : lire les notes PM avant toute délégation pour éviter les doublons.

### 5. Délégation avec critères de succès explicites

Toujours définir ce qui constitue un succès **avant** de déléguer :

```markdown
## Critères de succès pour cette délégation

- [ ] Fichier <artifact> créé dans <path>
- [ ] Toutes les ACs de la spec couvertes
- [ ] Aucun TODO/TBD résiduel
- [ ] Commité avec message Conventional Commits
```

L'agent rapporte son résultat en cochant ces critères.

## Anti-patterns à éviter

| Anti-pattern | Problème | Correction |
|---|---|---|
| Déléguer sans contexte | L'agent invente des hypothèses | Toujours transmettre le bloc contexte |
| Paralléliser des tâches dépendantes | Race condition sur les artifacts | Vérifier les dépendances avant de paralléliser |
| Merger review + fix en une passe | Perte de traçabilité | Toujours deux appels distincts |
| Continuer après MAX_ITERATIONS | Boucle infinie | Escalader à l'humain avec diagnostic |
| Re-déléguer sans lire les notes PM | Travail dupliqué | Lire `pm-notes.yaml` avant chaque délégation |

## Signaux de coordination dans les rapports d'agents

Quand un agent retourne son rapport, lire ces signaux :

- `Status: PASS` → phase complète, passer à la suivante
- `Status: FAIL` → lire `remediation_tasks`, lancer cycle fix
- `Status: BLOCKED` → escalader à l'humain, documenter dans `blockers:`
- `Status: PARTIAL` → valider ce qui est fait, relancer pour le reste

## Intégration avec les phases Samourai

```
Phase 4 (artifact generation) :
  → Parallèle : @spec-writer ‖ @test-plan-writer
  → Séquentiel : attendre les deux → @plan-writer

Phase 5 (delivery) :
  → @coder (toutes les phases du plan)

Phase 6-7 (review loop) :
  → @doc-syncer (séquentiel après coder)
  → @reviewer (séquentiel)
  → si FAIL → @coder (remediation) → @reviewer (re-review)

Phase 8 (quality gates) :
  → @runner (parallel si plusieurs suites)
  → si FAIL → @fixer → @runner (re-run)
```

## Acceptance Criteria

- Chaque délégation contient un bloc de contexte structuré complet
- Les tâches dépendantes sont exécutées en séquentiel, les indépendantes en parallèle
- Les boucles review/fix respectent une passe complète par itération avec limite d'escalade
- L'état de coordination est traçable et synchronisé dans les artefacts prévus
