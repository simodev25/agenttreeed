# Root Cause Tracing

Structured techniques to move from symptom to true root cause.

## 1) 5 Whys (Fast Causal Drill-Down)

Use when the failure path is short and understandable.

Process:
1. State the observed symptom clearly.
2. Ask “Why did this happen?” and answer with evidence.
3. Repeat up to five times (or until cause becomes actionable).
4. Validate the final cause by reproducing and proving the chain.

Rule: if an answer is speculative, pause and collect evidence first.

## 2) Fault Tree Analysis (Complex Systems)

Use when multiple causes could trigger the same failure.

Process:
1. Put the top failure at the root.
2. Branch into possible contributing events.
3. Mark each branch with AND/OR relationship.
4. Test branches to eliminate impossible paths.
5. Isolate the minimal failing combination.

Tip: start broad, then prune aggressively with logs, traces, and checks.

## 3) Causal Chain Mapping (Timeline-Based)

Use when sequence and timing matter (async, distributed, race conditions).

Process:
1. Build a timestamped event timeline.
2. Map data transformations across boundaries.
3. Highlight first point where expected state diverges.
4. Confirm the upstream trigger for that divergence.
5. Define the corrective action at the earliest reliable point.

## When to Stop Digging

Stop when all conditions are true:
- You can reproduce the issue deterministically (or bounded conditions).
- You identified the earliest actionable cause, not just a downstream symptom.
- One targeted fix explains and resolves the observed behavior.
- A test or verification step proves regression protection.

If further digging does not change the fix strategy, move to implementation.
