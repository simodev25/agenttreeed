from datetime import datetime, timezone

from app.services.execution.executor import ExecutionService


def test_json_safe_serializes_datetime() -> None:
    payload = {'ts': datetime(2026, 3, 12, 22, 0, tzinfo=timezone.utc), 'value': 1}
    safe = ExecutionService._json_safe(payload)
    assert isinstance(safe['ts'], str)
    assert safe['value'] == 1
