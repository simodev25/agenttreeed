# Modeles de Donnees Backend

> **18 tables** | **12 migrations** | SQLAlchemy 2.0 + Alembic + PostgreSQL 16

---

## Diagramme de Relations Entite

```
users ─────────┬──< strategies
               ├──< analysis_runs ──┬──< agent_steps
               │                    ├──< execution_orders
               │                    ├──< agent_runtime_sessions
               │                    ├──< agent_runtime_messages
               │                    ├──< agent_runtime_events
               │                    └──< governance_runs (via origin_run_id)
               ├──< backtest_runs ──< backtest_trades
               └──< prompt_templates

connector_configs        (autonome)
metaapi_accounts         (autonome)
audit_logs               (autonome)
llm_call_logs            (autonome)
portfolio_snapshots      (autonome)
trading_config_versions  (autonome)
```

---

## Schema par Table

### 1. `users`

Comptes utilisateurs de la plateforme.

| Colonne           | Type         | Contraintes                  |
| ----------------- | ------------ | ---------------------------- |
| `id`              | Integer      | PK, auto-increment          |
| `email`           | String       | UNIQUE, NOT NULL             |
| `hashed_password` | String       | NOT NULL                     |
| `role`            | String       | DEFAULT `'viewer'`           |
| `is_active`       | Boolean      | NOT NULL                     |
| `created_at`      | DateTime     | NOT NULL                     |

---

### 2. `strategies`

Strategies de trading gerees par le systeme.

| Colonne                  | Type         | Contraintes                              |
| ------------------------ | ------------ | ---------------------------------------- |
| `id`                     | Integer      | PK, auto-increment                       |
| `strategy_id`            | String       | UNIQUE, NOT NULL (ex. `STRAT-001`)       |
| `name`                   | String       | NOT NULL                                 |
| `description`            | Text         |                                          |
| `status`                 | String       | DRAFT\|BACKTESTING\|VALIDATED\|PAPER\|LIVE\|REJECTED |
| `score`                  | Float        |                                          |
| `template`               | String       |                                          |
| `symbol`                 | String       |                                          |
| `timeframe`              | String       |                                          |
| `params`                 | JSON         |                                          |
| `metrics`                | JSON         |                                          |
| `prompt_history`         | JSON         |                                          |
| `is_monitoring`          | Boolean      |                                          |
| `monitoring_mode`        | String       |                                          |
| `monitoring_risk_percent`| Float        |                                          |
| `last_signal_key`        | String       |                                          |
| `last_backtest_id`       | Integer      |                                          |
| `created_by_id`          | Integer      | FK -> `users.id`                         |
| `created_at`             | DateTime     | NOT NULL                                 |
| `updated_at`             | DateTime     |                                          |

---

### 3. `analysis_runs`

Executions d'analyse multi-agents.

| Colonne         | Type         | Contraintes                        |
| --------------- | ------------ | ---------------------------------- |
| `id`            | Integer      | PK, auto-increment                 |
| `pair`          | String       | NOT NULL, INDEX                    |
| `timeframe`     | String       | NOT NULL                           |
| `mode`          | String       | DEFAULT `'simulation'`             |
| `status`        | String       | DEFAULT `'pending'`                |
| `progress`      | Float        |                                    |
| `decision`      | JSON         |                                    |
| `trace`         | JSON         |                                    |
| `error`         | Text         |                                    |
| `created_by_id` | Integer      | FK -> `users.id`                   |
| `created_at`    | DateTime     | NOT NULL                           |
| `started_at`    | DateTime     |                                    |
| `updated_at`    | DateTime     |                                    |

**Relations** : `steps`, `orders`, `runtime_events`, `runtime_sessions`, `runtime_messages` (cascade `delete-orphan`).

---

### 4. `agent_steps`

Etapes individuelles executees par chaque agent au sein d'un run.

| Colonne          | Type         | Contraintes                    |
| ---------------- | ------------ | ------------------------------ |
| `id`             | Integer      | PK, auto-increment             |
| `run_id`         | Integer      | FK -> `analysis_runs.id`       |
| `agent_name`     | String       | NOT NULL                       |
| `status`         | String       |                                |
| `input_payload`  | JSON         |                                |
| `output_payload` | JSON         |                                |
| `error`          | Text         |                                |
| `created_at`     | DateTime     | NOT NULL                       |

---

### 5. `execution_orders`

