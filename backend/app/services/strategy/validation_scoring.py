from __future__ import annotations

MIN_VALIDATION_SCORE = 40.0
MIN_VALIDATION_PROFIT_FACTOR = 1.1
MAX_VALIDATION_DRAWDOWN_PCT = 35.0


def sample_size_factor(total_trades: int) -> float:
    """Scale score by sample size — stricter for small samples.

    Curve: 0 trades → 0.0, 10 trades → 0.35, 20 → 0.65, 30+ → 1.0.
    Previous version was too lenient (10 trades = 0.5).
    """
    if total_trades <= 0:
        return 0.0
    if total_trades < 10:
        # 1 trade = 0.035, 5 = 0.175, 9 = 0.315
        return total_trades / 28.5
    if total_trades < 30:
        # 10 = 0.35, 20 = 0.65, 29 ≈ 0.98
        return 0.35 + ((total_trades - 10) * (0.65 / 20.0))
    return 1.0


def return_penalty_factor(total_return_pct: float) -> float:
    """Gradual penalty for negative/low returns instead of binary 0.7.

    - return <= -10%: 0.3 (heavy penalty)
    - return = -5%: 0.5
    - return = 0%: 0.7
    - return = 5%: 0.9
    - return >= 10%: 1.0
    """
    if total_return_pct <= -10.0:
        return 0.3
    if total_return_pct <= 0.0:
        # Linear from 0.3 at -10% to 0.7 at 0%
        return 0.7 + (total_return_pct * 0.04)  # 0.04 per pct: -10→0.3, -5→0.5, 0→0.7
    if total_return_pct < 10.0:
        # Linear from 0.7 at 0% to 1.0 at 10%
        return 0.7 + (total_return_pct * 0.03)  # 0.03 per pct: 0→0.7, 5→0.85, 10→1.0
    return 1.0


def compute_validation_score(
    *,
    win_rate: float,
    profit_factor: float,
    max_dd: float,
    total_return: float,
    trades: int,
) -> tuple[float, float, float]:
    raw_score = min(
        100.0,
        max(
            0.0,
            win_rate * 0.3
            + min(profit_factor * 20.0, 40.0)
            + max(0.0, 30.0 - max_dd * 3.0),
        ),
    )
    sample_factor = sample_size_factor(trades)
    return_penalty = return_penalty_factor(total_return)
    score = raw_score * sample_factor * return_penalty
    return score, raw_score, sample_factor


def should_validate_strategy(
    *,
    score: float,
    total_return: float,
    profit_factor: float,
    max_dd: float,
) -> bool:
    return (
        float(score) >= MIN_VALIDATION_SCORE
        and float(total_return) > 0.0
        and float(profit_factor) >= MIN_VALIDATION_PROFIT_FACTOR
        and float(max_dd) <= MAX_VALIDATION_DRAWDOWN_PCT
    )
