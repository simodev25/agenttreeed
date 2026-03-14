# Données Forex et news

## Source marché/news

- Provider: `backend/app/services/market/yfinance_provider.py`
- Source: Yahoo Finance via `yfinance`
- Mapping symbole:
  - entrée plateforme `EURUSD`
  - symbole Yahoo `EURUSD=X`

## Timeframes et fenêtre de récupération

- `M5`: interval `5m`, période `7d`
- `M15`: interval `15m`, période `30d`
- `H1`: interval `60m`, période `90d`
- `H4`: base `60m` puis resampling `4h`
- `D1`: interval `1d`, période `365d`

## Snapshot marché normalisé

`get_market_snapshot(pair, timeframe)` retourne:

- `last_price`
- `change_pct`
- `rsi`
- `ema_fast` / `ema_slow`
- `macd_diff`
- `atr`
- `trend` (`bullish` / `bearish` / `neutral`)
- `degraded`

## News normalisées

`get_news_context(pair)` retourne une liste `news`:

- `title`
- `publisher`
- `link`
- `published`

## Historique pour backtest

`get_historical_candles(pair, timeframe, start_date, end_date)` alimente:

- stratégie `ema_rsi`
- stratégie `agents_v1`

## Intégration mémoire

- Après run complété: résumé stocké dans `memory_entries`.
- Recherche mémoire:
  - Qdrant prioritaire (collection configurable), avec filtre strict `pair` + `timeframe`,
  - repli SQL cosine si Qdrant indisponible.

## Mode dégradé

- Si Yahoo Finance indisponible:
  - payload `degraded=true`,
  - orchestration continue avec signaux partiels,
  - run reste traçable.
