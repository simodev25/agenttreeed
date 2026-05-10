# Index de Documentation Projet - Kairos Mesh

> **Date de generation :** 2026-05-09
> **Mode :** Scan initial (deep)
> **Scan level :** Deep (lecture des fichiers critiques)

---

## Vue d'Ensemble du Projet

- **Nom :** Kairos Mesh
- **Type :** Monorepo multi-parts (3 parties)
- **Langage principal :** Python (backend), TypeScript (frontend)
- **Architecture :** Pipeline multi-agents en 4 phases + moteur de risque deterministe

### Parties du Projet

| Partie | Type | Stack | Racine |
|--------|------|-------|--------|
| **Backend** | backend | Python, FastAPI 0.116, SQLAlchemy 2.0, Celery 5.5, AgentScope 1.0 | `backend/` |
| **Frontend** | web | React 19, Vite 7, Tailwind CSS 4, MUI 7, TypeScript 5.9 | `frontend/` |
| **Infrastructure** | infra | Docker Compose, Prometheus 2.55, Grafana 11.2, Tempo 2.6, Helm | `infra/` |

### Metriques Cles

| Metrique | Valeur |
|----------|--------|
| Endpoints REST | 48 |
| Endpoints WebSocket | 5 |
| Tables base de donnees | 18 |
| Migrations Alembic | 12 |
| Pages frontend | 9 |
| Composants frontend | 20+ |
| Hooks personnalises | 6 |
| Services Docker | 8 |
| Dashboards Grafana | 5 |

---

## Documentation Generee (BMad Scan)

### Architecture et Design