Ordres de trading emis par le systeme.

| Colonne               | Type         | Contraintes                    |
| --------------------- | ------------ | ------------------------------ |
| `id`                  | Integer      | PK, auto-increment             |
| `run_id`              | Integer      | FK -> `analysis_runs.id`       |
| `mode`                | String       |                                |
| `side`                | String       |                                |
| `symbol`              | String       |                                |
| `volume`              | Float        | DEFAULT `0.01`                 |
| `status`              | String       | DEFAULT `'created'`            |
| `request_payload`     | JSON         |                                |
| `response_payload`    | JSON         |                                |
| `error`               | Text         |                                |
| `created_at`          | DateTime     | NOT NULL                       |
| `metaapi_position_id` | String       | INDEX                          |

---

### 6. `backtest_runs`

Executions de backtesting.

| Colonne             | Type         | Contraintes                    |
| ------------------- | ------------ | ------------------------------ |
| `id`                | Integer      | PK, auto-increment             |
| `pair`              | String       | NOT NULL                       |
| `timeframe`         | String       | NOT NULL                       |
| `start_date`        | DateTime     |                                |
| `end_date`          | DateTime     |                                |
| `strategy`          | String       |                                |
| `llm_enabled`       | Boolean      |                                |
| `progress`          | Float        |                                |
| `status`            | String       |                                |
| `metrics`           | JSON         |                                |
| `equity_curve`      | JSON         |                                |
| `agent_validations` | JSON         |                                |
| `error`             | Text         |                                |
| `created_by_id`     | Integer      | FK -> `users.id`               |
| `created_at`        | DateTime     | NOT NULL                       |
| `started_at`        | DateTime     |                                |
| `updated_at`        | DateTime     |                                |

---

### 7. `backtest_trades`

Transactions individuelles generees lors d'un backtest.

| Colonne       | Type         | Contraintes                    |
| ------------- | ------------ | ------------------------------ |
| `id`          | Integer      | PK, auto-increment             |
| `run_id`      | Integer      | FK -> `backtest_runs.id`       |
| `side`        | String       |                                |
| `entry_time`  | DateTime     |                                |
| `exit_time`   | DateTime     |                                |
| `entry_price` | Float        |                                |
| `exit_price`  | Float        |                                |
| `pnl_pct`     | Float        |                                |
| `outcome`     | String       |                                |

---

### 8. `agent_runtime_sessions`

Sessions du runtime agentique. Chaque session represente un contexte d'execution d'agent.

| Colonne              | Type         | Contraintes                              |
| -------------------- | ------------ | ---------------------------------------- |
| `id`                 | Integer      | PK, auto-increment                       |
| `run_id`             | Integer      | FK -> `analysis_runs.id`                 |
| `session_key`        | String       | UNIQUE avec `run_id`                     |
| `parent_session_key` | String       |                                          |
| `label`              | String       |                                          |
| `name`               | String       |                                          |
| `status`             | String       |                                          |
| `mode`               | String       |                                          |
| `depth`              | Integer      |                                          |
| `role`               | String       |                                          |
| `can_spawn`          | Boolean      |                                          |
| `control_scope`      | String       |                                          |
| `turn`               | Integer      |                                          |
| `current_phase`      | String       |                                          |
| `resume_count`       | Integer      |                                          |
| `source_tool`        | String       |                                          |
| `objective`          | JSON         |                                          |
| `summary`            | JSON         |                                          |
| `metadata`           | JSON         |                                          |
| `completed_tools`    | JSON         |                                          |
| `state_snapshot`     | JSON         |                                          |
| `error`              | Text         |                                          |
| `started_at`         | DateTime     |                                          |
| `ended_at`           | DateTime     |                                          |
| `last_resumed_at`    | DateTime     |                                          |
| `created_at`         | DateTime     | NOT NULL                                 |
| `updated_at`         | DateTime     |                                          |

---

### 9. `agent_runtime_messages`

Messages echanges entre agents durant le runtime.

| Colonne             | Type         | Contraintes                    |
| ------------------- | ------------ | ------------------------------ |
| `id`                | Integer      | PK, auto-increment             |
| `run_id`            | Integer      | FK -> `analysis_runs.id`       |
| `session_key`       | String       |                                |
| `role`              | String       |                                |
| `content`           | Text         |                                |
| `sender_session_key`| String       |                                |
| `metadata`          | JSON         |                                |
| `created_at`        | DateTime     | NOT NULL                       |

