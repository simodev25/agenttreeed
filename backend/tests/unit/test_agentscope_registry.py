import asyncio

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from agentscope.message import Msg

from app.services.agentscope.registry import AgentScopeRegistry
from app.services.agentscope.schemas import DebateResult


def _make_msg(name="agent", text="result"):
    msg = MagicMock(spec=Msg)
    msg.name = name
    msg.get_text_content.return_value = text
    msg.metadata = {"signal": "neutral"}
    msg.content = text
    return msg


@pytest.mark.asyncio
@patch("app.services.agentscope.registry.build_toolkit", new_callable=AsyncMock)
@patch("app.services.agentscope.registry.build_model")
@patch("app.services.agentscope.registry.build_formatter")
@patch("app.services.agentscope.registry.run_debate", new_callable=AsyncMock)
async def test_execute_runs_all_phases(mock_debate, mock_formatter, mock_model, mock_toolkit):
    mock_toolkit.return_value = MagicMock()
    mock_model.return_value = MagicMock()
    mock_formatter.return_value = MagicMock()

    analyst_msg = _make_msg("technical-analyst", "Bearish trend detected")

    mock_debate.return_value = (
        _make_msg("bullish-researcher", "Bull thesis"),
        _make_msg("bearish-researcher", "Bear thesis"),
        DebateResult(winner="bearish", conviction="strong", key_argument="Momentum confirmed", weakness="News neutral"),
    )

    phase4_msg = _make_msg("trader-agent", "SELL decision")
    phase4_msg.metadata = {"decision": "HOLD", "conviction": 0.3, "reasoning": "No clear edge"}

    def _make_mock_agent(**kwargs):
        agent = AsyncMock(return_value=phase4_msg)
        agent.memory = None
        return agent

    mock_agent = _make_mock_agent()

    db = MagicMock()
    run = MagicMock()
    run.id = 1
    run.pair = "EURUSD"
    run.timeframe = "H1"

    prompt_service = MagicMock()
    prompt_service.render.return_value = {
        "prompt_id": 1, "version": 1,
        "system_prompt": "You are a trading agent.",
        "user_prompt": "", "skills": ["skill1"], "missing_variables": [],
    }

    registry = AgentScopeRegistry(
        prompt_service=prompt_service,
        market_provider=MagicMock(),
        execution_service=MagicMock(),
    )

    with patch.object(registry, "_resolve_market_data", new_callable=AsyncMock) as mock_market:
        mock_market.return_value = {"snapshot": {"last_price": 1.1}, "news": {}, "ohlc": {}}
        with patch.object(registry, "_resolve_provider_config") as mock_config:
            mock_config.return_value = ("ollama", "deepseek-v3.2", "http://localhost:11434", "")
            # Mock AgentModelSelector to enable LLM for all agents
            with patch("app.services.llm.model_selector.AgentModelSelector") as mock_selector_cls:
                mock_selector = MagicMock()
                mock_selector.is_enabled.return_value = True
                mock_selector_cls.return_value = mock_selector
                # Patch ALL_AGENT_FACTORIES
                with patch("app.services.agentscope.registry.ALL_AGENT_FACTORIES") as mock_factories:
                    # Factory must return a fresh AsyncMock each time (rebuild after Phase 1)
                    mock_factory_fn = MagicMock(side_effect=lambda **kw: _make_mock_agent(**kw))
                    mock_factories.items.return_value = [
                        (n, mock_factory_fn) for n in [
                            "technical-analyst", "news-analyst", "market-context-analyst",
                            "bullish-researcher", "bearish-researcher",
                            "trader-agent", "risk-manager", "execution-manager",
                        ]
                    ]
                    mock_factories.__iter__ = lambda self: iter([
                        "technical-analyst", "news-analyst", "market-context-analyst",
                        "bullish-researcher", "bearish-researcher",
                        "trader-agent", "risk-manager", "execution-manager",
                    ])
                    mock_factories.get = lambda name, default=None: mock_factory_fn
                    mock_factories.__getitem__ = lambda self, name: mock_factory_fn
                    result = await registry.execute(
                        db=db, run=run, pair="EURUSD", timeframe="H1", risk_percent=1.0,
                    )

    assert mock_debate.call_count == 1
    assert run.status == "completed"
    assert isinstance(run.decision, dict)
    assert run.decision.get("debate", {}).get("winner") == "bearish"
    assert db.add.call_count >= 8