- [Vue d'ensemble du projet](./project-overview.md) -- Resume, stack technologique, architecture
- [Architecture Backend](./architecture-backend.md) -- Pipeline multi-agents, services critiques, decisions de design
- [Architecture d'integration](./integration-architecture.md) -- Topologie services, points d'integration, flux de donnees, dev vs prod
- [Arborescence source annotee](./source-tree-analysis.md) -- Structure complete du projet avec annotations

### References Techniques

- [Contrats API Backend](./api-contracts-backend.md) -- 48 endpoints REST + 5 WebSocket, tous domaines
- [Modeles de donnees Backend](./data-models-backend.md) -- 18 tables, relations, migrations
- [Inventaire composants Frontend](./component-inventory-frontend.md) -- Pages, composants, hooks, types, feature flags

### Guides

- [Guide de developpement](./development-guide.md) -- Installation, commandes Make, variables env, tests, conventions, CI/CD, deploiement

---

## Documentation Existante (Pre-scan)

### Architecture et Conception

- [Architecture systeme](./architecture.md) -- Couches systeme, frontieres de confiance (document original)
- [Agents](./agents.md) -- Reference technique des 8 agents du pipeline
- [Pipeline de decision](./decision-pipeline.md) -- Scoring, seuils, mecaniques de debat
- [Flux d'execution](./runtime-flow.md) -- Execution etape par etape d'un run
- [Execution](./execution.md) -- Phase 4 : preflight checks, simulation vs paper vs live
- [Memoire](./memory.md) -- Stockage et acces information agents

### Guides Existants

- [Quickstart](./quickstart.md) -- Demarrage rapide (simulation avec Docker)
- [Getting Started](./getting-started.md) -- Configuration complete dev local
- [Configuration](./configuration.md) -- Reference variables d'environnement
- [Paper vs Live](./paper-vs-live.md) -- Differences modes execution
- [Guide UI](./ui-guide.md) -- Guide interface utilisateur
- [Onboarding](./onboarding.md) -- Kit installation et integration

### Gouvernance et Operations

- [Risque et gouvernance](./risk-and-governance.md) -- Moteur de risque, limites, gates
- [Observabilite](./observability.md) -- Metriques, traces, dashboards
- [Limitations](./limitations.md) -- Limites connues, contraintes operationnelles
- [Modele operationnel](./operating-model.md) -- Principes de livraison spec-driven

### Outils et Processus

- [Usage OpenCode](./opencode-usage.md) -- Configuration et utilisation OpenCode
- [Generation skills projet](./generate-project-skills.md) -- Commande generation skills agents

### Plans et Specs (docs/superpowers/)

- [Migration AgentScope](./superpowers/plans/2026-03-28-agentscope-migration.md)
- [Nettoyage nommage domaine](./superpowers/plans/2026-03-30-domain-naming-cleanup.md)
- [Risk Manager Portfolio](./superpowers/plans/2026-04-01-risk-manager-portfolio.md)
- [Hardening Strategy Engine](./superpowers/plans/2026-04-03-strategy-engine-hardening.md)
- [Open Source Readiness](./superpowers/plans/2026-04-10-open-source-readiness.md)
- [Refactor Documentation](./superpowers/plans/2026-04-10-documentation-refactor.md)
- [Integration MCP Externe](./superpowers/plans/2026-04-19-external-mcp-integration.md)

---

## Gouvernance Projet

### Conventions

- [Nommage](../governance/conventions/naming.md)
- [Branching](../governance/conventions/branching.md)
- [Artefacts](../governance/conventions/artifacts.md)

### Cycle de vie

- [Cycle de changement](../governance/lifecycle/change-lifecycle.md)
- [Stage gates](../governance/lifecycle/stage-gates.md)

### Politiques

- [Permissions agents](../governance/policies/agent-permissions.yaml)
- [Politique de review](../governance/policies/review-policy.yaml)
- [Politique effets de bord](../governance/policies/side-effects-policy.yaml)

---

## Templates

- [Template spec](../templates/spec.template.md)
- [Template plan d'implementation](../templates/implementation-plan.template.md)
- [Template plan de test](../templates/test-plan.template.md)
- [Template description PR](../templates/pr-description.template.md)
- [Template notes PM](../templates/pm-notes.template.yaml)

---

## Changements Documentes

### GH-19 : Fix Missing Prompt Placeholders

- [Spec](../doc/changes/2026-04/2026-04-25--GH-19--fix-missing-prompt-placeholders/chg-GH-19-spec.md)
- [Plan](../doc/changes/2026-04/2026-04-25--GH-19--fix-missing-prompt-placeholders/chg-GH-19-plan.md)
- [Plan de test](../doc/changes/2026-04/2026-04-25--GH-19--fix-missing-prompt-placeholders/chg-GH-19-test-plan.md)

### GH-20 : Fix Risk Engine Notional Exposure

- [Spec](../doc/changes/2026-04/2026-04-25--GH-20--fix-risk-engine-notional-exposure/chg-GH-20-spec.md)
- [Plan](../doc/changes/2026-04/2026-04-25--GH-20--fix-risk-engine-notional-exposure/chg-GH-20-plan.md)
- [Plan de test](../doc/changes/2026-04/2026-04-25--GH-20--fix-risk-engine-notional-exposure/chg-GH-20-test-plan.md)

---

## Pour Demarrer

1. Lire la [vue d'ensemble du projet](./project-overview.md) pour comprendre l'architecture globale
2. Suivre le [guide de developpement](./development-guide.md) pour configurer l'environnement
3. Consulter les [contrats API](./api-contracts-backend.md) pour comprendre les endpoints
4. Voir les [modeles de donnees](./data-models-backend.md) pour la structure de la base
5. Explorer l'[inventaire composants](./component-inventory-frontend.md) pour le frontend

---

## Prochaines Etapes BMad

Pour planifier de nouvelles fonctionnalites, utiliser ce index comme reference lors de :
- **Creation PRD** (`bmad-create-prd`) -- pointer vers ce fichier comme contexte projet
- **Creation Architecture** (`bmad-create-architecture`) -- pour de nouvelles decisions architecturales
- **Creation Epics & Stories** (`bmad-create-epics-and-stories`) -- pour decomposer le backlog

---

*Fichier d'etat : [project-scan-report.json](./project-scan-report.json)*
