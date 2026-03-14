from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import Role, require_roles
from app.db.models.backtest_run import BacktestRun
from app.db.session import get_db
from app.schemas.analytics import LlmAnalyticsSummary, LlmModelUsageItem
from app.services.analytics.llm_analytics import LlmAnalyticsService

router = APIRouter(prefix='/analytics', tags=['analytics'])


def _as_float(value: object) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


@router.get('/llm-summary', response_model=LlmAnalyticsSummary)
def llm_summary(
    days: int | None = Query(default=30, ge=1, le=3650),
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN, Role.TRADER_OPERATOR, Role.ANALYST, Role.VIEWER)),
) -> LlmAnalyticsSummary:
    service = LlmAnalyticsService()
    return LlmAnalyticsSummary.model_validate(service.summary(db=db, days=days))


@router.get('/llm-models', response_model=list[LlmModelUsageItem])
def llm_models_usage(
    days: int | None = Query(default=30, ge=1, le=3650),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN, Role.TRADER_OPERATOR, Role.ANALYST, Role.VIEWER)),
) -> list[LlmModelUsageItem]:
    service = LlmAnalyticsService()
    rows = service.models_usage(db=db, days=days, limit=limit)
    return [LlmModelUsageItem.model_validate(item) for item in rows]


@router.get('/backtests-summary')
def backtests_summary(
    db: Session = Depends(get_db),
    _=Depends(require_roles(Role.SUPER_ADMIN, Role.ADMIN, Role.TRADER_OPERATOR, Role.ANALYST, Role.VIEWER)),
) -> dict:
    count = 0
    return_sum = 0.0
    drawdown_sum = 0.0

    metrics_rows = db.query(BacktestRun.metrics).filter(BacktestRun.status == 'completed')
    for (metrics,) in metrics_rows:
        if not isinstance(metrics, dict):
            continue
        count += 1
        return_sum += _as_float(metrics.get('total_return_pct', 0.0))
        drawdown_sum += _as_float(metrics.get('max_drawdown_pct', 0.0))

    avg_return = (return_sum / count) if count else 0.0
    avg_drawdown = (drawdown_sum / count) if count else 0.0

    return {
        'total_backtests': count,
        'average_total_return_pct': round(float(avg_return or 0.0), 4),
        'average_max_drawdown_pct': round(float(avg_drawdown or 0.0), 4),
    }
