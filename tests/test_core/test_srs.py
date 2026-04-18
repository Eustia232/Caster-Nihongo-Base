import pytest
from datetime import datetime
from src.core.srs import FSRSEngine
from src.data.models import SRSProgress


def test_fsrs_engine_initial_review():
    engine = FSRSEngine()
    # 初始状态（尚未开始复习）
    new_card = None

    # 评分 3 (Good)
    new_progress = engine.review(
        new_card, 3, review_time=datetime(2026, 1, 27, 12, 0, 0)
    )

    assert new_progress.stability > 0
    # 根据 fsrs-python，初始状态 Good 后状态变为 1 (Learning)
    assert new_progress.state == 1