---

### 10. `agent_runtime_events`

Evenements emis par le runtime agentique (bus evenementiel).

| Colonne          | Type         | Contraintes                        |
| ---------------- | ------------ | ---------------------------------- |
| `id`             | Integer      | PK, auto-increment                 |
| `run_id`         | Integer      | FK -> `analysis_runs.id`           |
| `session_key`    | String       |                                    |
| `seq`            | Integer      | UNIQUE avec `run_id`               |
| `stream`         | String       |                                    |
| `event_type`     | String       |                                    |
| `actor`          | String       |                                    |
| `turn`           | Integer      |                                    |
| `correlation_id` | String       |                                    |
| `causation_id`   | String       |                                    |
| `payload`        | JSON         |                                    |
| `ts`             | BigInteger   |                                    |
| `created_at`     | DateTime     | NOT NULL                           |

---

### 11. `governance_runs`

Executions du systeme de gouvernance pour la gestion des positions ouvertes.

| Colonne            | Type         | Contraintes                        |
| ------------------ | ------------ | ---------------------------------- |
| `id`               | Integer      | PK, auto-increment                 |
| `position_ticket`  | String       |                                    |
| `symbol`           | String       |                                    |
| `side`             | String       |                                    |
| `origin_run_id`    | Integer      | FK -> `analysis_runs.id`, NULLABLE |
| `status`           | String       |                                    |
| `action`           | String       | HOLD\|ADJUST_SL\|ADJUST_TP\|ADJUST_SL_TP\|CLOSE |
| `new_sl`           | Float        |                                    |
| `new_tp`           | Float        |                                    |
| `conviction`       | Float        |                                    |
| `urgency`          | String       | low\|medium\|high\|critical        |
| `reasoning`        | Text         |                                    |
| `trace`            | JSON         |                                    |
| `requires_approval`| Boolean      |                                    |
| `approval_status`  | String       |                                    |
| `approved_by`      | String       |                                    |
| `approved_at`      | DateTime     |                                    |
| `executed`         | Boolean      |                                    |
| `executed_at`      | DateTime     |                                    |
| `execution_error`  | Text         |                                    |
| `error`            | Text         |                                    |
| `created_at`       | DateTime     | NOT NULL                           |
| `updated_at`       | DateTime     |                                    |

---

### 12. `connector_configs`

Configuration des connecteurs externes (brokers, APIs).

| Colonne          | Type         | Contraintes                    |
| ---------------- | ------------ | ------------------------------ |
| `id`             | Integer      | PK, auto-increment             |
| `connector_name` | String       | UNIQUE, NOT NULL               |
| `enabled`        | Boolean      |                                |
| `settings`       | JSON         |                                |
| `updated_at`     | DateTime     |                                |

---

### 13. `metaapi_accounts`

Comptes MetaAPI rattaches a la plateforme.

| Colonne      | Type         | Contraintes                    |
| ------------ | ------------ | ------------------------------ |
| `id`         | Integer      | PK, auto-increment             |
| `label`      | String       |                                |
| `account_id` | String       | UNIQUE, NOT NULL               |
| `region`     | String       |                                |
| `enabled`    | Boolean      |                                |
| `is_default` | Boolean      |                                |
| `created_at` | DateTime     | NOT NULL                       |
| `updated_at` | DateTime     |                                |

---

### 14. `audit_logs`

Journal d'audit des actions utilisateurs.

| Colonne        | Type         | Contraintes                    |
| -------------- | ------------ | ------------------------------ |
| `id`           | Integer      | PK, auto-increment             |
| `actor_email`  | String       |                                |
| `action`       | String       |                                |
| `target_type`  | String       |                                |
| `target_id`    | String       |                                |
| `details`      | JSON         |                                |
| `created_at`   | DateTime     | NOT NULL                       |

---

### 15. `llm_call_logs`

Journalisation des appels aux modeles de langage (LLM).

| Colonne             | Type         | Contraintes                    |
| ------------------- | ------------ | ------------------------------ |
| `id`                | Integer      | PK, auto-increment             |
| `provider`          | String       | INDEX                          |
| `model`             | String       |                                |
| `status`            | String       |                                |
| `prompt_tokens`     | Integer      |                                |
| `completion_tokens` | Integer      |                                |
| `total_tokens`      | Integer      |                                |
| `cost_usd`          | Float        |                                |
| `latency_ms`        | Integer      |                                |
| `error`             | Text         |                                |
| `created_at`        | DateTime     | NOT NULL                       |

