# Defense in Depth

Layered safeguards to prevent bugs from becoming incidents.

## Validation Layers

Apply validation at multiple boundaries:
- **Input boundary:** request/schema/type validation
- **Domain boundary:** business invariants and authorization checks
- **Persistence boundary:** constraints, transactions, uniqueness rules
- **Output boundary:** contract validation and safe serialization

Each layer should assume previous layers can fail.

## Guard Clauses

Prefer early exits for invalid or unsafe states:
- Reject impossible inputs immediately
- Fail fast when dependencies are unavailable
- Keep precondition checks near function entry

Guard clauses reduce nested logic and make failure modes explicit.

## Fail-Safe Defaults

When uncertain, choose behavior that minimizes harm:
- Deny-by-default for permissions
- Conservative defaults for destructive operations
- Idempotent retries where possible
- Feature flags defaulting to off for risky rollouts

## Monitoring and Alerting

Prevention includes fast detection:
- Instrument key invariants and error rates
- Emit structured logs with correlation IDs
- Track saturation/latency/error metrics (SLI/SLO aligned)
- Alert on symptom thresholds and causal indicators

Use alerts that are actionable and tied to runbooks.

## Practical Rollout Checklist

- Add at least one preventive layer near input
- Add one containment layer near side effects
- Add one detection signal (metric/log/alert)
- Add one regression test for the original failure mode
