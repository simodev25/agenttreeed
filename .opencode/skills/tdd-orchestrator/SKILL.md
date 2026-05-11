---
name: tdd-orchestrator
description: "Use when implémentant une feature ou un bugfix dans /run-plan — enforce le cycle red-green-refactor, coordonne les agents de test, garantit test-first avant tout code de production. Renforce @coder et @test-plan-writer."
---

# TDD Orchestrator

Enforce la discipline Test-Driven Development dans le pipeline Samourai. Garantit le cycle red-green-refactor et coordonne les agents de test selon le plan de test `chg-<workItemRef>-test-plan.md`.

<HARD-GATE>
Ne jamais écrire du code de production avant qu'un test en échec existe pour la fonctionnalité. Toute tâche d'implémentation commence par un test rouge.
</HARD-GATE>

## Inputs

- `workItemRef` actif et tâches d'implémentation à exécuter
- Test plan associé (`chg-<workItemRef>-test-plan.md`)
- Contexte de code impacté et comportements attendus
- Résultats de tests (RED/GREEN) pour chaque cycle

## Outputs

- Cycles TDD tracés par tâche (RED → GREEN → REFACTOR)
- Tests ajoutés/ajustés avant code de production
- Évidence de validation (tests verts, couverture, absence de régression)

## Output Format

- Journal de cycle par tâche : test écrit, échec attendu, fix minimal, refactor, preuve de passage
- Statut final par tâche : DONE | BLOCKED avec preuve de tests

## Activation dans Samourai

Activé automatiquement lors de :
- `/run-plan <workItemRef>` — phase d'implémentation
- `/check-fix` — correction de tests en échec
- Toute tâche de `@coder` impliquant du code de production

## Le cycle obligatoire

```
Pour chaque tâche d'implémentation :

  1. RED   → écrire le test (qui échoue)
             └─ vérifier qu'il échoue pour la bonne raison
  2. GREEN  → écrire le minimum de code pour faire passer le test
             └─ résister à l'envie d'over-engineer
  3. REFACTOR → améliorer le code sans casser les tests
             └─ les tests restent verts tout au long

Ne jamais fusionner deux étapes. Ne jamais sauter RED.
```

## Intégration avec le plan Samourai

Lire `chg-<workItemRef>-test-plan.md` avant toute implémentation :

```markdown
Pour chaque tâche du plan :
  1. Identifier les tests couvrant cette tâche dans le test-plan
  2. Écrire ces tests EN PREMIER (RED)
  3. Implémenter la fonctionnalité (GREEN)
  4. Refactoriser (REFACTOR)
  5. Committer : tests + code dans le même commit
```

Si le test-plan est absent ou incomplet → signaler à `@pm` avant de continuer.

## Niveaux de tests

### Pyramide recommandée

```
        /\
       /E2E\          ← peu, lents, coûteux
      /------\
     /Intégra-\       ← quelques-uns, vérifient les contrats
    /  tion    \
   /------------\
  /   Unitaires  \    ← beaucoup, rapides, isolés
 /________________\
```

Ratio cible : 70% unitaires / 20% intégration / 10% E2E.

### Quand écrire quel type

| Situation | Type de test |
|---|---|
| Logique métier pure | Unitaire |
| Interaction entre composants | Intégration |
| Parcours utilisateur complet | E2E |
| Contrat d'API | Contrat |
| Régression d'un bug | Unitaire (reproduire le bug d'abord) |

## Pratiques TDD dans Samourai

### Test d'abord, toujours

```
✅ Correct :
  1. git diff → test rouge ajouté
  2. git diff → code de production ajouté
  3. tests verts

❌ Incorrect :
  1. git diff → code de production ajouté
  2. git diff → test ajouté (après coup)
```

### Granularité des tests

- Un test = un comportement (pas une méthode)
- Nommage : `should_<expected_behavior>_when_<condition>`
- Arrange / Act / Assert clairement séparés
- Pas de logique dans les tests (pas de if/loop)

### Doublures de test (mocks/stubs/fakes)

Utiliser les doublures pour isoler l'unité testée :

```
Fake   → implémentation simplifiée (in-memory DB)
Stub   → retourne des valeurs prédéfinies
Mock   → vérifie les interactions (appels)
Spy    → enregistre les appels sans modifier le comportement
```

Règle : mocker les dépendances externes (DB, API, filesystem), pas la logique métier.

## Anti-patterns à détecter et corriger

| Anti-pattern | Détection | Correction |
|---|---|---|
| Test-after | Code sans test rouge préalable | Revenir en arrière, écrire le test d'abord |
| Tests tautologiques | Test qui teste l'implémentation, pas le comportement | Réécrire en termes de comportement observable |
| Tests fragiles | Tests cassés par un refactoring sans changement de comportement | Tester l'interface, pas les internes |
| Fixture gods | Setup de test de 100+ lignes | Extraire des builders/factories |
| Test sans assertion | Test qui ne peut pas échouer | Ajouter une assertion significative |
| Tests lents | Tests unitaires > 100ms | Identifier et isoler les I/O |

## Vérification de couverture

Après chaque cycle red-green-refactor, vérifier :

```bash
# Selon le stack du projet
npm test -- --coverage
pytest --cov
go test -cover ./...
```

Seuils minimaux (à adapter selon le projet) :
- Nouveau code : > 80% de couverture
- Code critique (auth, paiement, sécurité) : > 95%

## Signaux de fin de cycle

Un cycle TDD est complet quand :
- [ ] Tous les tests du test-plan pour cette tâche sont verts
- [ ] Aucune régression sur les tests existants
- [ ] Le code est refactorisé (pas de duplication, nommage clair)
- [ ] La couverture cible est atteinte
- [ ] Commit effectué avec tests + code

## Coordination avec les agents Samourai

| Agent | Rôle TDD |
|---|---|
| `@test-plan-writer` | Définit les tests à écrire (avant l'implémentation) |
| `@coder` | Applique ce skill pour chaque tâche |
| `@reviewer` | Vérifie que RED a bien précédé GREEN |
| `@runner` | Exécute la suite de tests complète |
| `@fixer` | Répare les tests cassés en mode root-cause |

## Acceptance Criteria

- Chaque tâche commence par un test RED vérifié pour la bonne raison
- Le code GREEN reste minimal et limité au comportement testé
- Le refactor conserve tous les tests au vert sans régression
- Les preuves (résultats tests/couverture/commit) sont traçables pour chaque cycle

## Relationship to test-driven-development skill

| Aspect | tdd-orchestrator | test-driven-development |
|--------|-----------------|------------------------|
| **Purpose** | Pipeline integration — orchestrates TDD within `/run-plan` delivery | Developer discipline — teaches and enforces TDD principles |
| **Scope** | Multi-task orchestration across plan phases | Single task/feature TDD cycle |
| **Used by** | `@coder` during `/run-plan` execution | Any agent implementing code |
| **Coordinates** | `@coder`, `@fixer`, `@committer` agents | Self-contained, no agent coordination |

**When to use which**: Use `tdd-orchestrator` when executing plan phases in the Samourai pipeline. Use `test-driven-development` when implementing any code change (standalone or within a plan phase).
