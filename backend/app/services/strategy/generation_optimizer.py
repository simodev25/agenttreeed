from __future__ import annotations

from typing import Any

from app.services.strategy.validation_scoring import compute_validation_score


def _metric(metrics: dict[str, Any], *keys: str) -> float:
    for key in keys:
        value = metrics.get(key)
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return 0.0


def _trades(metrics: dict[str, Any]) -> int:
    for key in ('total_trades', 'trades'):
        value = metrics.get(key)
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            continue
    return 0


def compute_generation_candidate_score(metrics: dict[str, Any]) -> float:
    score, _, _ = compute_validation_score(
        win_rate=_metric(metrics, 'win_rate_pct', 'win_rate'),
        profit_factor=_metric(metrics, 'profit_factor'),
        max_dd=abs(_metric(metrics, 'max_drawdown_pct', 'max_drawdown')),
        total_return=_metric(metrics, 'total_return_pct', 'total_return'),
        trades=_trades(metrics),
    )
    return float(score)


def should_optimize_generation(metrics: dict[str, Any]) -> bool:
    trades = _trades(metrics)
    score = compute_generation_candidate_score(metrics)
    total_return = _metric(metrics, 'total_return_pct', 'total_return')
    if trades <= 0:
        return True
    if trades < 10:
        return True
    if total_return <= 0:
        return True
    return score < 35.0


def choose_best_generation_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    if not candidates:
        raise ValueError('No generation candidates provided')

    def _sort_key(candidate: dict[str, Any]) -> tuple[float, int, float]:
        metrics = candidate.get('metrics', {}) if isinstance(candidate.get('metrics', {}), dict) else {}
        return (
            compute_generation_candidate_score(metrics),
            _trades(metrics),
            _metric(metrics, 'total_return_pct', 'total_return'),
        )

    return max(candidates, key=_sort_key)


def _is_crypto_symbol(symbol: str) -> bool:
    normalized = str(symbol or '').upper()
    return '.PRO' not in normalized and normalized.endswith('USD')


# ── Regime-adaptive preset banks per template ──
# Each entry: (params_dict, reason_str)
# Presets are ordered: default first, then regime-specific variants.

_REGIME_TRENDING = {'trending', 'trending_up', 'trending_down', 'trend'}
_REGIME_RANGING = {'ranging', 'range', 'sideways', 'choppy'}
_REGIME_VOLATILE = {'volatile', 'high_volatility'}
_REGIME_CALM = {'calm', 'low_volatility', 'quiet'}

