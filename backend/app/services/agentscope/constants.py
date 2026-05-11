"""Extracted thresholds, policies, timeframes, and asset constants."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DecisionGatingPolicy:
    min_combined_score: float
    min_confidence: float
    min_aligned_sources: int
    allow_technical_single_source_override: bool
    block_major_contradiction: bool
    contradiction_penalty_weak: float
    contradiction_penalty_moderate: float
    contradiction_penalty_major: float
    confidence_multiplier_moderate: float
    confidence_multiplier_major: float

CONSERVATIVE = DecisionGatingPolicy(
    min_combined_score=0.32, min_confidence=0.38, min_aligned_sources=2,
    allow_technical_single_source_override=False, block_major_contradiction=True,
    contradiction_penalty_weak=0.0, contradiction_penalty_moderate=0.08,
    contradiction_penalty_major=0.14, confidence_multiplier_moderate=0.80,
    confidence_multiplier_major=0.60,
)
BALANCED = DecisionGatingPolicy(
    min_combined_score=0.22, min_confidence=0.28, min_aligned_sources=1,
    allow_technical_single_source_override=True, block_major_contradiction=True,
    contradiction_penalty_weak=0.0, contradiction_penalty_moderate=0.06,
    contradiction_penalty_major=0.11, confidence_multiplier_moderate=0.85,
    confidence_multiplier_major=0.70,
)
PERMISSIVE = DecisionGatingPolicy(
    min_combined_score=0.13, min_confidence=0.25, min_aligned_sources=1,
    allow_technical_single_source_override=True, block_major_contradiction=True,
    contradiction_penalty_weak=0.01, contradiction_penalty_moderate=0.04,
    contradiction_penalty_major=0.08, confidence_multiplier_moderate=0.90,
    confidence_multiplier_major=0.75,
)
DECISION_MODES: dict[str, DecisionGatingPolicy] = {
    "conservative": CONSERVATIVE, "balanced": BALANCED, "permissive": PERMISSIVE,
}

TIMEFRAME_ORDER = ("M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN")
MAX_USEFUL_TF = "D1"

def higher_timeframes(current_tf: str, max_count: int = 2) -> list[str]:
    try:
        idx = TIMEFRAME_ORDER.index(current_tf)
    except ValueError:
        return []
    cap = TIMEFRAME_ORDER.index(MAX_USEFUL_TF)
    return list(TIMEFRAME_ORDER[idx + 1 : min(idx + 1 + max_count, cap + 1)])

# Technical scoring weights (MUST sum to 1.0)
# Rationale for calibration:
# - TREND + EMA = structural bias (0.30 combined) — most persistent signal
# - MACD + RSI = momentum confirmation (0.26 combined) — active directional pressure
# - MULTI_TF = cross-timeframe alignment (0.14) — high-conviction filter
# - LEVEL = S/R proximity (0.12) — key for entry precision and invalidation
# - DIVERGENCE = early reversal signal (0.08) — valuable but requires confirmation
# - PATTERN = candlestick formations (0.06) — timing signal, weak alone
# - CHANGE = recent price change (0.04) — noise on short TFs, minor weight
TREND_WEIGHT = 0.20
EMA_WEIGHT = 0.10
RSI_WEIGHT = 0.12
MACD_WEIGHT = 0.14
CHANGE_WEIGHT = 0.04
PATTERN_WEIGHT = 0.06
DIVERGENCE_WEIGHT = 0.08
MULTI_TF_WEIGHT = 0.14
LEVEL_WEIGHT = 0.12

_WEIGHT_SUM = TREND_WEIGHT + EMA_WEIGHT + RSI_WEIGHT + MACD_WEIGHT + CHANGE_WEIGHT + PATTERN_WEIGHT + DIVERGENCE_WEIGHT + MULTI_TF_WEIGHT + LEVEL_WEIGHT
assert abs(_WEIGHT_SUM - 1.0) < 1e-6, f"Scoring weights must sum to 1.0, got {_WEIGHT_SUM}"

# Risk sizing — default multipliers (used when regime is unknown)
SL_ATR_MULTIPLIER = 1.5
TP_ATR_MULTIPLIER = 2.5
SL_PERCENT_FALLBACK = 0.003
TP_PERCENT_FALLBACK = 0.006

# Regime-adaptive SL/TP multipliers
# Rationale:
# - Trending: wider TP to capture trend continuation, standard SL
# - Ranging: tighter SL/TP for mean-reversion at extremes
# - Volatile: wider SL to avoid noise stops, wider TP for expanded moves
# - Calm: tighter everything, price moves are smaller
REGIME_SL_TP_MULTIPLIERS: dict[str, tuple[float, float]] = {
    "trending_up":   (1.5, 3.0),   # R:R = 2.0 — let winners run
    "trending_down": (1.5, 3.0),   # R:R = 2.0 — let winners run
    "ranging":       (1.2, 1.8),   # R:R = 1.5 — tighter targets at S/R
    "volatile":      (2.0, 3.5),   # R:R = 1.75 — wider stops for noise
    "calm":          (1.0, 2.0),   # R:R = 2.0 — tight stops, moves are small
}

def get_sl_tp_multipliers(regime: str | None) -> tuple[float, float]:
    """Return (SL_multiplier, TP_multiplier) adapted to market regime."""
    if regime and regime.lower() in REGIME_SL_TP_MULTIPLIERS:
        return REGIME_SL_TP_MULTIPLIERS[regime.lower()]
    return (SL_ATR_MULTIPLIER, TP_ATR_MULTIPLIER)

# Signal thresholds
SIGNAL_THRESHOLD = 0.05
TECHNICAL_SIGNAL_THRESHOLD = 0.15
NEWS_SIGNAL_THRESHOLD = 0.10
CONTEXT_SIGNAL_THRESHOLD = 0.12

# Asset classes
FIAT_ASSETS = ("USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD")
CRYPTO_ASSETS = ("ADA", "AVAX", "BCH", "BNB", "BTC", "DOGE", "DOT", "ETH", "LINK", "LTC", "MATIC", "SOL", "UNI", "XRP")
COMMODITY_ASSETS = ("XAU", "XAG")