@pytest.mark.asyncio
@patch("app.services.agentscope.registry.build_toolkit", new_callable=AsyncMock)
@patch("app.services.agentscope.registry.build_model")
@patch("app.services.agentscope.registry.build_formatter")
async def test_execute_marks_failed_on_error(mock_formatter, mock_model, mock_toolkit):
    mock_toolkit.return_value = MagicMock()
    mock_model.side_effect = ValueError("Bad provider")
    mock_formatter.return_value = MagicMock()

    db = MagicMock()
    run = MagicMock()
    run.id = 1

    registry = AgentScopeRegistry()
    with patch.object(registry, "_resolve_provider_config") as mock_config:
        mock_config.return_value = ("bad", "x", "http://x", "")
        with pytest.raises(ValueError):
            await registry.execute(db=db, run=run, pair="EURUSD", timeframe="H1", risk_percent=1.0)

    assert run.status == "failed"


@pytest.mark.asyncio
@patch("app.services.agentscope.registry.build_toolkit", new_callable=AsyncMock)
@patch("app.services.agentscope.registry.build_model")
@patch("app.services.agentscope.registry.build_formatter")
@patch("app.services.agentscope.registry.run_debate", new_callable=AsyncMock)
async def test_execute_phase1_timeout_degrades_and_continues(
    mock_debate,
    mock_formatter,
    mock_model,
    mock_toolkit,
):
    mock_toolkit.return_value = MagicMock()
    mock_model.return_value = MagicMock()
    mock_formatter.return_value = MagicMock()

    mock_debate.return_value = (
        _make_msg("bullish-researcher", "Bull thesis"),
        _make_msg("bearish-researcher", "Bear thesis"),
        DebateResult(winner="no_edge", conviction="weak", key_argument="Fallback", weakness=""),
    )

    trader_msg = _make_msg("trader-agent", "HOLD decision")
    trader_msg.metadata = {"decision": "HOLD", "conviction": 0.2, "reasoning": "Degraded phase 1"}

    def _mk_agent_for(name: str):
        if name == "news-analyst":
            agent = AsyncMock(side_effect=asyncio.TimeoutError("simulated timeout"))
        elif name == "trader-agent":
            agent = AsyncMock(return_value=trader_msg)
        else:
            agent = AsyncMock(return_value=_make_msg(name, f"{name} ok"))
        agent.memory = None
        return agent

    db = MagicMock()
    run = MagicMock()
    run.id = 2
    run.pair = "EURUSD"
    run.timeframe = "H1"

    prompt_service = MagicMock()
    prompt_service.render.return_value = {
        "prompt_id": 1,
        "version": 1,
        "system_prompt": "You are a trading agent.",
        "user_prompt": "",
        "skills": [],
        "missing_variables": [],
    }
    registry = AgentScopeRegistry(
        prompt_service=prompt_service,
        market_provider=MagicMock(),
        execution_service=MagicMock(),
    )

    with patch.object(registry, "_resolve_market_data", new_callable=AsyncMock) as mock_market:
        mock_market.return_value = {"snapshot": {"last_price": 1.1}, "news": {}, "ohlc": {}}
        with patch.object(registry, "_resolve_provider_config") as mock_config:
            mock_config.return_value = ("ollama", "deepseek-v3.2", "http://localhost:11434", "")
            with patch("app.services.llm.model_selector.AgentModelSelector") as mock_selector_cls:
                mock_selector = MagicMock()
                mock_selector.is_enabled.return_value = True
                mock_selector_cls.return_value = mock_selector

                with patch("app.services.agentscope.registry.ALL_AGENT_FACTORIES") as mock_factories:
                    names = [
                        "technical-analyst", "news-analyst", "market-context-analyst",
                        "bullish-researcher", "bearish-researcher",
                        "trader-agent", "risk-manager", "execution-manager",
                    ]
                    items = []
                    for name in names:
                        items.append((name, MagicMock(side_effect=lambda _n=name, **kw: _mk_agent_for(_n))))

                    mock_factories.items.return_value = items
                    mock_factories.__iter__ = lambda self: iter(names)
                    mock_factories.get = lambda name, default=None: dict(items).get(name, default)
                    mock_factories.__getitem__ = lambda self, name: dict(items)[name]

                    result = await registry.execute(
                        db=db,
                        run=run,
                        pair="EURUSD",
                        timeframe="H1",
                        risk_percent=1.0,
                    )

    assert result is run
    assert run.status == "completed"

    # Verify degraded fallback persisted for the failing Phase 1 agent.
    news_step = None
    for call in db.add.call_args_list:
        step = call.args[0]
        if getattr(step, "agent_name", "") == "news-analyst":
            news_step = step
            break

    assert news_step is not None
    assert news_step.output_payload.get("metadata", {}).get("degraded") is True
