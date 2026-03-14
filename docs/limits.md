# Limites connues (V1)

## Sécurité / exploitation

- Le compte seed local (`admin@local.dev` / `admin1234`) est prévu pour dev/test uniquement.
- L'endpoint `POST /api/v1/auth/bootstrap-admin` doit rester limité aux environnements internes.
- Le mode `live` est désactivé par défaut (`ALLOW_LIVE_TRADING=false`).

## Données marché et broker

- `yfinance` et `MetaApi` peuvent être indisponibles de façon intermittente.
- En mode `paper`, un repli en simulation est possible si MetaApi rejette/ne confirme pas un ordre.
- Les données de deals/history MetaApi dépendent de la synchronisation du compte (`Sync in progress`).

## Mémoire long-terme

- Qdrant est prioritaire; repli SQL cosine activé si Qdrant indisponible.
- Le filtrage mémoire est borné au couple `pair` + `timeframe`.
- Les embeddings V1 sont déterministes (hash), pas des embeddings sémantiques LLM.

## Performance

- Le backtest `agents_v1` est plus coûteux que `ema_rsi` (pipeline multi-agent).
- Le composant de graphiques trades réels est chargé à la demande (lazy) pour réduire le bundle initial.
