import pytest
from datetime import datetime
from src.data.models import Word, SRSProgress


def test_word_model_validation():
    data = {
        "id": 1000,
        "kanji": "食べる",
        "kana": "たべる2",
        "meaning": "吃",
        "pos": "动词",
    }
    word = Word(**data)
    assert word.id == 1000
    assert word.kanji == "食べる"
    assert word.kana == "たべる2"
    assert word.meaning == "吃"
    assert word.pos == "动词"


def test_srs_progress_model():
    data = {
        "stability": 0.5,
        "difficulty": 3.0,
        "elapsed_days": 1,
        "scheduled_days": 2,
        "last_review": datetime(2026, 1, 27, 12, 0, 0),
        "state": 0,
    }
    progress = SRSProgress(**data)
    assert progress.stability == 0.5
    assert progress.state == 0