---

### 16. `prompt_templates`

Modeles de prompts versionnes par agent.

| Colonne               | Type         | Contraintes                        |
| --------------------- | ------------ | ---------------------------------- |
| `id`                  | Integer      | PK, auto-increment                 |
| `agent_name`          | String       | NOT NULL                           |
| `version`             | Integer      | UNIQUE avec `agent_name`           |
| `is_active`           | Boolean      |                                    |
| `system_prompt`       | Text         |                                    |
| `user_prompt_template`| Text         |                                    |
| `notes`               | Text         |                                    |
| `created_by_id`       | Integer      | FK -> `users.id`                   |
| `created_at`          | DateTime     | NOT NULL                           |
| `updated_at`          | DateTime     |                                    |

---

### 17. `portfolio_snapshots`

Instantanes periodiques de l'etat du portefeuille.

| Colonne               | Type         | Contraintes                    |
| --------------------- | ------------ | ------------------------------ |
| `id`                  | Integer      | PK, auto-increment             |
| `account_id`          | String       | INDEX                          |
| `timestamp`           | DateTime     | INDEX                          |
| `balance`             | Float        |                                |
| `equity`              | Float        |                                |
| `free_margin`         | Float        |                                |
| `used_margin`         | Float        |                                |
| `open_position_count` | Integer      |                                |
| `open_risk_total_pct` | Float        |                                |
| `daily_realized_pnl`  | Float        |                                |
| `daily_high_equity`   | Float        |                                |
| `snapshot_type`       | String       |                                |

---

### 18. `trading_config_versions`

Historique des versions de la configuration de trading.

| Colonne             | Type         | Contraintes                    |
| ------------------- | ------------ | ------------------------------ |
| `id`                | Integer      | PK, auto-increment             |
| `version`           | Integer      | INDEX                          |
| `changed_by`        | String       |                                |
| `changed_at`        | DateTime     | INDEX                          |
| `decision_mode`     | String       |                                |
| `settings_snapshot` | JSON         |                                |
| `changes_summary`   | Text         |                                |

---

## Carte des Cles Etrangeres

| Table enfant               | Colonne FK         | Table parent      |
| -------------------------- | ------------------ | ----------------- |
| `strategies`               | `created_by_id`    | `users`           |
| `analysis_runs`            | `created_by_id`    | `users`           |
| `agent_steps`              | `run_id`           | `analysis_runs`   |
| `execution_orders`         | `run_id`           | `analysis_runs`   |
| `agent_runtime_sessions`   | `run_id`           | `analysis_runs`   |
| `agent_runtime_messages`   | `run_id`           | `analysis_runs`   |
| `agent_runtime_events`     | `run_id`           | `analysis_runs`   |
| `backtest_runs`            | `created_by_id`    | `users`           |
| `backtest_trades`          | `run_id`           | `backtest_runs`   |
| `prompt_templates`         | `created_by_id`    | `users`           |
| `governance_runs`          | `origin_run_id`    | `analysis_runs`   |

---

## Historique des Migrations

| #    | Identifiant                        | Description                                                  |
| ---- | ---------------------------------- | ------------------------------------------------------------ |
| 1    | `0001_initial`                     | Schema initial                                               |
| 2    | `0002_v11_extensions`              | Prompts, memoire, backtests, comptes MetaAPI, logs LLM       |
| 3    | `0003_scheduled_runs`              | Runs planifies                                               |
| 4    | `0004_perf_indexes`                | Index de performance                                         |
| 5    | `0005_agentic_runtime_storage`     | Stockage runtime agents (sessions + messages)                |
| 6    | `0006_agentic_runtime_events`      | Table evenements runtime agents                              |
| 7    | `0007_strategy_symbol_timeframe`   | Ajout symbol/timeframe aux strategies                        |
| 8    | `0008_strategy_monitoring`         | Colonnes monitoring strategies                               |
| 9    | `0009_portfolio_snapshots`         | Table snapshots portefeuille                                 |
| 10   | `0010_trading_config_versions`     | Versions config trading                                      |
| 11   | `0011_governance_position_link`    | Ajout `metaapi_position_id` aux ordres                       |
| 12   | `0012_governance_runs`             | Table runs gouvernance                                       |
