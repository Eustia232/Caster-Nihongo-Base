import pytest
from datetime import datetime, timezone
from src.data.models import Word, SRSProgress


def test_word_model_validation():
    data = {
        "id": 1000,
        "kanji": "食べる",
        "kana": "たべる2",
        "meaning": "吃",
        "pos": "动词",
        "category": None,
    }
    word = Word(**data)
    assert word.id == 1000
    assert word.kanji == "食べる"


def test_srs_progress_model():
    data = {
        "stability": 0.5,
        "difficulty": 3.0,
        "due": datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc),
        "last_review": datetime(2026, 1, 27, 12, 0, 0, tzinfo=timezone.utc),
        "state": 0,
    }
    progress = SRSProgress(**data)
    assert progress.stability == 0.5
    assert progress.due.day == 28
