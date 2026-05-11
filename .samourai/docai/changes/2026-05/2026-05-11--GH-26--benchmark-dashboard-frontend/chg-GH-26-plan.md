---
id: chg-GH-26-benchmark-dashboard-frontend
status: Proposed
created: 2026-05-11T14:25:13Z
last_updated: 2026-05-11T14:25:13Z
owners: ["mbensass"]
service: frontend
labels: ["type:feature", "in-progress", "change"]
links:
  change_spec: ./chg-GH-26-spec.md
summary: >
  Livrer une interface dashboard benchmark intégrée au SPA React existant pour lister les fixtures,
  lancer des runs, visualiser les scores V1 par modèle et comparer plusieurs modèles sur une même
  fixture, tout en respectant le design system actuel.
version_impact: minor
---

# IMPLEMENTATION PLAN — GH-26: Agent Benchmark System — Lot B : Dashboard Frontend

## Context and Goals

Ce plan décline en phases implémentables le changement **GH-26** (Lot B) pour ajouter au frontend une page `/benchmark` et ses composants associés, en s'appuyant sur les patterns existants (notamment `BacktestsPage.tsx`), le client REST `frontend/src/api/client.ts`, et le design system documenté dans `frontend/UI_DOCUMENTATION.md`.

**Classification (Project Profile)** : feature (mode Build).

**Objectifs (depuis la spec)** :

- Exposer la fonctionnalité via la navigation principale (F-1, AC-F1-1).
- Lister les fixtures, permettre la sélection (F-2, AC-F2-1/2).
- Permettre de lancer un run (F-3, AC-F3-1/2).
- Afficher les résultats V1 et la coloration par seuil (F-4, AC-F4-1/2).
- Comparer 2+ modèles côte à côte (F-5, AC-F5-1).
- Afficher le détail d'un run (cases/attempts) (F-6, AC-F6-1).
- Typer l'ensemble des objets benchmark côté TS sans casser le build (F-7, AC-F7-1, NFR-3).

