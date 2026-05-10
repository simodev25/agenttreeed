# Testing Anti-Patterns

Common testing pitfalls and how to avoid them.

## 1) Flaky Tests

Symptoms:
- Pass/fail outcomes change without code changes
- Timing, network, or ordering sensitivity

Avoid by:
- Controlling time and randomness
- Removing external network dependencies
- Using deterministic test data and stable selectors

## 2) Test Interdependence

Symptoms:
- Tests pass alone but fail in suite
- Order-dependent behavior

Avoid by:
- Isolating state per test
- Resetting global/shared fixtures
- Avoiding hidden coupling through singleton state

## 3) Testing Implementation Details

Symptoms:
- Tests break after harmless refactor
- Assertions tied to internals instead of behavior

Avoid by:
- Asserting observable outcomes (inputs/outputs/effects)
- Favoring public API and user-visible behavior

## 4) Excessive Mocking

Symptoms:
- Tests mostly verify mock expectations
- Real integration bugs escape tests

Avoid by:
- Mocking only expensive/unstable boundaries
- Keeping core logic under real execution
- Using contract/integration tests for critical seams

## 5) Assertion-Free Tests

Symptoms:
- Test executes code but validates nothing
- “No exception thrown” is the only signal

Avoid by:
- Requiring explicit assertions for behavior
- Verifying state changes, return values, or emitted events

## 6) Slow Tests

Symptoms:
- Feedback loop too long for TDD
- Developers skip local execution

Avoid by:
- Keeping unit tests fast and focused
- Tagging and separating heavy integration/e2e suites
- Parallelizing where safe

## Quick Review Checklist

- Deterministic and isolated?
- Behavior-focused assertions?
- Minimal, justified mocks?
- At least one explicit assertion?
- Fast enough for frequent local runs?
