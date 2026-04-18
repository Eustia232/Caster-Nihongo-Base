from datetime import datetime, timezone, timedelta
from src.core.srs import FSRSEngine
from src.data.models import SRSProgress


def make_progress(
    stability=1.0,
    difficulty=1.0,
    due=None,
    last_review=None,
    state=0,
    consec=0,
    archived=False,
):
    if due is None:
        due = datetime.now(timezone.utc)
    return SRSProgress(
        stability=stability,
        difficulty=difficulty,
        due=due,
        last_review=last_review,
        state=state,
        consecutive_successes=consec,
        archived=archived,
    )


def test_auto_archive_after_six_consecutive():
    engine = FSRSEngine()
    progress = None
    now = datetime.now(timezone.utc)

    # Simulate 6 consecutive good reviews
    for i in range(6):
        progress = engine.review(progress, 3, review_time=now + timedelta(minutes=i))

    assert progress.archived is True
    assert progress.archived_reason == "auto:6_consecutive"
    assert progress.archived_at is not None


def test_consecutive_resets_on_failure():
    engine = FSRSEngine()
    progress = None
    now = datetime.now(timezone.utc)

    # Two goods
    progress = engine.review(progress, 3, review_time=now)
    progress = engine.review(progress, 3, review_time=now + timedelta(minutes=1))
    assert progress.consecutive_successes == 2

    # A failure resets
    progress = engine.review(progress, 1, review_time=now + timedelta(minutes=2))
    assert progress.consecutive_successes == 0
