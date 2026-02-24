from datetime import datetime, timezone
from typing import Optional, List, Dict, Union, Any, Tuple
from fsrs import Scheduler, Card, Rating, State
from src.data.models import SRSProgress
from datetime import timedelta


class FSRSEngine:
    """封装 FSRS 算法，提供简单的复习接口"""

    def __init__(self):
        self.scheduler = Scheduler()

    def review(
        self,
        current_progress: Optional[SRSProgress],
        rating: int,
        review_time: Optional[datetime] = None,
    ) -> SRSProgress:
        """
        处理单词复习
        :param current_progress: 当前 SRS 进度，如果是新词则为 None
        :param rating: 用户评分 (1: Again, 2: Hard, 3: Good, 4: Easy)
        :param review_time: 复习时间，默认为当前时间 (UTC)
        :return: 更新后的 SRSProgress
        """
        if review_time is None:
            review_time = datetime.now(timezone.utc)
        elif review_time.tzinfo is None:
            review_time = review_time.replace(tzinfo=timezone.utc)

        if current_progress is None:
            card = Card()
        else:
            last_review = current_progress.last_review
            if last_review and last_review.tzinfo is None:
                last_review = last_review.replace(tzinfo=timezone.utc)

            due = current_progress.due
            if due and due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)

            # fsrs.Card expects specific types (State enum for state,
            # floats for stability/difficulty). Ensure we coerce values to
            # match that API and include `step` if present on the progress
            # object. Also tolerate our SRSProgress `state` using 0 for "New"
            # (map it to Learning) and ensure cards in Relearning have a
            # non-None step (default to 0) to satisfy fsrs.scheduler assertions.
            raw_state = int(current_progress.state)
            if raw_state in (1, 2, 3):
                state_enum = State(raw_state)
            else:
                # treat unknown/0 (New) as Learning
                state_enum = State.Learning

            step_val = getattr(current_progress, "step", None)
            if state_enum == State.Relearning and step_val is None:
                step_val = 0

            card = Card(
                stability=float(current_progress.stability),
                difficulty=float(current_progress.difficulty),
                due=due,
                last_review=last_review,
                state=state_enum,
                step=step_val,
            )

        fsrs_rating = Rating(rating)
        updated_card, _ = self.scheduler.review_card(card, fsrs_rating, review_time)

        # Enforce a minimum next interval so that a reviewed card won't be
        # scheduled again too soon. Apply this rule to all reviews (both
        # correct and incorrect) and set the minimum to 17 hours.
        # This avoids immediate re-scheduling within a short window after any
        # review action.
        if updated_card.due is not None:
            min_due = review_time + timedelta(hours=17)
            if updated_card.due <= min_due:
                updated_card.due = min_due

        # Update consecutive success count and possibly archive
        prev_consec = 0
        prev_archived = False
        if current_progress is not None:
            prev_consec = getattr(current_progress, "consecutive_successes", 0)
            prev_archived = getattr(current_progress, "archived", False)

        if rating >= 3:
            consec = prev_consec + 1
        else:
            consec = 0

        archived = prev_archived
        archived_at = None
        archived_reason = None
        if not prev_archived and consec >= 6:
            archived = True
            archived_at = review_time
            archived_reason = "auto:6_consecutive"

        return SRSProgress(
            stability=updated_card.stability,
            difficulty=updated_card.difficulty,
            due=updated_card.due,
            last_review=updated_card.last_review,
            state=updated_card.state,
            consecutive_successes=consec,
            archived=archived,
            archived_at=archived_at,
            archived_reason=archived_reason,
        )
