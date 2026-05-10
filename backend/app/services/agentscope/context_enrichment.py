"""Context enrichment for agents — Multi-TF, run history, regime overlays.

Sprint 1 of the brainstorming improvements:
- R1: Multi-TF Light — inject higher/lower TF summary into agent context
- R2: Memoire Light — inject recent run history for the same pair
- I1: Regime overlay — dynamic briefing injected into agent prompts
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────
# R1: Multi-TF Light
# ────────────────────────────────────────────────────────

# Timeframe hierarchy for determining higher/lower TFs
_TF_HIERARCHY = ["M5", "M15", "H1", "H4", "D1"]

_TF_HIGHER: dict[str, str] = {
    "M5": "H1",
    "M15": "H1",
    "H1": "H4",
    "H4": "D1",
    "D1": "D1",  # D1 has no higher — use itself
}

_TF_LOWER: dict[str, str] = {
    "M5": "M5",   # M5 has no lower — use itself
    "M15": "M5",
    "H1": "M15",
    "H4": "H1",
    "D1": "H4",
}


def _compute_tf_summary(closes: list[float], highs: list[float], lows: list[float]) -> dict[str, Any]:
    """Compute a compact technical summary from OHLC arrays."""
    if not closes or len(closes) < 20:
        return {}

    try:
        import pandas as pd
        from ta.momentum import RSIIndicator
        from ta.trend import EMAIndicator

        close = pd.Series(closes)
        ema20 = EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]
        ema50 = EMAIndicator(close=close, window=50).ema_indicator().iloc[-1]
        rsi = RSIIndicator(close=close, window=14).rsi().iloc[-1]

        latest = float(close.iloc[-1])
        trend = "bullish" if ema20 > ema50 else "bearish"
        if abs(ema20 - ema50) < latest * 0.0003:
            trend = "neutral"

        # Trend slope: EMA20 direction over last 10 bars
        ema20_series = EMAIndicator(close=close, window=20).ema_indicator()
        if len(ema20_series.dropna()) >= 10:
            slope = (float(ema20_series.iloc[-1]) - float(ema20_series.iloc[-10])) / float(ema20_series.iloc[-10]) * 100
        else:
            slope = 0.0

        return {
            "trend": trend,
            "rsi": round(float(rsi), 1),
            "ema20_vs_ema50": trend,
            "trend_slope_pct": round(float(slope), 3),
            "last_price": round(latest, 6),
        }
    except Exception as exc:
        logger.warning("Multi-TF summary computation failed: %s", exc)
        return {}


async def fetch_multi_tf_context(
    pair: str,
    current_tf: str,
    account_id: str | None = None,
    region: str | None = None,
) -> dict[str, Any]:
    """Fetch higher and lower TF data and compute summaries.

    Returns dict with 'higher_tf' and 'lower_tf' keys, each containing
    a compact summary dict (trend, rsi, slope).
    """
    higher_tf = _TF_HIGHER.get(current_tf.upper(), current_tf.upper())
    lower_tf = _TF_LOWER.get(current_tf.upper(), current_tf.upper())

    result: dict[str, Any] = {
        "current_tf": current_tf.upper(),
        "higher_tf_name": higher_tf,
        "lower_tf_name": lower_tf,
        "higher_tf": {},
        "lower_tf": {},
    }

    # Skip if same as current (D1 higher or M5 lower)
    tfs_to_fetch: list[tuple[str, str]] = []
    if higher_tf != current_tf.upper():
        tfs_to_fetch.append((higher_tf, "higher_tf"))
    if lower_tf != current_tf.upper():
        tfs_to_fetch.append((lower_tf, "lower_tf"))

    if not tfs_to_fetch or not account_id:
        return result

    try:
        from app.services.trading.metaapi_client import MetaApiClient
        import asyncio

        metaapi = MetaApiClient()

        async def _fetch_one(tf: str) -> dict[str, Any]:
            try:
                candles_result = await metaapi.get_market_candles(
                    pair=pair, timeframe=tf, limit=100,
                    account_id=account_id, region=region or "new-york",
                )
                if isinstance(candles_result, dict) and not candles_result.get("degraded"):
                    candles = candles_result.get("candles", [])
                    if candles and len(candles) >= 20:
                        closes = [float(c.get("close", 0)) for c in candles[-100:]]
                        highs = [float(c.get("high", 0)) for c in candles[-100:]]
                        lows = [float(c.get("low", 0)) for c in candles[-100:]]
                        return _compute_tf_summary(closes, highs, lows)
            except Exception as exc:
                logger.warning("Multi-TF fetch failed for %s/%s: %s", pair, tf, exc)
            return {}

        tasks = [_fetch_one(tf) for tf, _ in tfs_to_fetch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, (tf, key) in enumerate(tfs_to_fetch):
            if isinstance(results[i], dict):
                result[key] = results[i]

    except Exception as exc:
        logger.warning("Multi-TF context fetch failed: %s", exc)

    return result


def format_multi_tf_block(mtf_context: dict[str, Any]) -> str:
    """Format multi-TF context into a compact text block for prompt injection."""
    if not mtf_context:
        return ""

    lines = ["Multi-timeframe context:"]

    higher = mtf_context.get("higher_tf", {})
    higher_name = mtf_context.get("higher_tf_name", "?")
    if higher:
        lines.append(
            f"- Higher TF ({higher_name}): trend={higher.get('trend', '?')}, "
            f"RSI={higher.get('rsi', '?')}, slope={higher.get('trend_slope_pct', '?')}%"
        )
    else:
        lines.append(f"- Higher TF ({higher_name}): not available")

    lower = mtf_context.get("lower_tf", {})
    lower_name = mtf_context.get("lower_tf_name", "?")
    if lower:
        lines.append(
            f"- Lower TF ({lower_name}): trend={lower.get('trend', '?')}, "
            f"RSI={lower.get('rsi', '?')}, slope={lower.get('trend_slope_pct', '?')}%"
        )
    else:
        lines.append(f"- Lower TF ({lower_name}): not available")

    # Alignment assessment
    current_tf = mtf_context.get("current_tf", "?")
    if higher and lower:
        trends = [higher.get("trend"), lower.get("trend")]
        if all(t == "bullish" for t in trends):
            lines.append(f"- TF Alignment: ALL BULLISH ({lower_name}+{current_tf}+{higher_name}) — strong directional confluence")
        elif all(t == "bearish" for t in trends):
            lines.append(f"- TF Alignment: ALL BEARISH ({lower_name}+{current_tf}+{higher_name}) — strong directional confluence")
        else:
            lines.append(f"- TF Alignment: MIXED — cross-timeframe divergence, reduce conviction")

    return "\n".join(lines)


# ────────────────────────────────────────────────────────
# R2: Memoire Light — Recent run history
# ────────────────────────────────────────────────────────

def fetch_recent_run_history(db, pair: str, limit: int = 7) -> list[dict[str, Any]]:
    """Query the N most recent completed runs for this pair from DB.

    Returns a list of compact dicts with decision, conviction, regime, result.
    """
    try:
        from app.db.models.run import AnalysisRun
        from app.db.models.agent_step import AgentStep

        runs = (
            db.query(AnalysisRun)
            .filter(
                AnalysisRun.pair == pair,
                AnalysisRun.status == "completed",
            )
            .order_by(AnalysisRun.created_at.desc())
            .limit(limit)
            .all()
        )

        if not runs:
            return []

        history: list[dict[str, Any]] = []
        for run in runs:
            decision_data = run.decision or {}
            if isinstance(decision_data, str):
                import json
                try:
                    decision_data = json.loads(decision_data)
                except (json.JSONDecodeError, ValueError):
                    decision_data = {}

            # Extract key fields from the decision JSON
            entry: dict[str, Any] = {
                "run_id": run.id,
                "timeframe": run.timeframe,
                "created_at": run.created_at.isoformat() if run.created_at else "?",
                "decision": decision_data.get("decision", "UNKNOWN"),
                "conviction": decision_data.get("conviction", 0),
            }

            # Try to extract regime from market-context-analyst step
            try:
                ctx_step = (
                    db.query(AgentStep)
                    .filter(
                        AgentStep.run_id == run.id,
                        AgentStep.agent_name == "market-context-analyst",
                    )
                    .first()
                )
                if ctx_step and ctx_step.output_payload:
                    meta = ctx_step.output_payload.get("metadata", {})
                    entry["regime"] = meta.get("regime", "unknown")
            except Exception:
                entry["regime"] = "unknown"

            history.append(entry)

        return history

    except Exception as exc:
        logger.warning("Failed to fetch run history for %s: %s", pair, exc)
        return []


def format_run_history_block(history: list[dict[str, Any]]) -> str:
    """Format run history into a compact text block for prompt injection."""
    if not history:
        return ""

    lines = [f"Recent analysis history ({len(history)} runs):"]

    for entry in history:
        decision = entry.get("decision", "?")
        conviction = entry.get("conviction", "?")
        regime = entry.get("regime", "?")
        tf = entry.get("timeframe", "?")
        created = entry.get("created_at", "?")
        # Shorten ISO timestamp to readable form
        if isinstance(created, str) and len(created) > 16:
            created = created[:16].replace("T", " ")

        lines.append(f"- [{created}] {tf}: {decision} (conviction={conviction}%, regime={regime})")

    # Trend summary
    decisions = [e.get("decision", "UNKNOWN") for e in history]
    buy_count = sum(1 for d in decisions if d == "BUY")
    sell_count = sum(1 for d in decisions if d == "SELL")
    hold_count = sum(1 for d in decisions if d == "HOLD")

    if buy_count > sell_count and buy_count > hold_count:
        lines.append(f"- Recent bias: BULLISH ({buy_count} BUY / {sell_count} SELL / {hold_count} HOLD)")
    elif sell_count > buy_count and sell_count > hold_count:
        lines.append(f"- Recent bias: BEARISH ({buy_count} BUY / {sell_count} SELL / {hold_count} HOLD)")
    else:
        lines.append(f"- Recent bias: NEUTRAL ({buy_count} BUY / {sell_count} SELL / {hold_count} HOLD)")

    # Conviction trend
    convictions = [e.get("conviction", 0) for e in history if isinstance(e.get("conviction"), (int, float))]
    if len(convictions) >= 3:
        recent_avg = sum(convictions[:3]) / 3
        older_avg = sum(convictions[3:]) / max(len(convictions[3:]), 1) if len(convictions) > 3 else recent_avg
        if recent_avg > older_avg + 5:
            lines.append("- Conviction trend: RISING")
        elif recent_avg < older_avg - 5:
            lines.append("- Conviction trend: FALLING")
        else:
            lines.append("- Conviction trend: STABLE")

    return "\n".join(lines)


# ────────────────────────────────────────────────────────
# I1: Regime Overlay — Dynamic prompt briefing
# ────────────────────────────────────────────────────────

REGIME_OVERLAYS: dict[str, dict[str, str]] = {
    "trending_up": {
        "technical-analyst": (
            "REGIME BRIEFING — TRENDING UP:\n"
            "- Bias: look for trend continuation setups (pullbacks to EMA, flag patterns)\n"
            "- Pullbacks to key moving averages are opportunities, not reversals\n"
            "- Weight structural trend indicators (EMA alignment, ADX) more heavily\n"
            "- Reduce weight of overbought RSI signals — trends can stay overbought\n"
        ),
        "trader-agent": (
            "REGIME BRIEFING — TRENDING UP:\n"
            "- Bias: favor BUY setups, require stronger evidence for SELL\n"
            "- Minimum conviction for BUY: 55% (favorable regime)\n"
            "- Minimum conviction for SELL: 75% (counter-trend requires high conviction)\n"
            "- Trailing stops preferred over fixed TP in strong trends\n"
        ),
        "news-analyst": (
            "REGIME BRIEFING — TRENDING UP:\n"
            "- Market is in an established uptrend — positive news confirms, negative news is counter-trend\n"
            "- Counter-trend news needs to be HIGH impact to override the technical trend\n"
            "- Look for catalysts that could accelerate or exhaust the current trend\n"
        ),
        "bullish-researcher": (
            "REGIME BRIEFING — TRENDING UP:\n"
            "- The trend is your primary evidence. Build on structural momentum.\n"
            "- Focus on continuation signals and trend acceleration catalysts.\n"
        ),
        "bearish-researcher": (
            "REGIME BRIEFING — TRENDING UP:\n"
            "- You are arguing counter-trend. Your bar is higher.\n"
            "- Focus on exhaustion signals: RSI divergence, volume decline, extended price from mean.\n"
            "- Counter-trend arguments need multiple confirming signals, not just one indicator.\n"
        ),
    },
    "trending_down": {
        "technical-analyst": (
            "REGIME BRIEFING — TRENDING DOWN:\n"
            "- Bias: look for trend continuation setups (rallies to resistance, bear flags)\n"
            "- Rallies to key moving averages are sell opportunities, not reversals\n"
            "- Weight structural trend indicators (EMA alignment, ADX) more heavily\n"
            "- Reduce weight of oversold RSI signals — trends can stay oversold\n"
        ),
        "trader-agent": (
            "REGIME BRIEFING — TRENDING DOWN:\n"
            "- Bias: favor SELL setups, require stronger evidence for BUY\n"
            "- Minimum conviction for SELL: 55% (favorable regime)\n"
            "- Minimum conviction for BUY: 75% (counter-trend requires high conviction)\n"
            "- Consider wider stops — downtrends have sharper retracements\n"
        ),
        "news-analyst": (
            "REGIME BRIEFING — TRENDING DOWN:\n"
            "- Market is in an established downtrend — negative news confirms, positive news is counter-trend\n"
            "- Counter-trend news needs to be HIGH impact to override the technical trend\n"
            "- Look for capitulation signals or major policy shifts that could reverse the trend\n"
        ),
        "bullish-researcher": (
            "REGIME BRIEFING — TRENDING DOWN:\n"
            "- You are arguing counter-trend. Your bar is higher.\n"
            "- Focus on capitulation signals: extreme oversold, volume climax, bullish divergence.\n"
            "- Counter-trend arguments need multiple confirming signals.\n"
        ),
        "bearish-researcher": (
            "REGIME BRIEFING — TRENDING DOWN:\n"
            "- The trend is your primary evidence. Build on structural weakness.\n"
            "- Focus on continuation signals and support breakdown catalysts.\n"
        ),
    },
    "ranging": {
        "technical-analyst": (
            "REGIME BRIEFING — RANGING:\n"
            "- Bias: focus on support/resistance boundaries and mean reversion\n"
            "- Trend-following signals are unreliable in ranges — reduce their weight\n"
            "- Key S/R levels with 3+ touches are the primary trading anchors\n"
            "- Watch for squeeze/compression setups that may precede breakout\n"
        ),
        "trader-agent": (
            "REGIME BRIEFING — RANGING:\n"
            "- Bias: prefer mean-reversion trades at range boundaries\n"
            "- BUY at support, SELL at resistance — avoid mid-range entries\n"
            "- Tighter SL/TP — ranges have defined boundaries\n"
            "- Minimum conviction: 60% (ranging is harder to trade)\n"
            "- HOLD is acceptable in mid-range — wait for boundaries\n"
        ),
        "news-analyst": (
            "REGIME BRIEFING — RANGING:\n"
            "- Market is range-bound — news catalysts could trigger a breakout\n"
            "- HIGH impact events near range boundaries are especially significant\n"
            "- Flag any catalyst that could break the current range structure\n"
        ),
        "bullish-researcher": (
            "REGIME BRIEFING — RANGING:\n"
            "- Focus on bounces from support. Breakout arguments need volume confirmation.\n"
            "- Range-bound context means your thesis has a natural target (resistance).\n"
        ),
        "bearish-researcher": (
            "REGIME BRIEFING — RANGING:\n"
            "- Focus on rejections from resistance. Breakdown arguments need volume confirmation.\n"
            "- Range-bound context means your thesis has a natural target (support).\n"
        ),
    },
    "volatile": {
        "technical-analyst": (
            "REGIME BRIEFING — VOLATILE:\n"
            "- Bias: expect wider price swings, reduce noise sensitivity\n"
            "- Use longer indicator periods to filter volatility noise\n"
            "- ATR-based levels are more reliable than fixed pip distances\n"
            "- Multiple conflicting signals are expected — focus on the strongest\n"
        ),
        "trader-agent": (
            "REGIME BRIEFING — VOLATILE:\n"
            "- Bias: widen SL to avoid noise stops, reduce position size\n"
            "- Minimum conviction: 70% (volatile regime requires higher bar)\n"
            "- HOLD is a valid and often smart decision in extreme volatility\n"
            "- If entering, use ATR-based SL (2x ATR minimum)\n"
        ),
        "news-analyst": (
            "REGIME BRIEFING — VOLATILE:\n"
            "- High volatility suggests active catalysts or uncertainty\n"
            "- Multiple news items may be competing — focus on the dominant driver\n"
            "- Event risk is amplified in volatile conditions\n"
        ),
        "bullish-researcher": (
            "REGIME BRIEFING — VOLATILE:\n"
            "- Volatile conditions mean rapid price moves. Your thesis must be conviction-based.\n"
            "- Timing is critical — identify specific triggers, not just direction.\n"
        ),
        "bearish-researcher": (
            "REGIME BRIEFING — VOLATILE:\n"
            "- Volatile conditions mean rapid price moves. Your thesis must be conviction-based.\n"
            "- Timing is critical — identify specific triggers, not just direction.\n"
        ),
    },
    "calm": {
        "technical-analyst": (
            "REGIME BRIEFING — CALM:\n"
            "- Bias: look for compression/squeeze setups that precede moves\n"
            "- Shorter indicator periods may catch subtle signals in low-vol\n"
            "- ATR is compressed — signals near support/resistance are more precise\n"
            "- Small moves can be significant relative to current volatility\n"
        ),
        "trader-agent": (
            "REGIME BRIEFING — CALM:\n"
            "- Bias: tighter SL/TP reflecting low volatility, normal position size\n"
            "- Minimum conviction: 55% (calm conditions offer cleaner setups)\n"
            "- Mean-reversion and breakout setups both work in calm conditions\n"
            "- Watch for volatility expansion signals (Bollinger squeeze, ATR expansion)\n"
        ),
        "news-analyst": (
            "REGIME BRIEFING — CALM:\n"
            "- Low volatility market — news catalysts can create outsized moves\n"
            "- Even MEDIUM impact events can break calm conditions\n"
            "- Upcoming events are especially important — they may trigger vol expansion\n"
        ),
        "bullish-researcher": (
            "REGIME BRIEFING — CALM:\n"
            "- Calm markets offer clean technical setups. Focus on precision entries.\n"
            "- Compression patterns (wedges, triangles) are your strongest evidence.\n"
        ),
        "bearish-researcher": (
            "REGIME BRIEFING — CALM:\n"
            "- Calm markets offer clean technical setups. Focus on precision entries.\n"
            "- Compression patterns (wedges, triangles) are your strongest evidence.\n"
        ),
    },
}

# Aliases for regime names
_REGIME_ALIASES: dict[str, str] = {
    "trending": "trending_up",
    "trend": "trending_up",
    "bullish": "trending_up",
    "bearish": "trending_down",
    "range": "ranging",
    "sideways": "ranging",
    "choppy": "ranging",
    "high_volatility": "volatile",
    "low_volatility": "calm",
    "quiet": "calm",
}


def get_regime_overlay(regime: str | None, agent_name: str) -> str:
    """Get the regime-specific prompt overlay for a given agent.

    Returns empty string if regime is unknown or no overlay defined.
    """
    if not regime:
        return ""

    normalized = regime.strip().lower()
    # Check direct match first, then aliases
    regime_key = normalized if normalized in REGIME_OVERLAYS else _REGIME_ALIASES.get(normalized, "")

    if not regime_key or regime_key not in REGIME_OVERLAYS:
        return ""

    overlay = REGIME_OVERLAYS[regime_key].get(agent_name, "")
    return overlay


def get_all_regime_overlays(regime: str | None) -> dict[str, str]:
    """Get regime overlays for all agents at once.

    Returns dict of agent_name → overlay_text.
    """
    if not regime:
        return {}

    normalized = regime.strip().lower()
    regime_key = normalized if normalized in REGIME_OVERLAYS else _REGIME_ALIASES.get(normalized, "")

    if not regime_key or regime_key not in REGIME_OVERLAYS:
        return {}

    return dict(REGIME_OVERLAYS[regime_key])