**Open questions (à résoudre pendant l'implémentation, sans inventer le contrat)** :

- OQ-1 : format exact de `GET /benchmark/runs/{id}/results` (agrégé par modèle vs par case/attempt).
- OQ-2 : numéro NODE et libellé exact de l'item "BENCHMARK" dans la sidebar.
- OQ-3 : confirmer que la création de fixture via UI reste hors périmètre.
- OQ-4 : pas de polling automatique des runs (confirmé differé) — uniquement refresh manuel.
- OQ-5 : confirmer les seuils de couleur V1 (0.7 / 0.4).

## Scope

### In Scope

- **F-7** : ajout de types TypeScript benchmark isolés (DEC-3) dans `frontend/src/types/benchmark.ts`.
- **F-1** : ajout d'un item sidebar + ajout de la route `/benchmark` en lazy loading.
- **F-2** : liste des fixtures (GET `/benchmark/fixtures`) et affichage vide (AC-F2-2).
- **F-3** : formulaire de création run (POST `/benchmark/runs`) avec `ButtonSpinner` pendant soumission.
- **F-4** : tableau résultats (GET `/benchmark/runs/{id}/results`) + coloration conditionnelle.
- **F-5** : vue comparaison multi-modèles (2+), meilleur score mis en évidence.
- **F-6** : détail run (GET `/benchmark/runs/{id}`) avec cases + attempts.
- Respect du design system (`theme.css` tokens / classes) et des contraintes maintenabilité (NFR-5, NFR-6, NFR-7).

### Out of Scope

- Toute modification backend (GH-24) ou du contrat API (Non-objectifs, 7.2).
- Charts avancés (radar/heatmap), scoring V2, export, tests E2E Playwright.
- Création de fixture via UI.

### Constraints

- **Additif uniquement** sur `Layout.tsx`, `App.tsx`, `api/client.ts` (compat ascendante 8.5).
- Pas de nouvelle dépendance npm.
- Aucun composant > 400 LOC (NFR-6) : extraire en sous-composants si nécessaire.
- Accessibilité : inputs/boutons avec label visible ou `aria-label` (NFR-7).
- Branching : la branche GH-26 est basée sur GH-24 (DEC-1) (risque RSK-2).

### Risks

- **RSK-1** : erreurs TS pré-existantes bloquant le build. Mitigation : types isolés dans `types/benchmark.ts` (DEC-3), ajout additif uniquement.
- **RSK-2** : divergence si GH-24 bouge. Mitigation : rebase régulier + garder le client API tolérant (champs `unknown` si non stabilisés).
- **RSK-3** : contrat API results non stabilisé. Mitigation : typer progressivement + marquer champs inconnus `unknown` + commentaires TODO.
- **RSK-4** : régression routes existantes. Mitigation : routage additif + smoke tests manuels des routes clés.

### Success Metrics

- `npm run build` sans nouvelle erreur TypeScript (NFR-3, KPI Build).
- Types benchmark couvrant 100% des champs consommés par l'UI (KPI types).
- Route `/benchmark` accessible (KPI route).

## Phases

### Phase 1: Types TypeScript + Client API

**Goal**: Poser un contrat TS isolé (DEC-3) et des méthodes API benchmark additifs dans `client.ts`.

**Tasks**:

- [x] **1.1** Créer `frontend/src/types/benchmark.ts` avec les types minimaux : `ModelSpec`, `BenchmarkFixture`, `BenchmarkRun`, `BenchmarkCase`, `BenchmarkAttempt`, `BenchmarkScoresV1`, `BenchmarkRunResults` (DM-1  DM-7). *(<=2h)* (types ajoutés dans `frontend/src/types/benchmark.ts`)
- [x] **1.2** Ajouter les méthodes API benchmark dans `frontend/src/api/client.ts` (additif) : `listBenchmarkFixtures`, `getBenchmarkFixture`, `listBenchmarkRuns`, `createBenchmarkRun`, `getBenchmarkRun`, `getBenchmarkRunResults` en utilisant `request<T>()`. *(<=2h)* (méthodes API benchmark ajoutées en mode additif)
- [x] **1.3** Dclarer/ajuster les types de rponse  incertains avec `unknown` + commentaires TODO liés  OQ-1/RSK-3, sans casser le build. *(<=2h)* (types tolérants `extra/raw` + TODO OQ-1/RSK-3)

**Acceptance Criteria**:

- Must: AC-F7-1 (types benchmark n'introduisent pas d'erreurs TS).
- Must: compat ascendante 8.5 (ajout uniquement, pas de modification des methodes existantes).

**Files and modules**:

- `frontend/src/types/benchmark.ts` (new)
- `frontend/src/api/client.ts` (updated)

**Tests**:

- `cd frontend && npm run build` (smoke pour TS)

**Completion signal**: `feat(GH-26): add benchmark TS types and API client methods`

---

### Phase 2: Route + Navigation (App.tsx, Layout.tsx)

**Goal**: Rendre la page benchmark accessible (F-1) via une route lazy et un item sidebar cohérent.

**Tasks**:

- [ ] **2.1** Créer un squelette `frontend/src/pages/BenchmarkPage.tsx` (titre + surfaces) aligné design system. *(<=2h)*
- [ ] **2.2** Enregistrer la route `/benchmark` dans `frontend/src/App.tsx` via `React.lazy()` + `withLayout(...)`. *(<=2h)*
- [ ] **2.3** Ajouter l'item "BENCHMARK" dans `frontend/src/components/Layout.tsx` (`navItems`) avec icône Lucide + `node`  dclarer (OQ-2). *(<=2h)*

**Acceptance Criteria**:

- Must: AC-F1-1 (clic sidebar  ouvre `/benchmark` sans erreur, titre visible).

**Files and modules**:

- `frontend/src/pages/BenchmarkPage.tsx` (new)
- `frontend/src/App.tsx` (updated)
- `frontend/src/components/Layout.tsx` (updated)

**Tests**:

- Navigation manuelle: login  sidebar  page BENCHMARK.

**Completion signal**: `feat(GH-26): add /benchmark route and sidebar entry`

---

### Phase 3: Page BenchmarkPage — liste fixtures

**Goal**: Implémenter la liste fixtures (F-2) avec gestion loading/empty/error selon les patterns de `BacktestsPage.tsx`.

**Tasks**:

- [ ] **3.1** Implémenter le chargement initial `GET /benchmark/fixtures` avec `useAuth()` + gestion `loading/error` (pattern `request<T>()` / ErrorBoundary). *(<=2h)*
- [ ] **3.2** Rendre un tableau/liste fixtures : nom, `agent_key`, `scenario_type`, date de création, avec styles `.hw-surface*` et classes text. *(<=2h)*
- [ ] **3.3** Implémenter l'état vide : message "Aucune fixture disponible" (AC-F2-2). *(<=2h)*

**Acceptance Criteria**:

- Must: AC-F2-1 (champs requis visibles).
- Must: AC-F2-2 (empty state).
- Should: NFR-1 (chargement < 2s en local : rendu progressif + loading state).

**Files and modules**:

- `frontend/src/pages/BenchmarkPage.tsx` (updated)

**Tests**:

- Test manuel: fixtures présentes vs 0 fixtures.

**Completion signal**: `feat(GH-26): implement benchmark fixtures list`

---

### Phase 4: Formulaire lancement run

**Goal**: Permettre la cration d'un run (F-3)  partir d'une fixture, avec UX de soumission.

**Tasks**:

- [ ] **4.1** Ajouter un panneau "RUN_CONFIGURATION" : slection fixture + champs `repeat_count` (optionnel) + `tags` (optionnel). *(<=2h)*
- [ ] **4.2** Ajouter l'édition des `model_specs` en liste (ajout/suppression ligne) avec validation minimale (au moins 1 modèle + provider/model_name). *(<=2h)*
- [ ] **4.3** Sur submit, appeler `POST /benchmark/runs` et afficher `ButtonSpinner` pendant soumission, puis rafrachir la liste des runs associés  la fixture. *(<=2h)*

**Acceptance Criteria**:

- Must: AC-F3-1 (POST mis + spinner).
- Must: AC-F3-2 (nouveau run apparaît après succès).

**Files and modules**:

- `frontend/src/pages/BenchmarkPage.tsx` (updated)
- (optionnel si extraction) `frontend/src/pages/benchmark/*` (new)

**Tests**:

- Test manuel: soumission valide/invalide, désactivation double-submit, erreurs API visibles.

**Completion signal**: `feat(GH-26): add benchmark run launch form`

---

### Phase 5: Tableau résultats + scores V1

**Goal**: Afficher les résultats agrégés (F-4) et la coloration des scores V1.

**Tasks**:

- [ ] **5.1** Ajouter une liste/table des runs de la fixture slectionnée (via `GET /benchmark/runs` filtrés client-side si pas de filtre serveur), slection d'un run. *(<=2h)*
- [ ] **5.2** Charger `GET /benchmark/runs/{id}/results` et rendre un tableau : modèle  5 métriques V1 + `overall` (AC-F4-1). *(<=2h)*
- [ ] **5.3** Implémenter la fonction de coloration (vert/orange/rouge) selon seuils (AC-F4-2) en utilisant les tokens/classes existants (`text-success`, `text-warning`, `text-danger` ou classes Tailwind conformes). *(<=2h)*

**Acceptance Criteria**:

- Must: AC-F4-1.
- Must: AC-F4-2.
- Must: AC-NFR5-1 (tokens, pas de valeurs hardcodées hors design system).

**Files and modules**:

- `frontend/src/pages/BenchmarkPage.tsx` (updated)
- (optionnel) `frontend/src/utils/benchmarkScores.ts` (new) pour helpers de coloration/format

**Tests**:

- Test manuel: run terminé  résultats visibles; cas score  0.39/0.4/0.7.

**Completion signal**: `feat(GH-26): render benchmark V1 results table with score coloring`

---

### Phase 6: Vue comparaison modèles

**Goal**: Comparer 2+ modèles (F-5) sur une même fixture.

**Tasks**:

- [ ] **6.1** Ajouter une slection multi-modèle (checkbox)  partir des résultats/runs, avec CTA "COMPARER" activé  partir de 2 slections. *(<=2h)*
- [ ] **6.2** Rendre une vue comparaison : tableau métriques  colonnes modèles, meilleur score par ligne mis en évidence. *(<=2h)*
- [ ] **6.3** Ajouter une action "Retour" / fermeture comparaison pour revenir aux résultats standard. *(<=2h)*

**Acceptance Criteria**:

- Must: AC-F5-1.

**Files and modules**:

- `frontend/src/pages/BenchmarkPage.tsx` (updated)

**Tests**:

- Test manuel: comparaison de 2 et 3 modèles, tie-breaks (scores égaux) affichage stable.

**Completion signal**: `feat(GH-26): add benchmark model comparison view`

---

### Phase 7: Détail run (attempts)

**Goal**: Afficher le détail run (F-6) : cases et attempts avec statuts/latence/tokens/erreurs.

**Tasks**:

- [ ] **7.1** Ajouter un panneau détail (pattern `ExpansionPanel`)  l'ouverture d'un run slectionné, avec appel `GET /benchmark/runs/{id}`. *(<=2h)*
- [ ] **7.2** Rendre la liste des `BenchmarkCase` avec statut + indicateurs (latence, tokens) et afficher les `BenchmarkAttempt` imbriqués (peut être un sous-panel). *(<=2h)*
- [ ] **7.3** Gérer l'affichage des erreurs (text prformaté, pas de rendu HTML) et ajouter labels/`aria-label` pour interactions (NFR-7). *(<=2h)*

**Acceptance Criteria**:

- Must: AC-F6-1.

**Files and modules**:

- `frontend/src/pages/BenchmarkPage.tsx` (updated)

**Tests**:

- Test manuel: run avec erreurs vs run OK; attempts multiples (`repeat_count`).

**Completion signal**: `feat(GH-26): add benchmark run detail (cases and attempts)`

---

### Phase 8: Vérification build + polish

**Goal**: Stabiliser, respecter les NFRs, et prparer la release (spec reconciliation + version bump).

**Tasks**:

- [ ] **8.1** Refactor si nécessaire pour respecter NFR-6 (composants < 400 LOC) via extraction de sous-composants `pages/benchmark/*`. *(<=2h)*
- [ ] **8.2** Passer en revue design system : tokens, typographie, classes, pas de couleurs hex hardcodées, messages/labels cohérents. *(<=2h)*
- [ ] **8.3** Exécuter `cd frontend && npm run build` et corriger les erreurs TS/lint bloquantes liées  GH-26 (NFR-3, NFR-4). *(<=2h)*
- [ ] **8.4** Smoke test manuel des routes existantes (au minimum `/`, `/terminal`, `/backtests`, `/connectors`, `/strategies`) pour couvrir RSK-4. *(<=2h)*
- [ ] **8.5** Version bump (convention repo) si requis pour une release applicative (NPM/package/app version), sinon documenter "no version bump required" dans PR. *(<=2h)*
- [ ] **8.6** Spec reconciliation : vérifier que l'implémentation respecte AC/NFR; mettre  jour la spec si divergence découverte (sans inventer). *(<=2h)*

**Acceptance Criteria**:

- Must: AC-NFR3-1.
- Must: AC-NFR5-1.

**Files and modules**:

- `frontend/src/pages/BenchmarkPage.tsx` (updated)
- `frontend/src/pages/benchmark/*` (new, si extraction)

**Tests**:

- `cd frontend && npm run build`

**Completion signal**: `chore(GH-26): polish benchmark dashboard and verify build`

---

### Phase 9: Code Review (Analysis)

**Goal**: Obtenir un audit (couverture, cohérence, risques) avant finalisation.

**Tasks**:

- [ ] **9.1** Passer `@reviewer` : vérification code vs spec (AC/NFR), patterns frontend, accessibilité, robustesse erreurs API. *(<=2h)*

**Acceptance Criteria**:

- Must: rapport review avec statut PASS ou liste de remédiations actionnables.

**Files and modules**:

- (aucun obligatoire; remédiations peuvent impacter `BenchmarkPage`/API/types)

**Tests**:

- Rejouer `npm run build` si remédiations.

**Completion signal**: `docs(GH-26): add code review notes for benchmark dashboard`

---

### Phase 10: Post-Code Review Fixes (conditional)

**Goal**: Adresser les remarques de review si nécessaire.

**Tasks**:

- [ ] **10.1** Appliquer les fix listés par la review (si FAIL/notes), en gardant des tranches <2h (split si besoin). *(<=2h)*

**Acceptance Criteria**:

- Must: Tous les items bloquants de review résolus ou documentés.

**Files and modules**:

- Selon remédiations.

**Tests**:

- `cd frontend && npm run build`

**Completion signal**: `fix(GH-26): address review feedback for benchmark dashboard`

---

### Phase 11: Finalize and Release

**Goal**: Clôturer la delivery et prparer la PR.

**Tasks**:

- [ ] **11.1** Vérifier que tous les AC (F-1..F-7) sont satisfaits via une checklist manuelle récap. *(<=2h)*
- [ ] **11.2** Version bump final (si applicable) + vérifier cohérence changelog/notes. *(<=2h)*
- [ ] **11.3** Spec reconciliation finale (alignement spec/plan/impl) et mise  jour des artefacts si écart. *(<=2h)*

**Acceptance Criteria**:

- Must: Build frontend OK.
- Must: Plan checkboxes prêtes  être cochées pendant exécution.

**Files and modules**:

- (selon version bump et doc sync)

**Tests**:

- `cd frontend && npm run build`

**Completion signal**: `chore(GH-26): finalize benchmark dashboard release prep`

## Test Scenarios

| ID | Scénario | Phases | AC |
|----|----------|--------|----|
| TS-1 | La route `/benchmark` est accessible depuis la sidebar et affiche un titre | 2 | AC-F1-1 |
| TS-2 | Fixtures présentes : la liste affiche nom, agent_key, scenario_type, created_at | 3 | AC-F2-1 |
| TS-3 | Aucune fixture : message "Aucune fixture disponible" | 3 | AC-F2-2 |
| TS-4 | Lancement run : validation modèle min + POST + spinner pendant soumission | 4 | AC-F3-1 |
| TS-5 | Après succès POST : le run apparaît dans la liste | 4 | AC-F3-2 |
| TS-6 | Résultats run : 5 métriques + overall par modèle | 5 | AC-F4-1 |
| TS-7 | Coloration scores : ef725 pour 70.7, orange pour 0.4–0.69, rouge <0.4 | 5 | AC-F4-2 |
| TS-8 | Comparaison : slection 2+ modèles  tableau comparaison + meilleur score par ligne | 6 | AC-F5-1 |
| TS-9 | Détail run : cases + attempts avec statut/latence/tokens/erreurs | 7 | AC-F6-1 |
| TS-10 | Build : `npm run build` ne rajoute pas d'erreur TS | 1,8 | AC-F7-1, AC-NFR3-1 |
| TS-11 | Design system : pas de couleurs hardcodées, composants utilisent tokens/classes existants | 5,8 | AC-NFR5-1 |

## Artifacts and Links

| Artifact | Location | Type |
|----------|----------|------|
| Change specification | `./chg-GH-26-spec.md` | Spec |
| Implementation plan | `./chg-GH-26-plan.md` | Plan |
| API client patterns | `../../../../frontend/src/api/client.ts` | Reference |
| Page pattern | `../../../../frontend/src/pages/BacktestsPage.tsx` | Reference |
| UI design system | `../../../../frontend/UI_DOCUMENTATION.md` | Reference |

## Plan Revision Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-11 | plan-writer | Plan initial (phases 1–11) aligné sur la spec GH-26 |

## Execution Log

| Phase | Status | Started | Completed | Commit | Notes |
|-------|--------|---------|-----------|--------|-------|
| Phase 1 | ✅ Complete | 2026-05-11 | 2026-05-11 | pending | Types benchmark + méthodes API ajoutés. Build frontend global échoue sur erreurs TS préexistantes hors GH-26 (log runner: `.samourai/tmpai/run-logs-runner/2026-05-11/163816-frontend-build-gh-26-phase-1.log`). |