_TEMPLATE_PRESETS: dict[str, list[tuple[dict[str, Any], str, set[str] | None]]] = {
    # ── Trend Following ──
    'ema_crossover': [
        ({'ema_fast': 9, 'ema_slow': 21, 'rsi_filter': 30}, 'standard trend preset — higher participation', None),
        ({'ema_fast': 12, 'ema_slow': 36, 'rsi_filter': 35}, 'wider spread — fewer whipsaws in trends', _REGIME_TRENDING),
        ({'ema_fast': 7, 'ema_slow': 18, 'rsi_filter': 25}, 'tight preset — catches early moves in calm markets', _REGIME_CALM | _REGIME_RANGING),
        ({'ema_fast': 8, 'ema_slow': 34, 'rsi_filter': 25}, 'asymmetric preset — low-volatility breakouts', _REGIME_CALM),
    ],
    'supertrend': [
        ({'atr_period': 10, 'atr_multiplier': 3.0}, 'standard supertrend', None),
        ({'atr_period': 14, 'atr_multiplier': 2.0}, 'tighter trail — trending markets', _REGIME_TRENDING),
        ({'atr_period': 7, 'atr_multiplier': 4.0}, 'wider trail — volatile whipsaw protection', _REGIME_VOLATILE),
        ({'atr_period': 10, 'atr_multiplier': 1.5}, 'tight trail — calm markets catch small moves', _REGIME_CALM),
    ],
    'adx_trend': [
        ({'adx_period': 14, 'adx_threshold': 25, 'di_period': 14}, 'standard ADX filter', None),
        ({'adx_period': 10, 'adx_threshold': 20, 'di_period': 10}, 'lower threshold — more signals in weak trends', _REGIME_CALM | _REGIME_RANGING),
        ({'adx_period': 14, 'adx_threshold': 30, 'di_period': 14}, 'strict filter — only strong trends', _REGIME_TRENDING),
        ({'adx_period': 20, 'adx_threshold': 25, 'di_period': 20}, 'slower ADX — reduces noise in volatile markets', _REGIME_VOLATILE),
    ],
    'ichimoku': [
        ({'tenkan': 9, 'kijun': 26, 'senkou_b': 52}, 'standard Ichimoku', None),
        ({'tenkan': 7, 'kijun': 22, 'senkou_b': 44}, 'faster Ichimoku — shorter trends', _REGIME_CALM),
        ({'tenkan': 12, 'kijun': 30, 'senkou_b': 60}, 'slower Ichimoku — strong trends only', _REGIME_TRENDING),
    ],
    'parabolic_sar': [
        ({'af_start': 0.02, 'af_step': 0.02, 'af_max': 0.2}, 'standard SAR', None),
        ({'af_start': 0.01, 'af_step': 0.01, 'af_max': 0.15}, 'slow SAR — fewer reversals in trends', _REGIME_TRENDING),
        ({'af_start': 0.03, 'af_step': 0.03, 'af_max': 0.3}, 'fast SAR — quick exits in volatile markets', _REGIME_VOLATILE),
    ],
    'donchian_breakout': [
        ({'entry_period': 20, 'exit_period': 10}, 'standard turtle breakout', None),
        ({'entry_period': 55, 'exit_period': 20}, 'wide channel — major breakouts only', _REGIME_RANGING),
        ({'entry_period': 10, 'exit_period': 5}, 'tight channel — catch early breakouts', _REGIME_CALM),
    ],
    # ── Mean Reversion ──
    'rsi_mean_reversion': [
        ({'rsi_period': 14, 'oversold': 30, 'overbought': 70}, 'standard RSI reversion', None),
        ({'rsi_period': 7, 'oversold': 20, 'overbought': 80}, 'fast RSI — extreme levels only', _REGIME_VOLATILE),
        ({'rsi_period': 14, 'oversold': 35, 'overbought': 65}, 'relaxed thresholds — more signals in ranges', _REGIME_RANGING),
        ({'rsi_period': 21, 'oversold': 25, 'overbought': 75}, 'slow RSI — smoother signals', _REGIME_CALM),
    ],
    'stochastic_reversal': [
        ({'k_period': 14, 'd_period': 3, 'oversold': 20, 'overbought': 80}, 'standard stochastic', None),
        ({'k_period': 9, 'd_period': 3, 'oversold': 15, 'overbought': 85}, 'fast stochastic — volatile markets', _REGIME_VOLATILE),
        ({'k_period': 14, 'd_period': 5, 'oversold': 25, 'overbought': 75}, 'smoothed — ranging markets', _REGIME_RANGING),
    ],
    'williams_r': [
        ({'period': 14, 'oversold': -80, 'overbought': -20}, 'standard Williams %R', None),
        ({'period': 7, 'oversold': -85, 'overbought': -15}, 'fast — extreme levels in volatile', _REGIME_VOLATILE),
        ({'period': 21, 'oversold': -75, 'overbought': -25}, 'slow — wider bands for ranging', _REGIME_RANGING),
    ],
    'cci_reversal': [
        ({'cci_period': 20, 'oversold': -100, 'overbought': 100}, 'standard CCI', None),
        ({'cci_period': 14, 'oversold': -150, 'overbought': 150}, 'wide CCI — extreme only in volatile', _REGIME_VOLATILE),
        ({'cci_period': 20, 'oversold': -80, 'overbought': 80}, 'relaxed CCI — more signals in ranges', _REGIME_RANGING),
    ],
    'keltner_reversion': [
        ({'ema_period': 20, 'atr_period': 10, 'atr_multiplier': 1.5}, 'standard Keltner reversion', None),
        ({'ema_period': 20, 'atr_period': 14, 'atr_multiplier': 2.0}, 'wider channel — volatile markets', _REGIME_VOLATILE),
        ({'ema_period': 15, 'atr_period': 10, 'atr_multiplier': 1.0}, 'tight channel — calm ranging', _REGIME_CALM | _REGIME_RANGING),
    ],
    # ── Breakout / Volatility ──
    'bollinger_breakout': [
        ({'bb_period': 20, 'bb_std': 2.0}, 'standard Bollinger breakout', None),
        ({'bb_period': 20, 'bb_std': 1.5}, 'tighter bands — more signals', _REGIME_CALM),
        ({'bb_period': 20, 'bb_std': 2.5}, 'wider bands — extreme breakouts only', _REGIME_VOLATILE),
        ({'bb_period': 30, 'bb_std': 2.0}, 'slower period — trend-strength breakouts', _REGIME_TRENDING),
    ],
    'squeeze_momentum': [
        ({'bb_period': 20, 'bb_std': 2.0, 'kc_period': 20, 'kc_multiplier': 1.5}, 'standard squeeze', None),
        ({'bb_period': 15, 'bb_std': 1.5, 'kc_period': 15, 'kc_multiplier': 1.0}, 'tight squeeze — calm markets', _REGIME_CALM),
        ({'bb_period': 25, 'bb_std': 2.5, 'kc_period': 25, 'kc_multiplier': 2.0}, 'wide squeeze — volatile compression', _REGIME_VOLATILE),
    ],
    'atr_trailing_stop': [
        ({'atr_period': 14, 'atr_multiplier': 2.5, 'trend_ema': 30}, 'standard ATR trail', None),
        ({'atr_period': 14, 'atr_multiplier': 1.5, 'trend_ema': 20}, 'tight trail — trending markets', _REGIME_TRENDING),
        ({'atr_period': 21, 'atr_multiplier': 3.5, 'trend_ema': 50}, 'wide trail — volatile markets', _REGIME_VOLATILE),
    ],
    # ── Momentum ──
    'macd_divergence': [
        ({'fast': 12, 'slow': 26, 'signal': 9}, 'standard MACD', None),
        ({'fast': 8, 'slow': 21, 'signal': 5}, 'fast MACD — early momentum shifts', _REGIME_TRENDING),
        ({'fast': 16, 'slow': 36, 'signal': 12}, 'slow MACD — noise reduction in ranges', _REGIME_RANGING),
    ],
    'roc_momentum': [
        ({'roc_period': 12, 'signal_period': 9, 'threshold': 1.0}, 'standard ROC', None),
        ({'roc_period': 9, 'signal_period': 5, 'threshold': 0.5}, 'fast ROC — catch early momentum', _REGIME_CALM),
        ({'roc_period': 21, 'signal_period': 12, 'threshold': 2.0}, 'slow ROC — strong momentum only', _REGIME_VOLATILE),
    ],
    'vwap_strategy': [
        ({'trend_ema': 30, 'deviation_pct': 0.3}, 'standard VWAP deviation', None),
        ({'trend_ema': 20, 'deviation_pct': 0.2}, 'tight VWAP — calm intraday', _REGIME_CALM),
        ({'trend_ema': 50, 'deviation_pct': 0.5}, 'wide VWAP — volatile intraday', _REGIME_VOLATILE),
    ],
    # ── Hybrid ──
    'triple_ema': [
        ({'ema_1': 5, 'ema_2': 13, 'ema_3': 34}, 'standard triple EMA', None),
        ({'ema_1': 3, 'ema_2': 8, 'ema_3': 21}, 'fast triple EMA — early alignment', _REGIME_TRENDING),
        ({'ema_1': 8, 'ema_2': 18, 'ema_3': 55}, 'slow triple EMA — noise filter', _REGIME_RANGING | _REGIME_VOLATILE),
    ],
    'macd_rsi_combo': [
        ({'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9, 'rsi_period': 14, 'rsi_oversold': 30, 'rsi_overbought': 70}, 'standard MACD+RSI', None),
        ({'macd_fast': 8, 'macd_slow': 21, 'macd_signal': 7, 'rsi_period': 10, 'rsi_oversold': 35, 'rsi_overbought': 65}, 'fast MACD+RSI — trending', _REGIME_TRENDING),
        ({'macd_fast': 14, 'macd_slow': 30, 'macd_signal': 12, 'rsi_period': 18, 'rsi_oversold': 25, 'rsi_overbought': 75}, 'slow MACD+RSI — ranging filter', _REGIME_RANGING),
    ],
    'pivot_points': [
        ({'lookback': 1}, 'daily pivots', None),
        ({'lookback': 3}, 'multi-day pivots — wider S/R', _REGIME_RANGING),
        ({'lookback': 5}, 'weekly pivots — strong S/R levels', _REGIME_TRENDING),
    ],
}

# Timeframe-specific adjustments: for shorter TFs, prefer faster presets
_SHORT_TIMEFRAMES = {'M5', 'M15'}
_LONG_TIMEFRAMES = {'D1', 'H4'}


def build_market_adaptive_param_candidates(
    *,
    template: str,
    symbol: str,
    timeframe: str,
    market_regime: str | None,
    current_params: dict[str, Any],
) -> list[dict[str, Any]]:
    regime = str(market_regime or '').lower()
    normalized_timeframe = str(timeframe or '').upper()
    candidates: list[dict[str, Any]] = []

    presets = _TEMPLATE_PRESETS.get(template)
    if not presets:
        return []

    # Filter presets: include universal (regime_set=None) + matching regime
    filtered: list[tuple[dict[str, Any], str]] = []
    for params, reason, regime_set in presets:
        if regime_set is None:
            # Universal preset — always include
            filtered.append((params, reason))
        elif regime and regime in regime_set:
            # Regime-specific match — prioritize by inserting at front
            filtered.insert(0, (params, f'{reason} [regime={regime}]'))

    # For short timeframes, also include calm/ranging presets if no regime match
    if not regime and normalized_timeframe in _SHORT_TIMEFRAMES:
        for params, reason, regime_set in presets:
            if regime_set and regime_set & (_REGIME_CALM | _REGIME_RANGING):
                filtered.append((params, f'{reason} [short-tf fallback]'))

    # Deduplicate against current params
    seen = {tuple(sorted((current_params or {}).items()))}
    for params, reason in filtered:
        key = tuple(sorted(params.items()))
        if key in seen:
            continue
        seen.add(key)
        candidates.append({
            'params': params,
            'reason': reason,
            'warnings': ['heuristic_adaptation'],
        })

    return candidates
