"""
e2e 测试专用配置：确保测试库存在一个"当前学期"。

e2e 走完整 API 链路（真实路由+JWT），排课/工单/统计接口依赖 Semester.get_current()；
若测试库无当前学期，这些接口会返回 400「未设置当前学期」而非被测逻辑结果。
此 autouse fixture 在每个 e2e 测试前补齐当前学期（若不存在）。
"""

import pytest
from datetime import date


@pytest.fixture(autouse=True)
def _ensure_current_semester(db):
    from apps.schedules.models import Semester

    if not Semester.objects.filter(is_current=True, is_deleted=False).exists():
        Semester.objects.create(
            name='e2e测试当前学期',
            code='E2E_CURRENT',
            start_date=date(2025, 9, 1),
            end_date=date(2026, 1, 20),
            is_current=True,
            total_weeks=20,
        )
    yield
