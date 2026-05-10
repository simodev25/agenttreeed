# Condition-Based Waiting

Reliable patterns for asynchronous conditions without brittle sleeps.

## Polling vs Event-Driven

### Polling
Use when no event source exists.
- Check a condition on a fixed or adaptive interval
- Keep checks cheap and side-effect free
- Cap total wait time with timeout

### Event-Driven
Use when signals are available (webhooks, callbacks, queue messages).
- Subscribe once and react to state changes
- Prefer correlation IDs to match events to requests
- Add fallback polling for missed events in critical paths

## Timeout Strategies

Always define time boundaries:
- **Per-attempt timeout:** max duration for a single operation
- **Overall timeout:** hard cap for full workflow
- **Grace timeout:** short buffer before cleanup/cancel

Timeout values should reflect real latency budgets, not guesses.

## Retry with Backoff

For transient failures:
- Retry only idempotent operations (or protect with idempotency keys)
- Use exponential backoff with jitter
- Stop retrying on known permanent errors

Example schedule: 200ms, 400ms, 800ms, 1600ms (+ jitter).

## Circuit Breaker Pattern

Protect downstream services from overload:
- **Closed:** requests pass normally
- **Open:** failures exceed threshold, fast-fail immediately
- **Half-open:** limited probes to test recovery

Pair with metrics to observe open/close transitions.

## Practical Checklist

- No fixed `sleep` without condition checks
- Timeouts defined at operation and workflow level
- Retries bounded and jittered
- Permanent errors short-circuit retries
- Circuit breaker used for unstable dependencies
