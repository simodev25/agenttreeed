# Limites connues V1

- Connecteur MetaApi dépend du broker/compte MetaTrader (symboles actifs, sessions, permissions).
- `risk-manager` et `execution-manager` sont déterministes (pas de raisonnement LLM).
- Analyse macro/sentiment encore proxy (heuristiques simples).
- Mémoire vectorielle basée sur embedding déterministe local (pas d'embedder sémantique externe en V1).
- Coût LLM estimé (pas une facturation contractuelle).
- Keycloak non branché (JWT local).
- Qdrant: attention à l'écart de versions client/serveur (warning de compatibilité possible).
- Backtest `agents_v1` utilise des snapshots simplifiés; ce n'est pas un replay broker tick-accurate.

