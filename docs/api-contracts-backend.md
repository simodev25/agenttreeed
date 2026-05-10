# Contrats API Backend — MultiAgentTrading

> **Date de génération :** 2026-05-09
> **Niveau de scan :** Exhaustif — 48 endpoints REST + 5 endpoints WebSocket
> **Préfixe REST :** `/api/v1`
> **Préfixe WebSocket :** `/ws` (monté sur la racine, hors `/api/v1`)

---

## Table des matières

1. [Health](#1-health)
2. [Auth](#2-auth)
3. [Runs](#3-runs)
4. [Trading](#4-trading)
5. [Connectors](#5-connectors)
6. [Prompts](#6-prompts)
7. [Backtests](#7-backtests)
8. [Analytics](#8-analytics)
9. [Portfolio](#9-portfolio)
10. [Strategies](#10-strategies)
11. [Governance](#11-governance)
12. [WebSocket](#12-websocket)
13. [Référentiel des rôles](#13-référentiel-des-rôles)

---

## 1. Health

> 1 endpoint — Vérification de la santé du service.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/health` | Non | Public | — | `{ api, postgres, llm, metaapi }` | Vérification santé du service (API, Postgres, LLM, MetaApi) |

---

## 2. Auth

> 3 endpoints — Authentification et gestion de session.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `POST` | `/auth/login` | Non | Public | `{ username, password }` | `{ token, user }` | Authentification utilisateur, retourne un JWT |
| `GET` | `/auth/me` | JWT | Tous | — | `{ id, username, role, ... }` | Profil de l'utilisateur courant |
| `POST` | `/auth/bootstrap-admin` | Non | Public | `{ username, password }` | `{ user, token }` | Création du premier admin (uniquement si 0 utilisateurs en base) |

---

## 3. Runs

> 4 endpoints — Gestion des runs d'analyse multi-agents.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/runs` | JWT | Tous | — | `[Run]` | Liste des runs d'analyse. Les admins voient tout, les autres uniquement leurs propres runs. Query : `limit`, `include_governance` |
| `POST` | `/runs` | JWT | SUPER_ADMIN, ADMIN, TRADER_OPERATOR, ANALYST | `{ pair, timeframe, mode, risk_percent, metaapi_account_ref }` | `Run` | Création et exécution d'un run. Query : `async_execution` |
| `GET` | `/runs/{run_id}` | JWT | Tous | — | `Run` (avec trace des étapes) | Détail d'un run avec la trace complète des étapes |
| `POST` | `/runs/{run_id}/cancel` | JWT | SUPER_ADMIN, ADMIN, TRADER_OPERATOR | — | `{ status }` | Annuler ou révoquer un run en cours |

---

## 4. Trading

> 10 endpoints — Opérations de trading, comptes broker et historique.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/trading/orders` | JWT | Tous | — | `[Order]` | Liste des ordres d'exécution. Query : `limit` |
| `GET` | `/trading/market-candles` | JWT | Tous | — | `[Candle]` | Bougies marché. Query : `account_ref`, `pair`, `timeframe`, `limit` |
| `GET` | `/trading/accounts` | JWT | Tous | — | `[Account]` | Liste des comptes MetaApi enregistrés |
| `POST` | `/trading/accounts` | JWT | SUPER_ADMIN, ADMIN | `{ account_ref, name, ... }` | `Account` | Enregistrer un nouveau compte MetaApi |
| `PATCH` | `/trading/accounts/{account_ref}` | JWT | SUPER_ADMIN, ADMIN | `{ name, ... }` | `Account` | Modifier les informations d'un compte MetaApi |
| `GET` | `/trading/account` | JWT | SUPER_ADMIN, ADMIN, TRADER_OPERATOR | — | `AccountInfo` | Informations du compte broker. Query : `account_ref` |
| `GET` | `/trading/positions` | JWT | Tous | — | `[Position]` | Positions ouvertes. Query : `account_ref` |
| `GET` | `/trading/open-orders` | JWT | Tous | — | `[Order]` | Ordres en attente. Query : `account_ref` |
| `GET` | `/trading/deals` | JWT | Tous | — | `[Deal]` | Historique des deals MetaApi. Query : `account_ref`, `days`, `limit`, `offset`. Feature flag : `ENABLE_METAAPI_REAL_TRADES_DASHBOARD` |
| `GET` | `/trading/history-orders` | JWT | Tous | — | `[HistoryOrder]` | Historique des ordres. Feature flag : `ENABLE_METAAPI_REAL_TRADES_DASHBOARD` |

---

## 5. Connectors

> 14 endpoints — Configuration des connecteurs externes, symboles, LLM et MCP.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/connectors` | JWT | SUPER_ADMIN, ADMIN | — | `[ConnectorConfig]` | Liste des configurations de connecteurs |
| `PUT` | `/connectors/{connector_name}` | JWT | SUPER_ADMIN, ADMIN | `{ config }` | `ConnectorConfig` | Modifier la configuration d'un connecteur |
| `POST` | `/connectors/{connector_name}/test` | JWT | SUPER_ADMIN, ADMIN | — | `{ success, message }` | Tester la connectivité d'un connecteur |
| `GET` | `/connectors/market-symbols` | JWT | Tous | — | `[SymbolGroup]` | Groupes de symboles tradeables |
| `PUT` | `/connectors/market-symbols` | JWT | SUPER_ADMIN, ADMIN | `{ symbols }` | `[SymbolGroup]` | Modifier l'univers des symboles |
| `GET` | `/connectors/ollama/models` | JWT | Tous | — | `[Model]` | Modèles LLM disponibles. Query : `provider` |
| `GET` | `/connectors/trading-config` | JWT | Tous | — | `TradingConfig` | Catalogue des paramètres trading. Query : `decision_mode`, `execution_mode` |
| `PUT` | `/connectors/trading-config` | JWT | SUPER_ADMIN, ADMIN | `{ config }` | `TradingConfig` | Sauvegarder la configuration trading par scope |
| `GET` | `/connectors/trading-config/versions` | JWT | Tous | — | `[ConfigVersion]` | Historique des versions de configuration |
| `POST` | `/connectors/trading-config/versions/{version_id}/restore` | JWT | SUPER_ADMIN, ADMIN | — | `TradingConfig` | Restaurer une version de configuration |
| `POST` | `/connectors/external-mcp/discover` | JWT | SUPER_ADMIN, ADMIN | `{ url }` | `[McpTool]` | Découvrir les outils d'un serveur MCP externe |
| `PUT` | `/connectors/external-mcp` | JWT | SUPER_ADMIN, ADMIN | `{ mcp_config }` | `McpConfig` | Sauvegarder la configuration MCP externe |
| `DELETE` | `/connectors/external-mcp/{mcp_id}` | JWT | SUPER_ADMIN, ADMIN | — | `{ success }` | Supprimer un connecteur MCP |
| `POST` | `/connectors/news/news-providers/{provider_name}/test` | JWT | SUPER_ADMIN, ADMIN | — | `{ success, message }` | Tester un fournisseur de news |

---

## 6. Prompts

> 3 endpoints — Gestion des templates de prompts pour les agents LLM.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/prompts` | JWT | Tous | — | `[PromptTemplate]` | Liste des templates de prompts. Query : `agent_name` |
| `POST` | `/prompts` | JWT | SUPER_ADMIN, ADMIN | `{ agent_name, template, ... }` | `PromptTemplate` | Créer une nouvelle version de prompt |
| `POST` | `/prompts/{prompt_id}/activate` | JWT | SUPER_ADMIN, ADMIN | — | `PromptTemplate` | Activer une version de prompt |

---

## 7. Backtests

> 3 endpoints — Exécution et consultation des backtests.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/backtests` | JWT | Tous | — | `[Backtest]` | Liste des backtests. Query : `limit` |
| `POST` | `/backtests` | JWT | Tous | `{ pair, timeframe, start_date, end_date, strategy, llm_enabled, agent_config }` | `Backtest` | Créer et exécuter un backtest. Query : `async_execution` |
| `GET` | `/backtests/{backtest_id}` | JWT | Tous | — | `Backtest` (avec trades) | Détail d'un backtest avec la liste des trades |

---

## 8. Analytics

> 3 endpoints — Tableaux de bord et métriques d'utilisation.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/analytics/llm-summary` | JWT | Tous | — | `LlmSummary` | Résumé de l'utilisation LLM. Query : `days` |
| `GET` | `/analytics/llm-models` | JWT | Tous | — | `[ModelUsage]` | Répartition de l'utilisation par modèle. Query : `days`, `limit` |
| `GET` | `/analytics/backtests-summary` | JWT | Tous | — | `BacktestsSummary` | Statistiques agrégées des backtests |

---

## 9. Portfolio

> 3 endpoints — Gestion du portefeuille, équité et stress tests.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/portfolio/state` | JWT | SUPER_ADMIN, ADMIN, VIEWER | — | `PortfolioState` | État du portefeuille avec limites de risque. Query : `account_ref` |
| `GET` | `/portfolio/history` | JWT | Tous | — | `[EquityPoint]` | Courbe d'équité. Query : `period` (valeurs : `24h`, `7d`, `30d`) |
| `GET` | `/portfolio/stress` | JWT | Tous | — | `StressResult` | Stress test sur les positions ouvertes. Query : `account_ref` |

---

## 10. Strategies

> 10 endpoints — Cycle de vie complet des stratégies de trading.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/strategies` | JWT | Tous | — | `[Strategy]` | Liste des stratégies. Query : `limit` |
| `GET` | `/strategies/{strategy_id}` | JWT | Tous | — | `Strategy` | Détail d'une stratégie |
| `DELETE` | `/strategies/{strategy_id}` | JWT | SUPER_ADMIN, ADMIN | — | `{ success }` | Supprimer une stratégie |
| `POST` | `/strategies/generate` | JWT | Tous | `{ prompt, pair, timeframe }` | `Strategy` | Générer une stratégie via LLM + backtest automatique |
| `POST` | `/strategies/{strategy_id}/validate` | JWT | Tous | — | `BacktestResult` | Lancer une validation par backtest |
| `POST` | `/strategies/{strategy_id}/promote` | JWT | SUPER_ADMIN, ADMIN | `{ target }` | `Strategy` | Promouvoir une stratégie (VALIDATED → PAPER → LIVE) |
| `POST` | `/strategies/{strategy_id}/edit` | JWT | Tous | `{ prompt }` | `Strategy` | Modifier les paramètres via conversation LLM |
| `GET` | `/strategies/{strategy_id}/indicators` | JWT | Tous | — | `[Indicator]` | Indicateurs overlays calculés depuis les bougies live |
| `POST` | `/strategies/{strategy_id}/start-monitoring` | JWT | SUPER_ADMIN, ADMIN, TRADER_OPERATOR | `{ mode, risk_percent }` | `{ status }` | Démarrer le monitoring d'une stratégie |
| `POST` | `/strategies/{strategy_id}/stop-monitoring` | JWT | SUPER_ADMIN, ADMIN, TRADER_OPERATOR | — | `{ status }` | Arrêter le monitoring d'une stratégie |

---

## 11. Governance

> 7 endpoints — Gouvernance des recommandations de trading.

| Méthode | Chemin | Auth | Rôles | Corps Requête | Réponse | Description |
|---------|--------|------|-------|---------------|---------|-------------|
| `GET` | `/governance/recommendations` | JWT | Tous | — | `[Recommendation]` | Liste des recommandations. Query : `limit`, `symbol`, `status`, `approval_status` |
| `GET` | `/governance/recommendations/{gov_run_id}` | JWT | Tous | — | `GovernanceRun` | Détail d'un run de gouvernance |
| `POST` | `/governance/{gov_run_id}/approve` | JWT | SUPER_ADMIN, ADMIN | — | `GovernanceRun` | Approuver une recommandation |
| `POST` | `/governance/{gov_run_id}/reject` | JWT | SUPER_ADMIN, ADMIN | — | `GovernanceRun` | Rejeter une recommandation |
| `POST` | `/governance/force` | JWT | SUPER_ADMIN, ADMIN | — | `GovernanceRun` | Forcer une évaluation de gouvernance |
| `GET` | `/governance/config` | JWT | SUPER_ADMIN, ADMIN | — | `GovernanceConfig` | Configuration de la gouvernance |
| `PUT` | `/governance/config` | JWT | SUPER_ADMIN, ADMIN | `{ auto_approve, ... }` | `GovernanceConfig` | Modifier la configuration de gouvernance (auto_approve, etc.) |

---

## 12. WebSocket

> 5 endpoints — Flux temps réel montés sur la racine (`/ws`), hors préfixe `/api/v1`.

| Protocole | Chemin | Auth | Query | Description |
|-----------|--------|------|-------|-------------|
| `WS` | `/ws/runs/{run_id}` | JWT | — | Progression d'un run en temps réel (poll DB toutes les 2 secondes) |
| `WS` | `/ws/trading/orders` | JWT | — | Flux des ordres d'exécution en live |
| `WS` | `/ws/market/prices` | JWT | `symbol` | Flux des prix marché en live (via Redis pub/sub) |
| `WS` | `/ws/portfolio` | JWT | — | État du portefeuille en live (équité, positions, risque) |
| `WS` | `/ws/governance` | JWT | — | Flux des recommandations de gouvernance en live |

---

## 13. Référentiel des rôles

| Rôle | Description | Niveau d'accès |
|------|-------------|----------------|
| `SUPER_ADMIN` | Super-administrateur | Accès complet à toutes les ressources et configurations |
| `ADMIN` | Administrateur | Accès complet à toutes les ressources et configurations |
| `TRADER_OPERATOR` | Opérateur de trading | Exécution des trades, gestion des stratégies et annulation de runs |
| `ANALYST` | Analyste | Lecture + création de runs et backtests |
| `VIEWER` | Observateur | Lecture seule sur les données du portefeuille et dashboards |

> **Note :** Lorsque la colonne « Rôles » indique « Tous », cela signifie que tout utilisateur authentifié (quel que soit son rôle) peut accéder à l'endpoint.
