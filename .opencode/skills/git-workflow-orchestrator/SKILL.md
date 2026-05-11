---
name: git-workflow-orchestrator
description: "Use when exécutant la phase commit/PR du pipeline Samourai — orchestrates code review → tests → conventional commit → PR creation avec checkpoints utilisateur. Renforce @committer et @pr-manager."
---

# Git Workflow Orchestrator

Orchestre le pipeline git complet (review → tests → commit → PR) avec checkpoints explicites avant chaque action irréversible. Adapté pour le cycle de delivery Samourai (`/commit` + `/pr`).

<HARD-GATE>
Ne jamais exécuter d'opérations git (commit, push, PR) sans checkpoint utilisateur explicite préalable. Chaque phase produit un fichier de sortie avant de passer à la suivante.
</HARD-GATE>

## Inputs

- État git courant (branche, diff, historique récent)
- Résultats de review et de tests nécessaires aux checkpoints
- Convention de commit/branche applicable au repo
- Validation explicite utilisateur à chaque checkpoint bloquant

## Activation dans Samourai

Ce skill est activé automatiquement lors de :
- `/commit` — phase 9 du pipeline (commit → push)
- `/pr` — phase 10 du pipeline (PR creation)
- `/check` → failure → remediation → re-commit

## Pipeline en 5 phases

```
Phase 1: Pré-commit review  → .git-workflow/01-code-review.md
Phase 2: Tests & validation  → .git-workflow/03-test-results.md
Phase 3: Commit message      → .git-workflow/06-commit-messages.md  [Conventional Commits]
Phase 4: Push & branch       → .git-workflow/08-push-results.md
Phase 5: PR creation         → .git-workflow/10-pr-created.md
```

Chaque phase se termine par un **CHECKPOINT** — arrêt et attente de validation utilisateur.

## Règles d'exécution

1. **Ordre strict** — ne pas sauter ni fusionner des étapes
2. **Fichiers de sortie obligatoires** — chaque étape écrit dans `.git-workflow/` avant de continuer
3. **Checkpoints bloquants** — STOP et attente d'approbation explicite avant toute action irréversible
4. **Halt on failure** — en cas d'erreur, STOP + présentation du problème à l'utilisateur
5. **Conventional Commits** — format obligatoire : `<type>(<scope>): <subject>`

## Phase 1 — Pré-commit review

Avant tout commit, analyser les changements :

```bash
git status
git diff --stat
git diff
git log --oneline -10
git branch --show-current
```

Sauvegarder dans `.git-workflow/00-git-context.md`.

Vérifier :
1. Violations de style
2. Vulnérabilités de sécurité
3. Problèmes de performance
4. Gestion d'erreurs manquante
5. Code debug non retiré (`console.log`, `print`, `debugger`)
6. Secrets ou credentials exposés

Sauvegarder dans `.git-workflow/01-code-review.md`.

### CHECKPOINT 1

```
Pré-commit review terminé.
Issues: [X critical, Y high, Z medium, W low]

1. Approuver → continuer vers les tests
2. Corriger d'abord → adresser les issues critical/high
3. Pause → sauvegarder et arrêter
```

## Phase 2 — Tests & validation

Si `--skip-tests` est passé, documenter le skip et passer en Phase 3.

Exécuter les tests du projet selon les conventions du repo :
- Tests unitaires
- Tests d'intégration
- Vérification de couverture

Sauvegarder résultats dans `.git-workflow/03-test-results.md`.

### CHECKPOINT 2

```
Tests terminés.
Résultats: [X passed, Y failed, Z skipped]
Couverture: [résumé]

1. Approuver → continuer vers le commit message
2. Corriger les tests en échec
3. Pause
```

## Phase 3 — Commit message (Conventional Commits)

Analyser les changements et catégoriser selon [Conventional Commits](https://www.conventionalcommits.org/) :

**Types** : `feat` | `fix` | `docs` | `style` | `refactor` | `perf` | `test` | `build` | `ci` | `chore` | `revert`

Format obligatoire :
```
<type>(<scope>): <subject>          ← 50 chars max
<blank line>
<body>                              ← what & why, not how
<blank line>
BREAKING CHANGE: <description>     ← si applicable
Refs: #<issue>
```

Sauvegarder dans `.git-workflow/06-commit-messages.md`.

### CHECKPOINT 3

```
Commit message proposé :
[afficher le message]

1. Approuver → continuer vers push
2. Modifier → indiquer les changements
3. Pause
```

## Phase 4 — Push & branch

Validation pré-push :
- Branch name conforme (`feat/<ref>/<slug>`, `fix/...`, `chore/...`)
- Pas de conflits avec la branche cible
- Pas de données sensibles dans les commits
- Règles de protection de branche respectées

Afficher les commandes git planifiées et demander confirmation :

```
Opérations git planifiées :
  git add <files>
  git commit -m "<message>"
  git push origin <branch> -u

1. Exécuter
2. Modifier
3. Annuler
```

### CHECKPOINT 4

```
Push terminé.
1. Approuver → créer la PR
2. Pause
```

## Phase 5 — PR creation

Générer une description PR complète incluant :
- Résumé des changements (quoi et pourquoi)
- Type de changement
- Tests effectués
- Breaking changes si applicable
- Checklist reviewer
- Références aux issues/tickets

Créer la PR via `gh pr create` avec le template généré.

Afficher et confirmer avant exécution.

## Intégration avec les agents Samourai

| Agent Samourai | Rôle dans ce skill |
|---|---|
| `@committer` | Exécute Phase 3 + Phase 4 |
| `@pr-manager` | Exécute Phase 5 |
| `@reviewer` | Alimente Phase 1 avec son rapport |
| `@runner` | Alimente Phase 2 avec les résultats de tests |

## État de session

Maintenir `.git-workflow/state.json` :
```json
{
  "status": "in_progress",
  "current_phase": 1,
  "completed_phases": [],
  "started_at": "ISO_TIMESTAMP"
}
```

Si une session existante est détectée au démarrage :
```
Session git-workflow trouvée (phase: X)
1. Reprendre depuis la phase X
2. Recommencer depuis le début
```

## Acceptance Criteria

- Les 5 phases sont exécutées dans l'ordre strict sans saut ni fusion
- Chaque phase écrit son artefact dans `.git-workflow/` avant la suivante
- Aucun commit/push/PR n'est exécuté sans validation utilisateur explicite
- Le commit respecte Conventional Commits et la PR contient les sections attendues
