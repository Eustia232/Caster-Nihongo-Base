from datetime import datetime, timezone
from typing import Optional, List, Dict, Union, Any, Tuple
from fsrs import Scheduler, Card, Rating
from src.data.models import SRSProgress


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

            card = Card(
                stability=current_progress.stability,
                difficulty=current_progress.difficulty,
                due=due,
                last_review=last_review,
                state=current_progress.state,
            )

        fsrs_rating = Rating(rating)
        updated_card, _ = self.scheduler.review_card(card, fsrs_rating, review_time)

        return SRSProgress(
            stability=updated_card.stability,
            difficulty=updated_card.difficulty,
            due=updated_card.due,
            last_review=updated_card.last_review,
            state=updated_card.state,
        )
