from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from app.services.benchmark.constants import BenchmarkRunStatus
from app.services.llm.call_context import use_analysis_run_id


logger = logging.getLogger(__name__)


@dataclass
class ScenarioAttemptResult:
    agent_name: str
    attempt_number: int
    raw_output: dict[str, Any]
    analysis_run_id: int | None = None


@dataclass
class ScenarioExecutionResult:
    status: str
    attempts: list[ScenarioAttemptResult]


def _try_extract_json(text: str) -> dict[str, Any]:
    """Try to extract a JSON object from text content."""
    if not text:
        return {}
    clean = text.strip()
    # Direct parse
    try:
        parsed = json.loads(clean)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, ValueError):
        pass
    # Find JSON block in text
    start = clean.find("{")
    if start >= 0:
        end = clean.rfind("}")
        if end > start:
            try:
                parsed = json.loads(clean[start:end + 1])
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, ValueError):
                pass
    return {}


def _extract_all_text_from_msg(msg: Any) -> str:
    """Extract text from ALL content blocks (text + thinking).

    AgentScope's get_text_content() only returns TextBlock content.
    Models like DeepSeek use ThinkingBlocks which contain the actual
    structured output. This function captures everything.
    """
    content = getattr(msg, 'content', None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                # TextBlock: {'type': 'text', 'text': '...'}
                if block.get('type') == 'text' and block.get('text'):
                    parts.append(block['text'])
                # ThinkingBlock: {'type': 'thinking', 'thinking': '...'}
                elif block.get('type') == 'thinking' and block.get('thinking'):
                    parts.append(block['thinking'])
            elif hasattr(block, 'text'):
                parts.append(str(block.text))
            elif hasattr(block, 'thinking'):
                parts.append(str(block.thinking))
        return '\n'.join(parts)
    if content is not None:
        return str(content)
    return ''


def _extract_output_payload(
    msg: Any,
    *,
    run_id: int = 0,
    agent_name: str = 'unknown-agent',
    attempt_number: int = 0,
) -> dict[str, Any]:
    """Extract structured output from an AgentScope Msg.

    Mirrors the extraction logic used by the real pipeline (_msg_to_dict):
    1. Check msg.metadata (structured dict set by ReActAgent)
    2. If empty, parse JSON from text content
    3. Fallback to {'text': ...}
    """
    if msg is None:
        logger.warning(
            'benchmark run_id=%s extraction got empty msg agent_name=%s attempt_number=%s',
            run_id,
            agent_name,
            attempt_number,
        )
        return {}
    # 1. Check metadata (AgentScope agents put structured output here)
    metadata = getattr(msg, 'metadata', None)
    if isinstance(metadata, dict) and metadata:
        logger.debug(
            'benchmark run_id=%s extraction from metadata agent_name=%s attempt_number=%s metadata_keys=%s metadata_size=%s',
            run_id,
            agent_name,
            attempt_number,
            sorted(list(metadata.keys())),
            len(metadata),
        )
        return metadata
    if metadata is None or (isinstance(metadata, dict) and not metadata):
        logger.warning(
            'benchmark run_id=%s extraction metadata empty agent_name=%s attempt_number=%s',
            run_id,
            agent_name,
            attempt_number,
        )
    # 2. Try to get text content from ALL blocks (text + thinking)
    text = ''
    try:
        text = _extract_all_text_from_msg(msg)
    except Exception as exc:
        logger.warning(
            'benchmark run_id=%s extraction _extract_all_text failed agent_name=%s attempt_number=%s error=%s',
            run_id,
            agent_name,
            attempt_number,
            exc,
        )
        # Fallback to get_text_content
        try:
            text = msg.get_text_content() or ''
        except Exception:
            text = str(getattr(msg, 'content', ''))
    if text:
        try:
            parsed = _try_extract_json(text)
        except Exception:
            logger.error(
                'benchmark run_id=%s extraction json parsing failed agent_name=%s attempt_number=%s',
                run_id,
                agent_name,
                attempt_number,
                exc_info=True,
            )
            parsed = {}
        if parsed:
            logger.debug(
                'benchmark run_id=%s extraction from text json agent_name=%s attempt_number=%s payload_keys=%s payload_size=%s',
                run_id,
                agent_name,
                attempt_number,
                sorted(list(parsed.keys())),
                len(parsed),
            )
            return parsed
    # 3. Try content as dict directly
    content = getattr(msg, 'content', None)
    if isinstance(content, dict) and content:
        logger.warning(
            'benchmark run_id=%s extraction fallback content dict agent_name=%s attempt_number=%s payload_keys=%s payload_size=%s',
            run_id,
            agent_name,
            attempt_number,
            sorted(list(content.keys())),
            len(content),
        )
        return content
    payload = {'text': text}
    logger.warning(
        'benchmark run_id=%s extraction fallback text agent_name=%s attempt_number=%s payload_keys=%s payload_size=%s',
        run_id,
        agent_name,
        attempt_number,
        sorted(list(payload.keys())),
        len(payload),
    )
    return payload


async def run_single_agent_scenario(
    *,
    run_id: int,
    analysis_run_id: int | None,
    agent_name: str,
    agent,
    context_msg,
    repetitions: int,
) -> ScenarioExecutionResult:
    attempts: list[ScenarioAttemptResult] = []
    for attempt_number in range(1, repetitions + 1):
        logger.info(
            'benchmark run_id=%s before agent call scenario=single-agent agent_name=%s attempt_number=%s',
            run_id,
            agent_name,
            attempt_number,
        )
        with use_analysis_run_id(analysis_run_id):
            result_msg = await agent(context_msg)
        content_value = getattr(result_msg, 'content', '')
        content_length = len(content_value) if isinstance(content_value, str) else len(str(content_value))
        metadata = getattr(result_msg, 'metadata', None)
        has_metadata = isinstance(metadata, dict) and bool(metadata)
        # Diagnostic: dump Msg structure to understand extraction failures
        text_content = ''
        try:
            text_content = result_msg.get_text_content() or ''
        except Exception:
            pass
        content_type = type(content_value).__name__
        content_preview = ''
        if isinstance(content_value, list):
            block_types = [type(b).__name__ if not isinstance(b, dict) else b.get('type', '?') for b in content_value[:5]]
            content_preview = f'blocks={block_types}'
        elif isinstance(content_value, str):
            content_preview = content_value[:200]
        logger.info(
            'benchmark run_id=%s after agent call scenario=single-agent agent_name=%s attempt_number=%s '
            'msg_type=%s has_metadata=%s content_type=%s content_length=%s text_content_length=%s content_preview=%s',
            run_id,
            agent_name,
            attempt_number,
            type(result_msg).__name__,
            has_metadata,
            content_type,
            content_length,
            len(text_content),
            content_preview,
        )

        payload = _extract_output_payload(result_msg, run_id=run_id, agent_name=agent_name, attempt_number=attempt_number)
        logger.debug(
            'benchmark run_id=%s extracted payload scenario=single-agent agent_name=%s attempt_number=%s payload_keys=%s payload_size=%s',
            run_id,
            agent_name,
            attempt_number,
            sorted(list(payload.keys())),
            len(payload),
        )
        attempts.append(
            ScenarioAttemptResult(
                agent_name=agent_name,
                attempt_number=attempt_number,
                raw_output=payload,
                analysis_run_id=analysis_run_id,
            )
        )
    return ScenarioExecutionResult(status=BenchmarkRunStatus.COMPLETED, attempts=attempts)


async def run_debate_bundle_scenario(
    *,
    run_id: int,
    analysis_run_id: int | None,
    llm_enabled_flags: dict[str, bool],
    bullish_agent,
    bearish_agent,
    trader_agent,
    context_msg,
    repetitions: int,
) -> ScenarioExecutionResult:
    if not all(llm_enabled_flags.get(agent_name, True) for agent_name in ('bullish-researcher', 'bearish-researcher', 'trader-agent')):
        logger.warning(
            'benchmark run_id=%s debate skipped due to llm_enabled flags=%s',
            run_id,
            llm_enabled_flags,
        )
        return ScenarioExecutionResult(status=BenchmarkRunStatus.SKIPPED_DEBATE, attempts=[])

    attempts: list[ScenarioAttemptResult] = []
    for attempt_number in range(1, repetitions + 1):
        logger.info(
            'benchmark run_id=%s before agent call scenario=debate-bundle agent_name=%s attempt_number=%s',
            run_id,
            'bullish-researcher',
            attempt_number,
        )
        with use_analysis_run_id(analysis_run_id):
            bullish_msg = await bullish_agent(context_msg)
            bullish_content = getattr(bullish_msg, 'content', '')
            bullish_metadata = getattr(bullish_msg, 'metadata', None)
            logger.info(
                'benchmark run_id=%s after agent call scenario=debate-bundle agent_name=%s attempt_number=%s msg_type=%s has_metadata=%s content_length=%s',
                run_id,
                'bullish-researcher',
                attempt_number,
                type(bullish_msg).__name__,
                isinstance(bullish_metadata, dict) and bool(bullish_metadata),
                len(bullish_content) if isinstance(bullish_content, str) else len(str(bullish_content)),
            )

            logger.info(
                'benchmark run_id=%s before agent call scenario=debate-bundle agent_name=%s attempt_number=%s',
                run_id,
                'bearish-researcher',
                attempt_number,
            )
            bearish_msg = await bearish_agent(bullish_msg)
            bearish_content = getattr(bearish_msg, 'content', '')
            bearish_metadata = getattr(bearish_msg, 'metadata', None)
            logger.info(
                'benchmark run_id=%s after agent call scenario=debate-bundle agent_name=%s attempt_number=%s msg_type=%s has_metadata=%s content_length=%s',
                run_id,
                'bearish-researcher',
                attempt_number,
                type(bearish_msg).__name__,
                isinstance(bearish_metadata, dict) and bool(bearish_metadata),
                len(bearish_content) if isinstance(bearish_content, str) else len(str(bearish_content)),
            )

            logger.info(
                'benchmark run_id=%s before agent call scenario=debate-bundle agent_name=%s attempt_number=%s',
                run_id,
                'trader-agent',
                attempt_number,
            )
            trader_msg = await trader_agent(bearish_msg)
            trader_content = getattr(trader_msg, 'content', '')
            trader_metadata = getattr(trader_msg, 'metadata', None)
            logger.info(
                'benchmark run_id=%s after agent call scenario=debate-bundle agent_name=%s attempt_number=%s msg_type=%s has_metadata=%s content_length=%s',
                run_id,
                'trader-agent',
                attempt_number,
                type(trader_msg).__name__,
                isinstance(trader_metadata, dict) and bool(trader_metadata),
                len(trader_content) if isinstance(trader_content, str) else len(str(trader_content)),
            )

        bullish_payload = _extract_output_payload(bullish_msg, run_id=run_id, agent_name='bullish-researcher', attempt_number=attempt_number)
        bearish_payload = _extract_output_payload(bearish_msg, run_id=run_id, agent_name='bearish-researcher', attempt_number=attempt_number)
        trader_payload = _extract_output_payload(trader_msg, run_id=run_id, agent_name='trader-agent', attempt_number=attempt_number)
        logger.debug(
            'benchmark run_id=%s extracted payload scenario=debate-bundle attempt_number=%s bullish_keys=%s bearish_keys=%s trader_keys=%s',
            run_id,
            attempt_number,
            sorted(list(bullish_payload.keys())),
            sorted(list(bearish_payload.keys())),
            sorted(list(trader_payload.keys())),
        )

        attempts.append(
            ScenarioAttemptResult(
                agent_name='bullish-researcher',
                attempt_number=attempt_number,
                raw_output=bullish_payload,
                analysis_run_id=analysis_run_id,
            )
        )
        attempts.append(
            ScenarioAttemptResult(
                agent_name='bearish-researcher',
                attempt_number=attempt_number,
                raw_output=bearish_payload,
                analysis_run_id=analysis_run_id,
            )
        )
        attempts.append(
            ScenarioAttemptResult(
                agent_name='trader-agent',
                attempt_number=attempt_number,
                raw_output=trader_payload,
                analysis_run_id=analysis_run_id,
            )
        )

    return ScenarioExecutionResult(status=BenchmarkRunStatus.COMPLETED, attempts=attempts)


async def run_full_pipeline_scenario(
    *,
    run_id: int,
    analysis_run_id: int | None,
    ordered_agents: list[tuple[str, Any]],
    context_msg,
    repetitions: int,
) -> ScenarioExecutionResult:
    attempts: list[ScenarioAttemptResult] = []
    for attempt_number in range(1, repetitions + 1):
        current_context = context_msg
        for agent_name, agent in ordered_agents:
            logger.info(
                'benchmark run_id=%s before agent call scenario=full-pipeline agent_name=%s attempt_number=%s',
                run_id,
                agent_name,
                attempt_number,
            )
            with use_analysis_run_id(analysis_run_id):
                result_msg = await agent(current_context)
            content_value = getattr(result_msg, 'content', '')
            metadata = getattr(result_msg, 'metadata', None)
            logger.info(
                'benchmark run_id=%s after agent call scenario=full-pipeline agent_name=%s attempt_number=%s msg_type=%s has_metadata=%s content_length=%s',
                run_id,
                agent_name,
                attempt_number,
                type(result_msg).__name__,
                isinstance(metadata, dict) and bool(metadata),
                len(content_value) if isinstance(content_value, str) else len(str(content_value)),
            )
            payload = _extract_output_payload(result_msg, run_id=run_id, agent_name=agent_name, attempt_number=attempt_number)
            logger.debug(
                'benchmark run_id=%s extracted payload scenario=full-pipeline agent_name=%s attempt_number=%s payload_keys=%s payload_size=%s',
                run_id,
                agent_name,
                attempt_number,
                sorted(list(payload.keys())),
                len(payload),
            )
            attempts.append(
                ScenarioAttemptResult(
                    agent_name=agent_name,
                    attempt_number=attempt_number,
                    raw_output=payload,
                    analysis_run_id=analysis_run_id,
                )
            )
            current_context = result_msg
    return ScenarioExecutionResult(status=BenchmarkRunStatus.COMPLETED, attempts=attempts)
